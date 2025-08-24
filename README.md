# Amazon Sale AI Dashboard

## 🎯 Overview

AI-powered sentiment analysis dashboard that scrapes Reddit discussions about Amazon sales and provides comprehensive insights using Gemini AI.

## ✨ Features

- **Reddit Scraping**: Multi-subreddit data collection with smart filtering
- **AI Sentiment Analysis**: Real-time sentiment analysis using Gemini AI
- **Comprehensive Insights**: Detailed AI-generated recommendations and analysis
- **Clean UI**: Responsive design with inline styles (no external CSS dependencies)
- **Smart Caching**: Processed events load instantly, with refresh options

## 🔄 Workflow

1. **Comments Section** (First) - Scraped Reddit discussions with pagination and filtering
2. **Sentiment Distribution** (Second) - AI-analyzed sentiment charts and breakdowns  
3. **AI Insights** (Third) - Comprehensive Gemini AI analysis with actionable recommendations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 16+ with npm
- Reddit API credentials ([Get here](https://www.reddit.com/prefs/apps))
- Gemini API key ([Get here](https://aistudio.google.com/))

### Setup

1. **Clone and navigate:**
   ```bash
   cd amazon-ai-dashboard
   ```

2. **Install dependencies:**
   ```bash
   cd backend && pip install -r requirements.txt
   cd ../dashboard && npm install
   ```

3. **Configure environment:**
   Create `.env` file in `backend/` directory:
   ```env
   REDDIT_CLIENT_ID=your_reddit_client_id
   REDDIT_CLIENT_SECRET=your_reddit_client_secret
   REDDIT_USER_AGENT=AmazonDashboard/2.0
   GEMINI_API_KEY=your_gemini_api_key
   ```

4. **Start the system:**
   ```bash
   ./start.sh
   ```

### Manual Start
```bash
# Backend
cd backend && PYTHONPATH=. python3 main.py

# Frontend  
cd dashboard && VITE_API_BASE=http://localhost:8000 npm run dev
```

## 🏗️ Architecture

### Backend (FastAPI)
- `main.py` - API server with workflow endpoints
- `lib/utils.py` - Core functionality with sentiment analysis
- **Database**: SQLite with event processing state tracking
- **APIs**: RESTful endpoints for event management and processing

### Frontend (React + Vanilla CSS)
- `App.jsx` - Single-file architecture with all components
- **Styling**: Pure inline styles (no Tailwind or external CSS)
- **Components**: EventSelector, CommentsSection, SentimentSection, InsightsSection

## 📊 Usage

### First Time Processing:
1. Select an event from dropdown (shows "○" = not processed)
2. Enter keywords (e.g., "amazon prime day, amazon deals")
3. Click "Process Event"
4. Wait 2-5 minutes for complete analysis
5. View results: Comments → Sentiment → Insights

### Returning User:
1. Select a processed event (shows "✓" = processed)
2. Instantly view cached results
3. Use "Refresh Data" to reprocess with new data

## 🎯 Configuration

### Sale Events
Edit `backend/lib/sale_events.json`:
```json
{
  "name": "Republic Day Sale",
  "slug": "republic_day_sale", 
  "start_date": "2025-01-20",
  "end_date": "2025-01-26",
  "description": "Amazon's Republic Day sale"
}
```

### Subreddits
Edit `backend/lib/subreddits.txt`:
```
IndiaDeals
AmazonIndia
IndianGaming
```

## 🛠️ Development

### API Endpoints
- `GET /events` - List all events with processing status
- `GET /events/{slug}` - Get detailed event data  
- `POST /events/{slug}/process` - Process event (scrape + analyze + insights)
- `GET /events/{slug}/status` - Check processing status

### Testing
```bash
cd backend && python3 test_api.py
```

## 🚨 Troubleshooting

### Events not loading
- Ensure backend is running on port 8000
- Check API connection: `curl http://localhost:8000/`

### Processing fails  
- Verify Reddit API credentials
- Check GEMINI_API_KEY is valid
- Monitor backend logs for errors

### No comments found
- Try different keywords
- Check subreddit relevance  
- Verify date ranges for older events

## 📈 Performance

- **Small event**: 50 comments, 1-2 minutes
- **Medium event**: 200 comments, 3-5 minutes  
- **Large event**: 500+ comments, 5-10 minutes

## 🔧 Tech Stack

- **Backend**: FastAPI, SQLite, PRAW (Reddit API), Gemini AI
- **Frontend**: React, Vite, Vanilla CSS
- **Deployment**: Self-hosted with simple start script

---

**🎉 Start exploring Amazon sale sentiment with AI-powered insights!**

Visit: http://localhost:3000 after running `./start.sh`
