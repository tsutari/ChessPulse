from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import chess, chess.engine, os, json, math
from model import TinyPolicyNet
from utils import board_to_tensor, legal_moves
from pydantic import BaseModel

app = FastAPI(title="ChessPulse API")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STOCKFISH = "/opt/homebrew/bin/stockfish"  # confirm with `which stockfish`
LEADERBOARD_FILE = "leaderboard.json"

_model = None
_engine = None

def get_model():
    global _model
    if _model is None:
        _model = TinyPolicyNet()
    return _model

def get_engine():
    global _engine
    if _engine is None:
        _engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH)
    return _engine

class GameResult(BaseModel):
    user: str
    result: str
    moves: int
    timestamp: int

def pick_move(fen: str, depth: int = 10):
    b = chess.Board(fen)

    # 1. Run Stockfish analysis (single search — best move comes from pv[0])
    result = get_engine().analyse(b, chess.engine.Limit(depth=depth))

    if not result.get("pv"):
        return {"move": None, "confidence": None}

    best_move = result["pv"][0]

    # 2. Centipawn score from Black's perspective
    cp = -result["score"].white().score(mate_score=10000)

    # 3. Sigmoid win probability
    p_stockfish = 1.0 / (1.0 + math.exp(-cp / 200.0))

    # 4. Neural network scalar confidence proxy
    x = board_to_tensor(b)
    neural_output = get_model().forward(x)

    # 5. Combine, no clamping
    confidence = 0.7 * p_stockfish + 0.3 * neural_output

    return {"move": best_move.uci(), "confidence": round(confidence, 3)}

@app.get("/")
def root():
    return {"message": "ChessPulse API is running", "status": "ok"}

@app.get("/move")
def move(fen: str, depth: int = 10):
    return pick_move(fen, depth)

@app.get("/leaderboard")
def get_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return {"rows": []}
    with open(LEADERBOARD_FILE, 'r') as f:
        rows = json.load(f).get("rows", [])
    top10 = sorted(rows, key=lambda r: r["moves"], reverse=True)[:10]
    return {"rows": top10}

@app.post("/submit_result")
def submit_result(result: GameResult):
    if result.result not in ("Win", "Loss", "Draw"):
        raise HTTPException(status_code=400, detail="result must be Win, Loss, or Draw")
    if not os.path.exists(LEADERBOARD_FILE):
        rows = []
    else:
        with open(LEADERBOARD_FILE, 'r') as f:
            rows = json.load(f).get("rows", [])
    rows.append({
        "user": result.user,
        "result": result.result,
        "moves": result.moves,
        "timestamp": result.timestamp,
    })
    rows = rows[-100:]
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump({"rows": rows}, f, indent=2)
    return {"status": "success"}

