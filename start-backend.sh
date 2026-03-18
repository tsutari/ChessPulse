#!/bin/bash
# ChessPulse Backend Startup Script

echo "🚀 Starting ChessPulse Backend..."
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/backend" || exit 1

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if Stockfish is installed
if ! command -v stockfish &> /dev/null; then
    echo "⚠️  WARNING: Stockfish not found!"
    echo "   Install it with: brew install stockfish"
    echo ""
fi

# Start the server
echo ""
echo "✅ Starting FastAPI server on http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""

uvicorn app:app --reload --port 8000

