import os, json, uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key="GEMINI_API_KEY",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
# openai.api_key = os.getenv("OPENAI_API_KEY")

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app = FastAPI(title="Amazon Sale AI Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_RAW = "data/raw"
DATA_PROCESSED = "data/processed"

class InsightRequest(BaseModel):
    slug: str
    max_comments: int = 200

def load_events():
    path = os.path.join(DATA_RAW, "sale_events.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def slug_to_files(slug: str):
    raw_csv = os.path.join(DATA_RAW, f"{slug}_reddit_comments.csv")
    proc_csv = os.path.join(DATA_PROCESSED, f"{slug}_sentiment.csv")
    return raw_csv, proc_csv

# backend/main.py  # new code written to fix bugs
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Amazon Sale AI Dashboard Backend Running!"}

@app.get("/events")
def list_events():
    events = load_events()
    # if no slug in file, synthesize one
    for e in events:
        if "slug" not in e:
            e["slug"] = "".join(c if c.isalnum() else "_" for c in e["name"].lower())
    return events

@app.get("/comments")
def get_comments(slug: str, limit: int = 200, offset: int = 0):
    raw_csv, proc_csv = slug_to_files(slug)
    csv_path = proc_csv if os.path.exists(proc_csv) else raw_csv
    if not os.path.exists(csv_path):
        raise HTTPException(404, detail=f"No data for slug '{slug}'")

    df = pd.read_csv(csv_path)
    # normalize expected columns
    cols = [c.lower() for c in df.columns]
    df.columns = cols
    keep = [c for c in ["submission_title","comment","created_utc","subreddit","sentiment","url"] if c in df.columns]
    if not keep:
        keep = df.columns.tolist()

    sliced = df[keep].fillna("").iloc[offset:offset+limit]
    return {"total": len(df), "rows": sliced.to_dict(orient="records")}

@app.get("/sentiment")
def sentiment_summary(slug: str):
    _, proc_csv = slug_to_files(slug)
    if not os.path.exists(proc_csv):
        raise HTTPException(404, detail=f"Processed sentiment file not found for '{slug}'")
    df = pd.read_csv(proc_csv)
    if "sentiment" not in df.columns:
        raise HTTPException(400, detail="sentiment column missing in processed file")

    total = len(df)
    dist = df["sentiment"].str.strip().str.title().value_counts().to_dict()
    top_titles = df["submission_title"].value_counts().head(10).to_dict() if "submission_title" in df.columns else {}
    return {"total": total, "distribution": dist, "top_posts": top_titles}

@app.post("/insights")
def generate_insights(req: InsightRequest):
    raw_csv, proc_csv = slug_to_files(req.slug)
    csv_path = proc_csv if os.path.exists(proc_csv) else raw_csv
    if not os.path.exists(csv_path):
        raise HTTPException(404, detail=f"No data for slug '{req.slug}'")

    df = pd.read_csv(csv_path).fillna("")
    if "comment" not in df.columns:
        # try lower-case fallback
        if "comment" not in [c.lower() for c in df.columns]:
            raise HTTPException(400, detail="No 'comment' column found")
        df.columns = [c.lower() for c in df.columns]

    # sample up to max_comments
    sample = df.sample(min(req.max_comments, len(df)), random_state=42)
    title_hint = sample["submission_title"].iloc[0] if "submission_title" in sample.columns and len(sample) else ""

    joined = "\n".join(f"- {r['comment']}" for _, r in sample.iterrows())

    prompt = f"""
You are an analyst for Amazon sales events. Based ONLY on these Reddit comments, provide:
1) Sentiment distribution (Positive/Negative/Neutral) with brief justification
2) Top 5 pain points and actionable recommendations
3) Top 5 delights and what to double down on
4) Watch-outs for next sale (risks)
Keep it concise and bullet-based. Comments:\n{joined}
"""

    try:
        # OpenAI chat completion
        resp = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[{"role":"user","content": prompt}],
            # temperature=0.2
        )
        
        text = resp.choices[0].message  #resp.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(500, detail=f"OpenAI error: {e}")

    return {"slug": req.slug, "summary": text}

if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8000)
