import praw
import ssl
import concurrent.futures
import logging
import requests
import re
import os
from dotenv import load_dotenv
from openai import OpenAI   # ← OpenAI client

load_dotenv()  # load all API keys / secrets from .env

# ──────────────────────────────────────────────
# 1.  CONFIG
# ──────────────────────────────────────────────
banned           = []
output_dir       = "amazon_prime_day"
AMAZON_KEYWORDS  = ["prime day", "amazon sale", "lightning deal",
                    "great indian festival", "black friday amazon",
                    "cyber monday amazon"]
POST_LIMIT       = 200
CHAR_LIMIT       = 20000
MAX_WORKERS      = 20

os.makedirs(output_dir, exist_ok=True)
logging.basicConfig(filename='reddit_amazon.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ──────────────────────────────────────────────
# 2.  REDDIT AUTH (env-based)
# ──────────────────────────────────────────────
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_SECRET"),
    user_agent="AmazonSaleScraper",
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD")
)

# ──────────────────────────────────────────────
# 3.  LLM AUTH + CALL (env-based)
# ──────────────────────────────────────────────
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_api(text: str, heading: str) -> str:
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",   # or any model you want
            messages=[
                {"role": "system", "content": "You are an AI that analyzes Reddit threads about Amazon sales."},
                {"role": "user", "content": build_prompt_amazon(heading, text)}
            ],
            temperature=0.4,
            max_tokens=1200
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"LLM API call failed: {e}")
        return f"(error calling LLM: {e})"

# ──────────────────────────────────────────────
# 4.  PROMPT (unchanged)
# ──────────────────────────────────────────────
def build_prompt_amazon(post_title: str, comments_text: str) -> str:
    return f"""
You are given Reddit threads about **Amazon Prime Day or other Amazon sales**.

Post Title: **{post_title}**
Comments:
{comments_text}

If the content is clearly unrelated to Amazon sales, reply only:
***Not Sure If the post is related to Amazon Sale***

Otherwise analyse strictly from the comments and produce:

1) **Overall Sentiment** toward Amazon Sale (positive/negative/neutral + confidence %)
2) **Key Themes**  
   a. Pricing / Deals  
   b. Delivery / Shipping  
   c. Stock Availability  
   d. Customer Service  
   e. Other Themes  
   For each theme, split summary into Positive / Negative with verbatim examples [username].
3) **Comparisons** to other retailers (Walmart, Best Buy, Target, etc.).
4) **5-8 sentence Summary** of key insights.
5) **Total Comments Considered** (Amazon-related only).
"""

# ──────────────────────────────────────────────
# 5.  COMMENT TREE HELPERS
# ──────────────────────────────────────────────
def build_threaded_comment_view(comment, indent=0, max_indent=100):
    if comment.body in ["[deleted]", "[removed]"]:
        return ""
    prefix = "  " * indent + "↳ " if indent else ""
    author = comment.author.name if comment.author else "Unknown"
    line   = f"{prefix}{author}: {comment.body.strip()}\n"
    if indent < max_indent:
        for reply in comment.replies:
            line += build_threaded_comment_view(reply, indent + 1, max_indent)
    return line

def safe_filename(title: str) -> str:
    # Replace invalid filename characters with "_"
    return re.sub(r'[\\/*?:"<>|]', "_", title)[:100]  # also limit length

# def sanitize_filename(title: str) -> str:
#     return re.sub(r'[\\/*?:"<>|]', '_', title)[:100].strip()

# ──────────────────────────────────────────────
# 6.  MAIN SCRAPER
# ──────────────────────────────────────────────
def extract_amazon_sale_threads(keywords, post_limit, char_limit=CHAR_LIMIT):
    for kw in keywords:
        posts = reddit.subreddit("all").search(kw, sort="relevance",
                                               limit=post_limit, time_filter="month")
        for post in posts:
            out_file = safe_filename(post.title) + ".txt"

            # out_file = f"{post.id}_{safe_filename(post.title)}.txt"
            if out_file in os.listdir(output_dir):
                continue

            post.comments.replace_more(limit=None)
            blocks, idx, buf = [], 1, ""
            for top in post.comments:
                thread = build_threaded_comment_view(top)
                if not thread.strip():
                    continue
                if len(buf) + len(thread) >= char_limit:
                    blocks.append((idx, buf))
                    idx += 1
                    buf  = ""
                buf += "\n" + thread
            if buf.strip():
                blocks.append((idx, buf))

            summaries = []
            with concurrent.futures.ThreadPoolExecutor(MAX_WORKERS) as exe:
                fut = {exe.submit(call_api, block, post.title): i for i, block in blocks}
                for future in concurrent.futures.as_completed(fut):
                    summaries.append((fut[future], future.result()))
            summaries.sort()
            refined = "\n".join([f"🔍 Refined Summary #{i}:\n{s}" for i, s in summaries])

                # out_file = safe_filename(post.title) + ".txt"
                # with open(os.path.join(output_dir, out_file), "w", encoding="utf-8") as f:
                # f.write(post.selftext)

            with open(os.path.join(output_dir, out_file), "w", encoding="utf-8") as f:
                f.write(post.title + "\n\n")
                f.write(post.shortlink + "\n\n")
                f.write(refined)

            print(f"✅ Saved summary → {out_file}")

if __name__ == "__main__":
    extract_amazon_sale_threads(AMAZON_KEYWORDS, POST_LIMIT)



# import praw, pandas as pd, json
# from datetime import datetime
# from dotenv import load_dotenv
# import os

# # Load environment variables
# load_dotenv()

# # Initialize Reddit API
# reddit = praw.Reddit(
#     client_id=os.getenv("REDDIT_CLIENT_ID"),
#     client_secret=os.getenv("REDDIT_SECRET"),
#     user_agent=os.getenv("USER_AGENT")
# )

# # Load sale events
# with open("data/raw/sale_events.json") as f:
#     sales = json.load(f)

# # Load subreddits
# with open("scraper/subreddits.txt") as f:
#     subreddits = [line.strip() for line in f if line.strip()]

# Loop through all sales
# for sale in sales:
#     name = sale["name"]
#     slug = sale["slug"]
#     start_date = datetime.strptime(sale["start_date"], "%Y-%m-%d").timestamp()
#     end_date = datetime.strptime(sale["end_date"], "%Y-%m-%d").timestamp()

#     product_file = f"data/raw/products_{slug}.csv"
#     output_file = f"data/raw/{slug}_reddit_comments.csv"

#     if not os.path.exists(product_file):
#         print(f"⚠️ Skipping {name} – product file not found.")
#         continue

#     products_df = pd.read_csv(product_file)
#     product_names = [p.lower() for p in products_df["product_name"].tolist()]
#     results = []

#     print(f"\n📦 Scraping comments for {name}...")

#     for sub in subreddits:
#         try:
#             subreddit = reddit.subreddit(sub)
#             subreddit.id  # force access
#             print(f"🔍 Searching r/{sub} for {name}...")
#         except Exception as e:
#             print(f"⚠️ Skipping r/{sub} → {e}")
#             continue

# # 1. More flexible keyword list  (first two words of each product)
# product_keywords = []
# for p in product_names:
#     product_keywords.extend(p.split()[:2])   # fire tv  -> ["fire", "tv"]

# # 2. Broader search query + larger limit
# for submission in subreddit.search("amazon OR deal OR sale", limit=50, time_filter="year"):

# #  if start_date <= submission.created_utc <= end_date:
#     print("🔗 Title:", submission.title)
#     submission.comments.replace_more(limit=0)
#     for c in submission.comments.list():
#         print("💬", c.body[:120])  # print sample of each comment
#         body = c.body.lower()
#         for product in product_names:
#           if product in c.body.lower():
#         # save it
#         # if any(k in body for k in product_keywords):
#                 results.append({
#                      "subreddit": sub,
#                      "submission_title": submission.title,
#                      "comment": c.body,
#                      "created_utc": c.created_utc,
#                      "url": submission.url
#                 })
#     # Save if any results
#     if results:
#         os.makedirs("data/raw/", exist_ok=True)
#         pd.DataFrame(results).to_csv(output_file, index=False)
#         print(f"✅ {len(results)} comments saved to {output_file}")
#     else:
#         print(f"ℹ️ No comments found for {name}")

# pd.DataFrame(results).to_csv(f"data/raw/{slug}_reddit_comments.csv", index=False)


  # Previous Code 

# import praw  # praw is a reddit api scraper using python 
# import pandas as pd
# import json
# from datetime import datetime
# from dotenv import load_dotenv
# import os
# import csv 

# load_dotenv() # load environment variables 

# # Initialize Reddit API
# reddit = praw.Reddit(
#     client_id=os.getenv("REDDIT_CLIENT_ID"),
#     client_secret=os.getenv("REDDIT_SECRET"),
#     user_agent=os.getenv("USER_AGENT")
# )

# # Load sale events
# with open("data/sale_events.json") as f:
#     sales = json.load(f)

# # Choose the sale you want to scrape
# selected_sale = next(s for s in sales if s["name"] == "Fab TV Sale")
# start_date = datetime.strptime(selected_sale["start_date"], "%Y-%m-%d").timestamp()
# end_date = datetime.strptime(selected_sale["end_date"], "%Y-%m-%d").timestamp()

# # Load product names
# products_df = pd.read_csv("data/products_fab_tv_sale.csv")
# product_names = [p.lower() for p in products_df["product_name"].tolist()]

# # Load subreddits
# with open("scraper/subreddits.txt") as f:
#     subreddits = [line.strip() for line in f if line.strip()]

# # Result storage
# results = []

# # Scrape posts/comments
# # for sub in subreddits:
# #     subreddit = reddit.subreddit(sub)
# #     print(f"Searching r/{sub}...")

# for sub in subreddits:
#     try:
#         subreddit = reddit.subreddit(sub)
#         subreddit.id  # Forces PRAW to fetch subreddit, raises error if invalid
#         print(f"🔍 Searching r/{sub}...")
#     except Exception as e:
#         print(f"⚠️ Skipping invalid subreddit: r/{sub} → {e}")
#         continue

#     for submission in subreddit.search("Amazon", limit=10):
#         # print("🔗 Found post:", submission.title)
#         if start_date <= submission.created_utc <= end_date:
#             submission.comments.replace_more(limit=0)
#             for comment in submission.comments.list():
#                 # print("🗨️", comment.body[:100])
#                 if hasattr(comment, "body"):
#                     body = comment.body.lower()
#                     for product in product_names:
#                         print("📦 Products to match:", product_names[:5])# print the 1st 5 values of the product name 
#                         if product.split()[0] in body:
#                             print(f"📌 MATCHED → Product: {product} | Comment: {comment.body[:100]}")
#                             results.append({
#                                 "subreddit": sub,
#                                 "product": product,
#                                 "comment": comment.body,
#                                 "created_utc": comment.created_utc,
#                                 "submission_title": submission.title,
#                                 "url": submission.url
#                             })

# # to make sure the data/raw/ folder exists befor adding 
# os.makedirs("data/raw/", exist_ok=True)

# # Save to CSV
# # with open("data/raw/fab_tv_sale_reddit_comments.csv", "w", newline="", encoding="utf-8") as f:
# #     writer = csv.writer(f)
# #     writer.writerow(["comment", "score", "timestamp"]) # columns / headers 
# print(f"🧮 Total matches found: {len(results)}")

# if not results:
#     print("❌ No matching comments found. CSV not written.")
#     exit()
    
# if results:
#     output_df = pd.DataFrame(results)
#     output_df.to_csv("data/raw/fab_tv_sale_reddit_comments.csv", index=False)
#     print(f"✅ Scraping done. Data saved to fab_tv_sale_reddit_comments.csv")
# else:
#     print("❌ No matching comments found for products.")
