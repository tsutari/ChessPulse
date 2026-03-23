# ChessPulse

A chess app where you play against Stockfish and watch its confidence shift in real time.

Live at **[tsutari.github.io/ChessPulse](https://tsutari.github.io/ChessPulse)**.

## What it does

You play White and Stockfish plays Black. After every AI move a confidence score shows how good Stockfish thinks its position is, plotted on a live chart as the game goes on, and results are tracked on the leaderboard.

## Tech stack

- Frontend: plain HTML/CSS/JS with chess.js and chessboard.js, no build step needed
- Backend: FastAPI and python-chess to talk to Stockfish
- Confidence score: Stockfish centipawn eval run through a sigmoid, blended with a small NumPy MLP
- Deployed on Render (backend) and GitHub Pages (frontend)

## How the confidence score works

The confidence score is Stockfish's centipawn evaluation run through a sigmoid, blended 70/30 with a small NumPy MLP running on the board state.
