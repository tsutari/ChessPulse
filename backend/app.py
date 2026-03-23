from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import chess, chess.engine, os, json, math, shutil, random, logging
from model import TinyPolicyNet
from utils import board_to_tensor, legal_moves
from pydantic import BaseModel

app = FastAPI(title="ChessPulse API")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tsutari.github.io",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_STOCKFISH_WARNING_LOGGED = False

def _resolve_stockfish():
    for candidate in [
        os.environ.get("STOCKFISH_PATH"),
        shutil.which("stockfish"),
        "/usr/bin/stockfish",
        "/usr/games/stockfish",
    ]:
        if candidate and os.path.isfile(candidate):
            return candidate
    return None

STOCKFISH = _resolve_stockfish()

def _get_stockfish_move(fen: str, depth: int = 10):
    """Return (uci_move, cp) using Stockfish, or a random legal move if unavailable."""
    global _STOCKFISH_WARNING_LOGGED
    b = chess.Board(fen)
    if STOCKFISH is None:
        if not _STOCKFISH_WARNING_LOGGED:
            logging.warning("Stockfish not found — falling back to random legal moves.")
            _STOCKFISH_WARNING_LOGGED = True
        move = random.choice(list(b.legal_moves))
        return move.uci(), 0
    engine = get_engine()
    result = engine.analyse(b, chess.engine.Limit(depth=depth))
    best_move = result["pv"][0] if result.get("pv") else None
    if not best_move:
        move = random.choice(list(b.legal_moves))
        return move.uci(), 0
    cp = -result["score"].white().score(mate_score=10000)
    return best_move.uci(), cp

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
    if _engine is None and STOCKFISH:
        _engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH)
    return _engine

class GameResult(BaseModel):
    user: str
    result: str
    moves: int
    timestamp: int

def pick_move(fen: str, depth: int = 10):
    b = chess.Board(fen)

    # 1. Get best move + centipawn via Stockfish (or random fallback)
    uci_move, cp = _get_stockfish_move(fen, depth)

    if not uci_move:
        return {"move": None, "confidence": None}

    # 2. Sigmoid win probability from Black's perspective
    p_stockfish = 1.0 / (1.0 + math.exp(-cp / 200.0))

    # 3. Neural network scalar confidence proxy
    x = board_to_tensor(b)
    neural_output = get_model().forward(x)

    # 4. Combine, no clamping
    confidence = 0.7 * p_stockfish + 0.3 * neural_output

    return {"move": uci_move, "confidence": round(confidence, 3)}

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

@app.get("/debug")
def debug():
    import shutil, os
    return {
        "which_stockfish": shutil.which("stockfish"),
        "usr_bin_exists": os.path.isfile("/usr/bin/stockfish"),
        "usr_games_exists": os.path.isfile("/usr/games/stockfish"),
        "env_var": os.environ.get("STOCKFISH_PATH")
    }

