import os
import praw
import time
import sqlite3
import json
import logging
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the database path
BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "amazon_dashboard.db"

# Initialize OpenAI client for sentiment analysis
sentiment_client = None
if os.getenv("GEMINI_API_KEY"):
    sentiment_client = OpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    logger.info("Sentiment analysis client initialized")
else:
    logger.warning("GEMINI_API_KEY not found - sentiment analysis will be disabled")

def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create sale_events table with processing status
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            start_date TEXT,
            end_date TEXT,
            is_processed BOOLEAN DEFAULT FALSE,
            comments_count INTEGER DEFAULT 0,
            sentiment_analyzed BOOLEAN DEFAULT FALSE,
            insights_generated BOOLEAN DEFAULT FALSE,
            last_processed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create comments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_slug TEXT NOT NULL,
            submission_title TEXT,
            comment TEXT NOT NULL,
            subreddit TEXT,
            url TEXT,
            created_utc INTEGER,
            sentiment TEXT CHECK(sentiment IN ('', 'positive', 'negative', 'neutral')),
            sentiment_score REAL DEFAULT 0.0,
            author TEXT,
            score INTEGER DEFAULT 0,
            comment_hash TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_slug) REFERENCES sale_events (slug)
        )
    """)
    
    # Create insights table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_slug TEXT NOT NULL,
            content TEXT NOT NULL,
            insight_type TEXT DEFAULT 'general',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_slug) REFERENCES sale_events (slug)
        )
    """)
    
    # Create indexes for performance
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_comments_event_slug ON comments (event_slug)",
        "CREATE INDEX IF NOT EXISTS idx_comments_sentiment ON comments (sentiment)",
        "CREATE INDEX IF NOT EXISTS idx_comments_created_utc ON comments (created_utc)",
        "CREATE INDEX IF NOT EXISTS idx_comments_hash ON comments (comment_hash)",
        "CREATE INDEX IF NOT EXISTS idx_sale_events_slug ON sale_events (slug)",
        "CREATE INDEX IF NOT EXISTS idx_insights_event_slug ON insights (event_slug)"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    # Insert or update sale events
    cursor.execute("DELETE FROM sale_events")  # Clean slate
    events = get_sale_events()
    for event in events:
        cursor.execute("""
            INSERT INTO sale_events (slug, name, description, start_date, end_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            event['slug'],
            event['name'],
            event.get('description', ''),
            event.get('start_date', ''),
            event.get('end_date', '')
        ))
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at: {DATABASE_PATH} with {len(events)} events")

def get_sale_events() -> List[Dict[str, Any]]:
    """Load sale events from JSON file"""
    events_file = Path(__file__).parent / "sale_events.json"
    try:
        with open(events_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading sale events: {e}")
        return []

def get_subreddits() -> List[str]:
    """Load subreddits from text file"""
    subreddits_file = Path(__file__).parent / "subreddits.txt"
    try:
        with open(subreddits_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Error loading subreddits: {e}")
        return ["IndiaDeals", "AmazonIndia", "IndianGaming"]

def get_event_status(event_slug: str = None) -> Dict[str, Any]:
    """Get processing status for an event"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    if event_slug:
        cursor.execute("""
            SELECT slug, name, description, is_processed, comments_count, 
                   sentiment_analyzed, insights_generated, last_processed_at
            FROM sale_events WHERE slug = ?
        """, (event_slug,))
        result = cursor.fetchone()
        
        if result:
            return {
                "slug": result[0],
                "name": result[1], 
                "description": result[2],
                "is_processed": bool(result[3]),
                "comments_count": result[4],
                "sentiment_analyzed": bool(result[5]),
                "insights_generated": bool(result[6]),
                "last_processed_at": result[7]
            }
    else:
        cursor.execute("""
            SELECT slug, name, description, is_processed, comments_count,
                   sentiment_analyzed, insights_generated, last_processed_at
            FROM sale_events ORDER BY created_at DESC
        """)
        results = cursor.fetchall()
        
        events = []
        for result in results:
            events.append({
                "slug": result[0],
                "name": result[1],
                "description": result[2],
                "is_processed": bool(result[3]),
                "comments_count": result[4],
                "sentiment_analyzed": bool(result[5]),
                "insights_generated": bool(result[6]),
                "last_processed_at": result[7]
            })
        
        conn.close()
        return {"events": events}
    
    conn.close()
    return {}

def clean_text(text: str) -> str:
    """Clean and normalize text for processing"""
    if not text or len(text.strip()) < 3:
        return ""
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove Reddit formatting
    text = re.sub(r'/u/[\\w-]+', '', text)
    text = re.sub(r'/r/[\\w-]+', '', text)
    text = re.sub(r'\\[deleted\\]|\\[removed\\]', '', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\\s+', ' ', text)
    text = text.strip()
    
    # Remove very short content
    if len(text) < 10 or text.lower() in ['deleted', 'removed', 'edit', 'update']:
        return ""
    
    return text

def generate_comment_hash(comment: str, author: str, subreddit: str) -> str:
    """Generate unique hash for comment deduplication"""
    unique_string = f"{comment[:100]}{author}{subreddit}"
    return hashlib.md5(unique_string.encode()).hexdigest()

class RedditScraper:
    def __init__(self):
        """Initialize Reddit API client"""
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID", ""),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
            user_agent=os.getenv("REDDIT_USER_AGENT", "AmazonDashboard/2.0")
        )
    
    def test_connection(self) -> bool:
        """Test if Reddit API connection is working"""
        try:
            subreddit = self.reddit.subreddit("test")
            next(subreddit.hot(limit=1))
            return True
        except Exception as e:
            logger.error(f"Reddit API connection failed: {str(e)}")
            return False
    
    def scrape_event_data(self, event_slug: str, keywords: List[str] = None, max_posts: int = 50) -> List[Dict[str, Any]]:
        """Scrape Reddit data for a specific event"""
        if not keywords:
            keywords = ["amazon sale", "amazon deals", "amazon discount", "amazon offer"]
        
        subreddits = get_subreddits()
        all_comments = []
        
        logger.info(f"Starting scrape for event '{event_slug}' with keywords: {keywords}")
        
        for subreddit_name in subreddits[:10]:  # Limit to top 10 subreddits
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                for keyword in keywords[:3]:  # Limit to top 3 keywords
                    try:
                        posts = subreddit.search(
                            keyword, 
                            sort='relevance', 
                            time_filter='year',
                            limit=max_posts // (len(keywords) * len(subreddits[:10]))
                        )
                        
                        for post in posts:
                            post.comments.replace_more(limit=0)
                            
                            # Get top comments
                            for comment in post.comments.list()[:10]:
                                if len(comment.body) > 20 and comment.body not in ['[deleted]', '[removed]']:
                                    clean_comment = clean_text(comment.body)
                                    clean_title = clean_text(post.title)
                                    
                                    if not clean_comment:
                                        continue
                                    
                                    author_name = str(comment.author) if comment.author else "[deleted]"
                                    comment_hash = generate_comment_hash(clean_comment, author_name, subreddit_name)
                                    
                                    comment_data = {
                                        "submission_title": clean_title[:200],
                                        "comment": clean_comment[:1000],
                                        "subreddit": subreddit_name,
                                        "url": f"https://reddit.com{post.permalink}",
                                        "created_utc": int(comment.created_utc),
                                        "author": author_name,
                                        "score": comment.score,
                                        "comment_hash": comment_hash
                                    }
                                    all_comments.append(comment_data)
                        
                        time.sleep(1)  # Rate limiting
                        
                    except Exception as e:
                        logger.error(f"Error searching {keyword} in r/{subreddit_name}: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error accessing subreddit r/{subreddit_name}: {str(e)}")
                continue
        
        logger.info(f"Scraped {len(all_comments)} comments for event '{event_slug}'")
        return all_comments

def analyze_sentiment_batch(comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze sentiment for a batch of comments with rate limiting"""
    if not sentiment_client:
        logger.warning("Sentiment analysis not available")
        return comments
    
    logger.info(f"Analyzing sentiment for {len(comments)} comments")
    
    for i, comment in enumerate(comments):
        try:
            text = comment.get('comment', '')
            if not text:
                comment['sentiment'] = 'neutral'
                comment['sentiment_score'] = 0.0
                continue
                
            prompt = f"""Analyze the sentiment of this text about Amazon sales/products. 
Respond with only one word: 'positive', 'negative', or 'neutral'

Text: {text[:300]}"""
            
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    response = sentiment_client.chat.completions.create(
                        model="gemini-2.0-flash",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1,
                        max_tokens=10
                    )
                    
                    sentiment = response.choices[0].message.content.strip().lower()
                    
                    if sentiment not in ['positive', 'negative', 'neutral']:
                        sentiment = 'neutral'
                    
                    score_map = {'positive': 0.8, 'neutral': 0.0, 'negative': -0.8}
                    
                    comment['sentiment'] = sentiment
                    comment['sentiment_score'] = score_map.get(sentiment, 0.0)
                    
                    logger.info(f"Analyzed comment {i+1}/{len(comments)}: {sentiment}")
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        logger.warning(f"Rate limit hit for comment {i+1}, attempt {attempt + 1}/{max_retries}. Waiting {retry_delay * (attempt + 1)} seconds...")
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    else:
                        logger.error(f"Error analyzing sentiment for comment {i+1}: {e}")
                        comment['sentiment'] = 'neutral'
                        comment['sentiment_score'] = 0.0
                        break
            else:
                # All retries exhausted
                logger.error(f"All retries exhausted for comment {i+1}. Using neutral sentiment.")
                comment['sentiment'] = 'neutral'
                comment['sentiment_score'] = 0.0
            
            # Rate limiting delay between comments (increased for better stability)
            time.sleep(1.0)
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment for comment {i+1}: {e}")
            comment['sentiment'] = 'neutral'
            comment['sentiment_score'] = 0.0
    
    return comments

def generate_insights(event_slug: str) -> str:
    """Generate AI insights for an event"""
    if not sentiment_client:
        return "AI insights unavailable. Please configure GEMINI_API_KEY."
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get comments for the event
    cursor.execute("""
        SELECT comment, sentiment, sentiment_score 
        FROM comments 
        WHERE event_slug = ? 
        ORDER BY score DESC 
        LIMIT 50
    """, (event_slug,))
    
    comments = cursor.fetchall()
    conn.close()
    
    if not comments:
        return "No comments available for analysis."
    
    # Prepare comments text
    comments_text = "\n".join([f"- {comment[0][:200]}..." for comment in comments])
    
    # Get sentiment distribution
    sentiment_counts = {}
    for comment in comments:
        sentiment = comment[1] or 'neutral'
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
    
    prompt = f"""Analyze these Amazon sale-related Reddit comments and provide insights:

Sentiment Distribution: {sentiment_counts}

Comments:
{comments_text}

Please provide:
1) **Overall Sentiment Summary**: Brief overview of customer sentiment
2) **Top 3 Pain Points**: Main customer complaints with recommendations
3) **Top 3 Positive Aspects**: What customers appreciated most
4) **Key Recommendations**: Top 3 actionable improvements for Amazon

Keep response concise and actionable."""
    
    try:
        response = sentiment_client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return "Failed to generate AI insights. Please try again later."

def save_comments(comments: List[Dict[str, Any]], event_slug: str) -> int:
    """Save comments to database with deduplication"""
    if not comments:
        return 0
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    added_count = 0
    for comment in comments:
        try:
            cursor.execute("""
                INSERT INTO comments 
                (event_slug, submission_title, comment, subreddit, url, created_utc, 
                 sentiment, sentiment_score, author, score, comment_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_slug,
                comment.get('submission_title', ''),
                comment.get('comment', ''),
                comment.get('subreddit', ''),
                comment.get('url', ''),
                comment.get('created_utc', 0),
                comment.get('sentiment', ''),
                comment.get('sentiment_score', 0.0),
                comment.get('author', ''),
                comment.get('score', 0),
                comment.get('comment_hash', '')
            ))
            added_count += 1
        except sqlite3.IntegrityError:
            # Duplicate comment, skip
            continue
    
    conn.commit()
    conn.close()
    
    logger.info(f"Saved {added_count} new comments for event '{event_slug}'")
    return added_count

def save_insights(event_slug: str, insights_content: str) -> None:
    """Save AI insights to database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Remove existing insights for this event
    cursor.execute("DELETE FROM insights WHERE event_slug = ?", (event_slug,))
    
    # Add new insights
    cursor.execute("""
        INSERT INTO insights (event_slug, content, insight_type)
        VALUES (?, ?, ?)
    """, (event_slug, insights_content, 'general'))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Saved insights for event '{event_slug}'")

def update_event_status(event_slug: str, **kwargs) -> None:
    """Update event processing status"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    set_clauses = []
    params = []
    
    for key, value in kwargs.items():
        if key in ['is_processed', 'comments_count', 'sentiment_analyzed', 'insights_generated']:
            set_clauses.append(f"{key} = ?")
            params.append(value)
    
    if 'last_processed_at' not in kwargs:
        set_clauses.append("last_processed_at = ?")
        params.append(datetime.now().isoformat())
    
    params.append(event_slug)
    
    if set_clauses:
        sql = f"UPDATE sale_events SET {', '.join(set_clauses)} WHERE slug = ?"
        cursor.execute(sql, params)
        conn.commit()
    
    conn.close()

def get_event_data(event_slug: str) -> Dict[str, Any]:
    """Get all data for an event"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get event info
    cursor.execute("""
        SELECT slug, name, description, is_processed, comments_count,
               sentiment_analyzed, insights_generated, last_processed_at
        FROM sale_events WHERE slug = ?
    """, (event_slug,))
    
    event_info = cursor.fetchone()
    if not event_info:
        conn.close()
        return {}
    
    # Get comments
    cursor.execute("""
        SELECT submission_title, comment, subreddit, sentiment, sentiment_score, 
               author, score, created_utc, url
        FROM comments 
        WHERE event_slug = ? 
        ORDER BY score DESC, created_utc DESC
        LIMIT 100
    """, (event_slug,))
    
    comments = []
    for row in cursor.fetchall():
        comments.append({
            "submission_title": row[0],
            "comment": row[1],
            "subreddit": row[2], 
            "sentiment": row[3],
            "sentiment_score": row[4],
            "author": row[5],
            "score": row[6],
            "created_utc": row[7],
            "url": row[8]
        })
    
    # Get sentiment distribution
    cursor.execute("""
        SELECT sentiment, COUNT(*) as count
        FROM comments 
        WHERE event_slug = ? AND sentiment != ''
        GROUP BY sentiment
    """, (event_slug,))
    
    sentiment_distribution = []
    total_sentiments = 0
    for row in cursor.fetchall():
        count = row[1]
        total_sentiments += count
        sentiment_distribution.append({
            "sentiment": row[0],
            "count": count
        })
    
    # Calculate percentages
    for item in sentiment_distribution:
        item["percentage"] = round((item["count"] / total_sentiments) * 100, 1) if total_sentiments > 0 else 0
    
    # Get insights
    cursor.execute("""
        SELECT content FROM insights 
        WHERE event_slug = ? 
        ORDER BY created_at DESC 
        LIMIT 1
    """, (event_slug,))
    
    insights_row = cursor.fetchone()
    insights = insights_row[0] if insights_row else ""
    
    conn.close()
    
    return {
        "event": {
            "slug": event_info[0],
            "name": event_info[1],
            "description": event_info[2],
            "is_processed": bool(event_info[3]),
            "comments_count": event_info[4],
            "sentiment_analyzed": bool(event_info[5]),
            "insights_generated": bool(event_info[6]),
            "last_processed_at": event_info[7]
        },
        "comments": comments,
        "sentiment_distribution": sentiment_distribution,
        "insights": insights
    }

# Export functions
__all__ = [
    'init_database', 'get_sale_events', 'get_event_status', 'get_event_data',
    'RedditScraper', 'analyze_sentiment_batch', 'generate_insights',
    'save_comments', 'save_insights', 'update_event_status'
]