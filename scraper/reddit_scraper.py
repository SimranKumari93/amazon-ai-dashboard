import praw
import pandas as pd
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_SECRET"),
    user_agent=os.getenv("USER_AGENT")
)

# Load sale events
with open("data/raw/sale_events.json") as f:
    sales = json.load(f)

# Load subreddits
with open("scraper/subreddits.txt") as f:
    subreddits = [line.strip() for line in f if line.strip()]

# Loop through all sales
for sale in sales:
    name = sale["name"]
    slug = sale["slug"]
    start_date = datetime.strptime(sale["start_date"], "%Y-%m-%d").timestamp()
    end_date = datetime.strptime(sale["end_date"], "%Y-%m-%d").timestamp()

    product_file = f"data/raw/products_{slug}.csv"
    output_file = f"data/raw/{slug}_reddit_comments.csv"

    if not os.path.exists(product_file):
        print(f"⚠️ Skipping {name} – product file not found.")
        continue

    products_df = pd.read_csv(product_file)
    product_names = [p.lower() for p in products_df["product_name"].tolist()]
    results = []

    print(f"\n📦 Scraping comments for {name}...")

    for sub in subreddits:
        try:
            subreddit = reddit.subreddit(sub)
            subreddit.id  # force access
            print(f"🔍 Searching r/{sub} for {name}...")
        except Exception as e:
            print(f"⚠️ Skipping r/{sub} → {e}")
            continue

# 1. More flexible keyword list  (first two words of each product)
product_keywords = []
for p in product_names:
    product_keywords.extend(p.split()[:2])   # fire tv  -> ["fire", "tv"]

# 2. Broader search query + larger limit
for submission in subreddit.search("amazon OR deal OR sale", limit=50, time_filter="year"):

    # if start_date <= submission.created_utc <= end_date:
    print("🔗 Title:", submission.title)
    submission.comments.replace_more(limit=0)
    for c in submission.comments.list():
        print("💬", c.body[:120])  # print sample of each comment
        body = c.body.lower()
        if any(k in body for k in product_keywords):
                results.append({
                     "subreddit": sub,
                     "submission_title": submission.title,
                     "comment": c.body,
                     "created_utc": c.created_utc,
                     "url": submission.url
                })
    # Save if any results
    if results:
        os.makedirs("data/raw/", exist_ok=True)
        pd.DataFrame(results).to_csv(output_file, index=False)
        print(f"✅ {len(results)} comments saved to {output_file}")
    else:
        print(f"ℹ️ No comments found for {name}")


# import os, json, praw, pandas as pd
# from datetime import datetime
# from dotenv import load_dotenv

# load_dotenv()
# reddit = praw.Reddit(
#     client_id=os.getenv("REDDIT_CLIENT_ID"),
#     client_secret=os.getenv("REDDIT_SECRET"),
#     user_agent=os.getenv("USER_AGENT"))

# # Load sale events
# with open("data/raw/sale_events.json") as f:
#     sales = json.load(f)

# # Load subreddits
# with open("scraper/subreddits.txt") as f:
#     subreddits = [line.strip() for line in f if line.strip()]

# # Loop through all sales
# for selected_sale in sales:
#     slug = selected_sale["name"].lower().replace(" ", "_").replace("’", "").replace("'", "")
#     start_date = datetime.strptime(selected_sale["start_date"], "%Y-%m-%d").timestamp()
#     end_date = datetime.strptime(selected_sale["end_date"], "%Y-%m-%d").timestamp()

#     product_file = f"data/raw/products_{slug}.csv"
#     output_file = f"data/raw/{slug}_reddit_comments.csv"

#     if not os.path.exists(product_file):
#         print(f"⚠️ Skipping {selected_sale['name']} — product file not found.")
#         continue

#     products_df = pd.read_csv(product_file)
#     product_names = [p.lower() for p in products_df["product_name"].tolist()]
#     results = []

#     for sub in subreddits:
#         try:
#             subreddit = reddit.subreddit(sub)
#             subreddit.id
#             print(f"🔍 Searching r/{sub} for {selected_sale['name']}...")
#         except Exception as e:
#             print(f"⚠️ Skipping invalid subreddit: r/{sub} → {e}")
#             continue

#         for submission in subreddit.search("Amazon", limit=10):
#             if start_date <= submission.created_utc <= end_date:
#                 submission.comments.replace_more(limit=0)
#                 for comment in submission.comments:
#                     if hasattr(comment, "body"):
#                         body = comment.body.lower()
#                         for product in product_names:
#                             if product in body:
#                                 results.append({
#                                     "subreddit": sub,
#                                     "product": product,
#                                     "comment": comment.body,
#                                     "created_utc": comment.created_utc,
#                                     "submission_title": submission.title,
#                                     "url": submission.url
#                                 })

#     if results:
#         os.makedirs("data/raw/", exist_ok=True)
#         output_df = pd.DataFrame(results)
#         output_df.to_csv(output_file, index=False)
#         print(f"✅ {selected_sale['name']} — Scraped and saved to {output_file}")
#     else:
#         print(f"ℹ️ No comments found for {selected_sale['name']}")

# for submission in reddit.subreddit("amazon").hot(limit=5):
#     print("🔗", submission.title)

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
