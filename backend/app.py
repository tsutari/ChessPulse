from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import chess, chess.engine, os, torch, torch.nn.functional as F, json, math
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

MODEL = TinyPolicyNet(); MODEL.eval()
STOCKFISH="/opt/homebrew/bin/stockfish"  # confirm with `which stockfish`
LEADERBOARD_FILE = "leaderboard.json"

class GameResult(BaseModel):
    user: str
    result: str
    moves: int
    timestamp: int

def pick_move(fen: str, depth: int = 10):
    b = chess.Board(fen)

    # 1. Run multipv=5 analysis — returns a list of up to 5 lines
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH)
    try:
        lines = engine.analyse(b, chess.engine.Limit(depth=depth), multipv=5)
    finally:
        engine.quit()

    if not lines or not lines[0].get("pv"):
        return {"move": None, "confidence": None, "heatmap": []}

    best_move = lines[0]["pv"][0]

    # 2. Centipawn score from Black's perspective (top line)
    cp = -lines[0]["score"].white().score(mate_score=10000)

    # 3. Sigmoid win probability
    p_stockfish = 1.0 / (1.0 + math.exp(-cp / 200.0))

    # 4. Neural network scalar confidence proxy
    x = board_to_tensor(b)
    with torch.no_grad():
        logits = MODEL(x).squeeze(0)
    neural_output = float(torch.sigmoid(logits.mean()))

    # 5. Combine, no clamping
    confidence = 0.7 * p_stockfish + 0.3 * neural_output

    # 6. Build heatmap: destination square + cp value (Black's perspective) per candidate
    heatmap = []
    for line in lines:
        if line.get("pv"):
            move = line["pv"][0]
            sq = chess.square_name(move.to_square)
            val = -line["score"].white().score(mate_score=10000)
            heatmap.append({"square": sq, "value": val})

    return {
        "move": best_move.uci(),
        "confidence": round(confidence, 3),
        "heatmap": heatmap,
    }

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
        data = json.load(f)
    return data

@app.post("/submit_result")
def submit_result(result: GameResult):
    if not os.path.exists(LEADERBOARD_FILE):
        data = {"rows": []}
    else:
        with open(LEADERBOARD_FILE, 'r') as f:
            data = json.load(f)
    
    data["rows"].append({
        "user": result.user,
        "result": result.result,
        "moves": result.moves,
        "timestamp": result.timestamp
    })
    
    # Keep only the last 50 entries
    data["rows"] = data["rows"][-50:]
    
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    return {"status": "success"}

