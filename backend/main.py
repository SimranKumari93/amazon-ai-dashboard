import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging

from lib.utils import (
    init_database, get_sale_events, get_event_status, get_event_data,
    RedditScraper, analyze_sentiment_batch, generate_insights,
    save_comments, save_insights, update_event_status, DATABASE_PATH
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class ProcessEventRequest(BaseModel):
    event_slug: str
    keywords: Optional[List[str]] = None
    max_posts: Optional[int] = 50
    force_refresh: Optional[bool] = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_database()
    logger.info("Database initialized")
    yield
    # Shutdown (if needed)

# Initialize FastAPI app
app = FastAPI(
    title="Amazon Sale AI Dashboard",
    description="AI-powered sentiment analysis for Amazon sale events",
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

@app.get("/events")
def list_events():
    """Get all sale events with their processing status"""
    try:
        events_data = get_event_status()
        return {"success": True, "data": events_data["events"]}
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")

@app.get("/events/{event_slug}")
def get_event_details(event_slug: str):
    """Get detailed data for a specific event"""
    try:
        event_data = get_event_data(event_slug)
        
        if not event_data:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return {"success": True, "data": event_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching event data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching event data: {str(e)}")

@app.post("/events/{event_slug}/scrape-comments")
def scrape_comments(event_slug: str, request: ProcessEventRequest):
    """Scrape comments for an event"""
    try:
        # Check if event exists
        events = get_sale_events()
        event = next((e for e in events if e['slug'] == event_slug), None)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        logger.info(f"Scraping comments for event: {event_slug}")
        
        # Step 1: Scrape comments
        scraper = RedditScraper()
        if not scraper.test_connection():
            raise HTTPException(status_code=500, detail="Reddit API connection failed")
            
        comments = scraper.scrape_event_data(
            event_slug, 
            request.keywords or ["amazon sale", "amazon deals", "amazon discount"],
            request.max_posts or 50
        )
        
        if not comments:
            raise HTTPException(status_code=404, detail="No comments found")
        
        # Step 2: Save comments (without sentiment analysis)
        for comment in comments:
            comment['sentiment'] = ''
            comment['sentiment_score'] = 0.0
        
        saved_count = save_comments(comments, event_slug)
        
        # Step 3: Update event status
        update_event_status(
            event_slug,
            comments_count=saved_count,
            is_processed=True
        )
        
        return {
            "success": True,
            "message": f"Successfully scraped {saved_count} comments",
            "data": {
                "comments_count": saved_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping comments for event {event_slug}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events/{event_slug}/analyze-sentiment")
def analyze_event_sentiment(event_slug: str):
    """Analyze sentiment for scraped comments"""
    try:
        # Check if event exists
        events = get_sale_events()
        event = next((e for e in events if e['slug'] == event_slug), None)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        logger.info(f"Analyzing sentiment for event: {event_slug}")
        
        # Get existing comments from database
        import sqlite3
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, comment FROM comments 
            WHERE event_slug = ? AND (sentiment IS NULL OR sentiment = '')
        """, (event_slug,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No comments found to analyze")
        
        # Analyze sentiment for comments
        comments_data = [{'id': row[0], 'comment': row[1]} for row in rows]
        analyzed_comments = analyze_sentiment_batch(comments_data)
        
        # Update comments in database
        updated_count = 0
        for comment in analyzed_comments:
            try:
                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE comments 
                    SET sentiment = ?, sentiment_score = ?
                    WHERE id = ?
                """, (comment['sentiment'], comment['sentiment_score'], comment['id']))
                conn.commit()
                conn.close()
                updated_count += 1
            except Exception as e:
                logger.error(f"Error updating comment {comment['id']}: {e}")
                continue
        
        # Update event status
        update_event_status(event_slug, sentiment_analyzed=True)
        
        return {
            "success": True,
            "message": f"Successfully analyzed sentiment for {updated_count} comments",
            "data": {
                "analyzed_count": updated_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing sentiment for event {event_slug}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events/{event_slug}/generate-insights")
def generate_event_insights(event_slug: str):
    """Generate AI insights for an event"""
    try:
        # Check if event exists
        events = get_sale_events()
        event = next((e for e in events if e['slug'] == event_slug), None)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        logger.info(f"Generating insights for event: {event_slug}")
        
        # Generate insights
        insights = generate_insights(event_slug)
        if not insights or "unavailable" in insights.lower():
            raise HTTPException(status_code=500, detail="Failed to generate insights")
        
        # Save insights
        save_insights(event_slug, insights)
        
        # Update event status
        update_event_status(event_slug, insights_generated=True)
        
        return {
            "success": True,
            "message": "Successfully generated AI insights",
            "data": {
                "insights": insights
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating insights for event {event_slug}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/{event_slug}/status")
def get_processing_status(event_slug: str):
    """Get processing status for an event"""
    try:
        status = get_event_status(event_slug)
        
        if not status:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return {"success": True, "data": status}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching status: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching status: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)