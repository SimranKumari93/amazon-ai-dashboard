import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI

from lib.utils import (
    init_database, get_sale_events, get_subreddits, RedditScraper,
    generate_keywords, get_comments, add_comments, get_sentiment_summary
)

load_dotenv()

# Initialize OpenAI client for Gemini (optional for insights)
client = None
if os.getenv("GEMINI_API_KEY"):
    client = OpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

# Pydantic models
class ScrapeRequest(BaseModel):
    keywords: Optional[List[str]] = None
    max_posts: Optional[int] = 50
    subreddits: Optional[List[str]] = None

class InsightRequest(BaseModel):
    max_comments: Optional[int] = 100

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_database()
    yield
    # Shutdown (if needed)

# Initialize FastAPI app
app = FastAPI(
    title="Amazon Sale AI Dashboard",
    description="Simple API for Amazon sale sentiment analysis",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints

@app.get("/")
def root():
    """Health check endpoint"""
    return {"message": "Amazon Sale AI Dashboard API v2.0 is running!"}

@app.get("/sale-events")
def list_sale_events():
    """Get all predefined sale events"""
    try:
        events = get_sale_events()
        return {"success": True, "data": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")

@app.get("/subreddits")
def list_subreddits():
    """Get all configured subreddits"""
    try:
        subreddits = get_subreddits()
        return {"success": True, "data": subreddits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching subreddits: {str(e)}")

@app.get("/comments")
def get_all_comments(limit: int = 100, offset: int = 0, keywords: Optional[str] = None):
    """Get comments from database with optional keyword filtering"""
    try:
        keyword_list = None
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        
        comments_data = get_comments(limit, offset, keyword_list)
        return {"success": True, "data": comments_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching comments: {str(e)}")

@app.get("/sentiment")
def get_sentiment():
    """Get sentiment analysis summary"""
    try:
        sentiment_data = get_sentiment_summary()
        return {"success": True, "data": sentiment_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sentiment: {str(e)}")

@app.post("/scrape")
def scrape_reddit_data(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Scrape Reddit data based on keywords"""
    try:
        # Use provided keywords or generate from query
        keywords = request.keywords
        if not keywords:
            keywords = generate_keywords("prime day")  # Default keywords
        
        # Add scraping task to background
        background_tasks.add_task(
            scrape_reddit_task, 
            keywords,
            request.subreddits or get_subreddits(),
            request.max_posts
        )
        
        return {"success": True, "message": "Scraping started in background", "keywords": keywords}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting scrape: {str(e)}")

@app.get("/scrape/status")
def get_scrape_status():
    """Get current database status"""
    try:
        comments_data = get_comments(1, 0)
        return {
            "success": True, 
            "data": {
                "total_comments": comments_data["total"],
                "last_updated": "recent" if comments_data["total"] > 0 else "never"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@app.post("/insights")
def generate_insights(request: InsightRequest):
    """Generate AI insights from comments"""
    try:
        # Get comments for analysis
        comments_data = get_comments(request.max_comments, 0)
        if comments_data["total"] == 0:
            raise HTTPException(status_code=400, detail="No comments available for analysis")
        
        # Prepare comments for AI analysis
        comments_text = "\n".join([
            f"- {comment['comment']}" 
            for comment in comments_data["rows"] 
            if comment["comment"]
        ][:50])  # Limit to first 50 comments
        
        if not comments_text.strip():
            raise HTTPException(status_code=400, detail="No valid comments found for analysis")
        
        if not client:
            return {
                "success": True, 
                "data": {
                    "insights": "AI insights unavailable. Please configure GEMINI_API_KEY in environment variables."
                }
            }
        
        # Create prompt for Gemini
        prompt = f"""
Analyze these Amazon sale-related Reddit comments and provide:

1) **Sentiment Distribution**: Overall sentiment (Positive/Negative/Neutral) with percentages
2) **Top 5 Pain Points**: Main customer complaints with actionable recommendations
3) **Top 5 Delights**: What customers loved most
4) **Key Recommendations**: Top 3 improvements for Amazon sales

Keep the response concise and actionable.

Comments:
{comments_text}
"""
        
        try:
            response = client.chat.completions.create(
                model="gemini-2.0-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            insights = response.choices[0].message.content.strip()
        except Exception:
            insights = "Failed to generate AI insights. Please check API configuration."
        
        return {"success": True, "data": {"insights": insights}}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

# Helper functions

def scrape_reddit_task(keywords: List[str], subreddits: List[str], max_posts: int):
    """Background task to scrape Reddit data"""
    try:
        print(f"Starting scrape task - Keywords: {keywords}, Subreddits: {len(subreddits)}, Max posts: {max_posts}")
        scraper = RedditScraper()
        
        if scraper.test_connection():
            print(f"✓ Reddit API connected. Scraping for keywords: {keywords}")
            comments = scraper.scrape_posts_by_keywords(keywords, subreddits, max_posts)
            print(f"✓ Scraping completed. Found {len(comments)} comments")
        else:
            print("✗ Reddit API not available, cannot scrape data")
            return
        
        if comments:
            add_comments(comments)
            print(f"✓ Added {len(comments)} comments to database successfully")
            
            # Verify data was saved
            from lib.utils import get_comments
            total_in_db = get_comments(1, 0)["total"]
            print(f"✓ Database now contains {total_in_db} total comments")
        else:
            print("⚠ No comments found for the given keywords")
            
    except Exception as e:
        print(f"✗ Error in scraping task: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)