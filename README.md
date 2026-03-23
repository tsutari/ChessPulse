# ChessPulse

A chess app where you play against Stockfish and watch its confidence shift in real time. I play chess and wanted to see if I could build something that visualized how the engine reads the position as the game unfolds.

Live at **[tsutari.github.io/ChessPulse](https://tsutari.github.io/ChessPulse)**.

## What it does

You play White and Stockfish plays Black. After every AI move a confidence score shows how good Stockfish thinks its position is, plotted on a live chart as the game goes on. There's also a leaderboard if you actually manage to beat it.

## Tech stack

- Frontend: plain HTML/CSS/JS with chess.js and chessboard.js, no build step needed
- Backend: FastAPI and python-chess to talk to Stockfish
- Confidence score: Stockfish centipawn eval run through a sigmoid, blended with a small NumPy MLP
- Deployed on Render (backend) and GitHub Pages (frontend)

## How the confidence score works

Mostly the Stockfish centipawn evaluation converted to a probability with a sigmoid. The neural net component is a small MLP running on the board state that adds an offset -- the two signals are weighted 70/30. The number is meaningful because the Stockfish eval driving it is real.
