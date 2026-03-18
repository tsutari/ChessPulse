#!/bin/bash
# ChessPulse Frontend Startup Script

echo "🚀 Starting ChessPulse Frontend..."
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/frontend" || exit 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    echo "VITE_API=http://127.0.0.1:8000" > .env
fi

# Start the development server
echo ""
echo "✅ Starting Vite dev server on http://localhost:5173"
echo "   Press Ctrl+C to stop"
echo ""

npm run dev

