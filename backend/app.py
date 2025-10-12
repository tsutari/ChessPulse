from fastapi import FastAPI
import chess, subprocess, os, torch, torch.nn.functional as F
from model import TinyPolicyNet
from utils import board_to_tensor, legal_moves

app = FastAPI(title="ChessPulse API")
MODEL = TinyPolicyNet(); MODEL.eval()
STOCKFISH="/opt/homebrew/bin/stockfish"  # confirm with `which stockfish`

def pick_move(fen,style="classic"):
    b=chess.Board(fen)
    x=board_to_tensor(b)
    with torch.no_grad(): logits=MODEL(x).squeeze(0)
    temp={"defensive":0.5,"classic":1.0,"aggressive":1.5}.get(style,1.0)
    probs=F.softmax(logits/temp,0)
    leg=legal_moves(b)
    step=max(1,len(probs)//max(1,len(leg)))
    scored=[(m,float(probs[min(i*step,probs.size(0)-1)])) for i,m in enumerate(leg)]
    scored.sort(key=lambda t:t[1],reverse=True)
    mv,p=(scored[0] if scored else (None,0))
    if not mv or p<0.25:
        proc=subprocess.run([STOCKFISH],
            input=f"position fen {fen}\ngo depth 6\nquit\n".encode(),
            capture_output=True)
        for line in proc.stdout.decode().splitlines():
            if line.startswith("bestmove"):
                mv=line.split()[1]; p=0.95; break
    return {"move":mv,"confidence":round(p,3),"top_moves":scored[:3]}

@app.get("/move")
def move(fen:str,style:str="classic"):
    return pick_move(fen,style)

