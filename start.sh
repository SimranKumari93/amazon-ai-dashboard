#!/bin/bash

echo "🚀 Amazon AI Dashboard - Clean & Optimized"
echo "=========================================="

# Navigate to project directory
PROJECT_DIR="/Users/debsouryadatta/Desktop/neel/Coding/Practice/amazon-ai-dashboard"
cd "$PROJECT_DIR"

# Start backend server
echo "🔧 Starting backend server..."
cd backend
PYTHONPATH=. python3 main.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Test backend health
echo "🩺 Testing backend health..."
HEALTH_CHECK=$(curl -s http://localhost:8000/ | grep -c "running" || echo "0")
if [ "$HEALTH_CHECK" -gt 0 ]; then
    echo "✅ Backend is healthy"
else
    echo "⚠️ Backend might not be ready yet, continuing anyway..."
fi

# Navigate to frontend
cd ../dashboard

# Start frontend with clean version (no Tailwind dependencies needed)
echo "🎨 Starting clean frontend..."
VITE_API_BASE=http://localhost:8000 npx vite --port 3000 --host 0.0.0.0 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait a moment for servers to start
sleep 2

echo ""
echo "🎉 Amazon AI Dashboard is running!"
echo "================================="
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "✨ Clean Features:"
echo "   - No Tailwind CSS (pure inline styles)"
echo "   - Proper section ordering: Comments → Sentiment → AI Insights"
echo "   - All components in single file for easy maintenance"
echo "   - Responsive design with clean CSS"
echo ""
echo "🔄 Correct Workflow:"
echo "   1. Comments Section (FIRST) - Shows scraped Reddit data"
echo "   2. Sentiment Distribution (SECOND) - AI-analyzed charts"
echo "   3. AI Insights (THIRD) - Comprehensive Gemini analysis"
echo ""
echo "💡 To get started:"
echo "   1. Select an event from the dropdown"
echo "   2. All 3 sections will appear (initially empty)"
echo "   3. Click 'Process Event' to scrape & analyze"
echo "   4. Watch data populate in correct order"
echo ""
echo "Press Ctrl+C to stop both servers"

# Create cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap for cleanup
trap cleanup INT

# Wait for user to stop
wait