# Amazon Sale AI Dashboard - Backend

A FastAPI backend for sentiment analysis of Reddit comments about Amazon sale events, powered by Gemini AI.

## Features

- **SQLite Database**: Efficient local storage instead of CSV files
- **Gemini AI Integration**: Uses Google's Gemini model via OpenAI-compatible API
- **RESTful API**: Simple and intuitive endpoints
- **Sample Data**: Automatically generates sample data for demonstration
- **CORS Support**: Ready for frontend integration

## Installation

1. **Clone the repository**:
   ```bash
   cd backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

4. **Run the server**:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## Environment Variables

Create a `.env` file with:

```env
GEMINI_API_KEY=your_gemini_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=AmazonDashboard/1.0
FRONTEND_ORIGIN=http://localhost:5173
```

## API Endpoints

### Events
- `GET /events` - Get all sale events
- `POST /events` - Create a new sale event

### Comments
- `GET /events/{event_slug}/comments` - Get comments for an event
- `POST /events/{event_slug}/comments` - Add comments to an event

### Sentiment Analysis
- `GET /events/{event_slug}/sentiment` - Get sentiment summary for an event

### AI Insights
- `POST /events/{event_slug}/insights` - Generate AI insights for an event
- `GET /events/{event_slug}/insights` - Get latest insights for an event

## Database Schema

The SQLite database includes:
- **sale_events**: Store sale event information
- **reddit_comments**: Store comments with sentiment analysis
- **insights**: Store AI-generated insights

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Sample Data

The application automatically creates sample events and comments for demonstration purposes when the database is empty.

## Technologies Used

- **FastAPI**: Modern Python web framework
- **SQLite**: Lightweight database
- **Gemini AI**: Google's language model
- **OpenAI Library**: For API compatibility
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server