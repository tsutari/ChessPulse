# 🚀 ChessPulse Quick Start Guide

Get ChessPulse running locally in **5 minutes**!

## Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.12+** installed (`python3 --version`)
- ✅ **Node.js 18+** installed (`node --version`)
- ✅ **Stockfish** chess engine (`brew install stockfish` on macOS)

## 🏃 Quick Start

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/ChessPulse.git
cd ChessPulse
```

### Step 2: Start the Backend (Terminal 1)

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# OR on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify Stockfish installation
which stockfish
# Copy the path and update line 20 in app.py if different from /opt/homebrew/bin/stockfish

# Start the FastAPI server
uvicorn app:app --reload --port 8000
```

✅ **Backend ready!** Visit http://localhost:8000 to verify (you should see a JSON response)

### Step 3: Start the Frontend (Terminal 2)

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Verify .env file exists with correct backend URL
cat .env
# Should show: VITE_API=http://127.0.0.1:8000

# Start the Vite dev server
npm run dev
```

✅ **Frontend ready!** Visit http://localhost:5173 to play chess!

## 🎮 Using ChessPulse

1. **Open your browser** to http://localhost:5173
2. **Select AI style**: Choose between Defensive 🛡️, Classic ⚖️, or Aggressive ⚔️
3. **Make your move**: Drag and drop pieces on the board
4. **Watch the AI respond**: See confidence scores in real-time
5. **Check the leaderboard**: View game history on the right panel

## 🧪 Testing the API

Test the backend directly:

```bash
# Get AI move for starting position
curl "http://localhost:8000/move?fen=rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR%20w%20KQkq%20-%200%201&style=classic"

# Get leaderboard
curl http://localhost:8000/leaderboard

# Check API status
curl http://localhost:8000
```

## 🐛 Troubleshooting

### Backend won't start

**Issue:** `ModuleNotFoundError: No module named 'fastapi'`  
**Solution:** Make sure you activated the virtual environment and installed dependencies:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

**Issue:** Stockfish not found  
**Solution:** Install Stockfish and update the path in `backend/app.py`:
```bash
brew install stockfish
which stockfish  # Copy this path
# Edit app.py line 20 with the correct path
```

### Frontend won't start

**Issue:** `Cannot find module 'react'`  
**Solution:** Install dependencies:
```bash
npm install
```

**Issue:** API calls failing with CORS errors  
**Solution:** 
1. Verify backend is running on port 8000
2. Check `.env` file has `VITE_API=http://127.0.0.1:8000`
3. Restart the frontend dev server after changing `.env`

**Issue:** Chess board not showing  
**Solution:** Clear browser cache and hard reload (Cmd+Shift+R on Mac)

### Port already in use

**Backend (port 8000):**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9
```

**Frontend (port 5173):**
```bash
# Find and kill the process
lsof -ti:5173 | xargs kill -9
```

## 📁 Project Structure

```
ChessPulse/
├── backend/
│   ├── app.py              # FastAPI server
│   ├── model.py            # Neural network
│   ├── utils.py            # Helper functions
│   ├── leaderboard.json    # Game history
│   └── requirements.txt    # Python packages
│
└── frontend/
    ├── src/
    │   ├── App.jsx         # Main component
    │   ├── ChessBoard.jsx  # Chess game logic
    │   └── api.js          # Backend API calls
    ├── .env                # Backend URL config
    └── package.json        # Node packages
```

## 🔧 Development Commands

### Backend

```bash
# Start with auto-reload
uvicorn app:app --reload --port 8000

# Run in production mode (no reload)
uvicorn app:app --host 0.0.0.0 --port 8000

# View API docs
open http://localhost:8000/docs
```

### Frontend

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🎯 Next Steps

- **Customize AI behavior**: Edit `backend/model.py` and `backend/utils.py`
- **Improve UI**: Modify `frontend/src/App.css` and components
- **Add features**: See the main [README.md](README.md) for future enhancements
- **Deploy to AWS**: Follow the deployment guide in [README.md](README.md)

## 💡 Tips

- Use **Chrome DevTools** (F12) to debug frontend issues
- Check **Terminal logs** for backend errors
- The AI uses **Stockfish as fallback** when confidence is low (<25%)
- Game results are saved to `backend/leaderboard.json`
- The neural network is **untrained** (random weights) - it's a demo architecture

## 🆘 Still Having Issues?

1. Check that all prerequisites are installed
2. Ensure you're running commands from the correct directory
3. Verify both frontend and backend are running simultaneously
4. Try restarting both servers
5. Check the GitHub Issues page for known problems

---

**Happy Chess Playing! ♟️**

For detailed documentation, see [README.md](README.md)

