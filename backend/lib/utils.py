import os
import praw
import time
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Get the database path
BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "amazon_dashboard.db"

def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_title TEXT,
            comment TEXT NOT NULL,
            subreddit TEXT,
            url TEXT,
            created_utc INTEGER,
            sentiment TEXT,
            author TEXT,
            score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DATABASE_PATH}")

def get_sale_events() -> List[Dict[str, Any]]:
    """Load sale events from JSON file"""
    events_file = Path(__file__).parent / "sale_events.json"
    try:
        with open(events_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading sale events: {e}")
        return []

def get_subreddits() -> List[str]:
    """Load subreddits from text file"""
    subreddits_file = Path(__file__).parent / "subreddits.txt"
    try:
        with open(subreddits_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error loading subreddits: {e}")
        return ["IndiaDeals", "AmazonIndia", "IndianGaming"]

class RedditScraper:
    def __init__(self):
        """Initialize Reddit API client"""
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID", ""),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
            user_agent=os.getenv("REDDIT_USER_AGENT", "AmazonDashboard/1.0")
        )
    
    def test_connection(self) -> bool:
        """Test if Reddit API connection is working"""
        try:
            subreddit = self.reddit.subreddit("test")
            next(subreddit.hot(limit=1))
            return True
        except Exception as e:
            print(f"Reddit API connection failed: {str(e)}")
            return False
    
    def scrape_posts_by_keywords(self, keywords: List[str], subreddits: List[str] = None, max_posts: int = 50) -> List[Dict[str, Any]]:
        """Scrape Reddit posts for specific keywords"""
        if not subreddits:
            subreddits = get_subreddits()
        
        all_comments = []
        
        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                for keyword in keywords:
                    try:
                        posts = subreddit.search(
                            keyword, 
                            sort='relevance', 
                            time_filter='year',
                            limit=max_posts // len(keywords)
                        )
                        
                        for post in posts:
                            post.comments.replace_more(limit=0)
                            
                            for comment in post.comments.list()[:10]:
                                if len(comment.body) > 10 and comment.body not in ['[deleted]', '[removed]']:
                                    comment_data = {
                                        "submission_title": post.title[:200],
                                        "comment": comment.body[:1000],
                                        "subreddit": subreddit_name,
                                        "url": f"https://reddit.com{post.permalink}",
                                        "created_utc": int(comment.created_utc),
                                        "sentiment": "",
                                        "author": str(comment.author) if comment.author else "[deleted]",
                                        "score": comment.score
                                    }
                                    all_comments.append(comment_data)
                        
                        time.sleep(1)  # Rate limiting
                        
                    except Exception as e:
                        print(f"Error searching {keyword} in r/{subreddit_name}: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"Error accessing subreddit r/{subreddit_name}: {str(e)}")
                continue
        
        return all_comments

def generate_keywords(query: str) -> List[str]:
    """Generate search keywords for Amazon sales"""
    base_keywords = ["amazon sale", "amazon deals", "amazon discount", "amazon offer"]
    
    if query:
        query_keywords = [
            f"amazon {query.lower()}",
            f"{query.lower()} sale",
            f"{query.lower()} deals"
        ]
        return list(set(base_keywords + query_keywords))
    
    return base_keywords

# Database operations
def get_comments(limit: int = 100, offset: int = 0, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
    """Get comments from database with optional keyword filtering"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Base query
    query = "SELECT * FROM comments"
    params = []
    
    # Add keyword filtering if provided
    if keywords:
        keyword_conditions = []
        for keyword in keywords:
            keyword_conditions.append("(comment LIKE ? OR submission_title LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        if keyword_conditions:
            query += " WHERE " + " OR ".join(keyword_conditions)
    
    query += " ORDER BY created_utc DESC"
    
    # Get total count
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]
    
    # Add pagination
    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    columns = [desc[0] for desc in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "rows": rows,
        "total": total,
        "limit": limit,
        "offset": offset
    }

def add_comments(comments: List[Dict[str, Any]]):
    """Add comments to database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    for comment in comments:
        cursor.execute("""
            INSERT INTO comments 
            (submission_title, comment, subreddit, url, created_utc, sentiment, author, score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            comment.get('submission_title', ''),
            comment.get('comment', ''),
            comment.get('subreddit', ''),
            comment.get('url', ''),
            comment.get('created_utc', 0),
            comment.get('sentiment', ''),
            comment.get('author', ''),
            comment.get('score', 0)
        ))
    
    conn.commit()
    conn.close()

def get_sentiment_summary() -> Dict[str, Any]:
    """Get sentiment analysis summary"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            sentiment,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM comments WHERE sentiment != ''), 2) as percentage
        FROM comments 
        WHERE sentiment != ''
        GROUP BY sentiment
        ORDER BY count DESC
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    return {
        "distribution": [
            {"sentiment": row[0], "count": row[1], "percentage": row[2]}
            for row in results
        ]
    }

# Export the utilities
__all__ = [
    'DATABASE_PATH', 'init_database', 'get_sale_events', 'get_subreddits',
    'RedditScraper', 'generate_keywords', 'get_comments', 'add_comments', 'get_sentiment_summary'
]