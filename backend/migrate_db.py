#!/usr/bin/env python3
"""
Database migration script to update schema to new version
"""

import sqlite3
import os
from pathlib import Path

# Get the database path
BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / "amazon_dashboard.db"

def migrate_database():
    """Migrate database to new schema"""
    print(f"🔄 Migrating database: {DATABASE_PATH}")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Check existing columns in sale_events
        cursor.execute("PRAGMA table_info(sale_events)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Existing columns: {columns}")
        
        # Add missing columns to sale_events
        if 'is_processed' not in columns:
            print("Adding is_processed column...")
            cursor.execute("ALTER TABLE sale_events ADD COLUMN is_processed BOOLEAN DEFAULT FALSE")
            
        if 'comments_count' not in columns:
            print("Adding comments_count column...")
            cursor.execute("ALTER TABLE sale_events ADD COLUMN comments_count INTEGER DEFAULT 0")
            
        if 'sentiment_analyzed' not in columns:
            print("Adding sentiment_analyzed column...")
            cursor.execute("ALTER TABLE sale_events ADD COLUMN sentiment_analyzed BOOLEAN DEFAULT FALSE")
            
        if 'insights_generated' not in columns:
            print("Adding insights_generated column...")
            cursor.execute("ALTER TABLE sale_events ADD COLUMN insights_generated BOOLEAN DEFAULT FALSE")
            
        if 'last_processed_at' not in columns:
            print("Adding last_processed_at column...")
            cursor.execute("ALTER TABLE sale_events ADD COLUMN last_processed_at TIMESTAMP")
        
        # Check and update comments table if needed
        cursor.execute("PRAGMA table_info(comments)")
        comment_columns = [column[1] for column in cursor.fetchall()]
        print(f"Comments table columns: {comment_columns}")
        
        if 'sentiment_score' not in comment_columns:
            print("Adding sentiment_score column to comments...")
            cursor.execute("ALTER TABLE comments ADD COLUMN sentiment_score REAL DEFAULT 0.0")
            
        if 'comment_hash' not in comment_columns:
            print("Adding comment_hash column to comments...")
            cursor.execute("ALTER TABLE comments ADD COLUMN comment_hash TEXT")
            
        # Create insights table if it doesn't exist
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
        
        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_comments_event_slug ON comments (event_slug)",
            "CREATE INDEX IF NOT EXISTS idx_comments_sentiment ON comments (sentiment)",
            "CREATE INDEX IF NOT EXISTS idx_comments_created_utc ON comments (created_utc)",
            "CREATE INDEX IF NOT EXISTS idx_comments_hash ON comments (comment_hash)",
            "CREATE INDEX IF NOT EXISTS idx_insights_event_slug ON insights (event_slug)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
            
        conn.commit()
        print("✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()