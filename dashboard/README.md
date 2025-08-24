# Amazon Sale AI Dashboard - Frontend

A modern React frontend for visualizing sentiment analysis of Reddit comments about Amazon sale events.

## Features

- **Modern React**: Built with React 18 and Vite
- **Responsive Design**: Clean, modern interface
- **Interactive Charts**: Sentiment visualization with Recharts
- **Real-time Data**: Connects to FastAPI backend
- **AI Insights**: Display AI-generated analysis
- **Error Handling**: Graceful error handling and loading states

## Installation

1. **Navigate to dashboard directory**:
   ```bash
   cd dashboard
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables** (optional):
   ```bash
   # Create .env file if you need to change API URL
   echo "VITE_API_BASE=http://localhost:8000" > .env
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:5173`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Components

### App.jsx
Main application component that manages state and API calls.

### SentimentChart.jsx
Interactive pie chart showing sentiment distribution using Recharts.

### CommentsTable.jsx
Table component displaying Reddit comments with sentiment analysis.

### InsightsPanel.jsx
Panel for generating and displaying AI insights with loading states.

## API Integration

The frontend communicates with the FastAPI backend through:
- Event management
- Comment retrieval
- Sentiment analysis display
- AI insight generation

## Styling

- **CSS-in-JS**: Inline styles for component isolation
- **Modern Design**: Clean, professional interface
- **Responsive**: Works on desktop and mobile
- **Color Coding**: Sentiment-based color coding

## Technologies Used

- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **Recharts**: Chart library for data visualization
- **ESLint**: Code linting and formatting

## Environment Variables

- `VITE_API_BASE`: Backend API URL (defaults to `http://localhost:8000`)

## Development

The application is designed to work seamlessly with the FastAPI backend. Make sure the backend is running before starting the frontend development server.