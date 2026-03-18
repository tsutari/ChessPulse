import { useState, useRef } from "react";
import { Chessboard } from "react-chessboard";
import { Chess } from "chess.js";
import { getMove, submitResult } from "./api";

export default function ChessBoard({ styleMode, onGameEnd }) {
  // Use useRef to maintain the game instance without causing re-renders
  const game = useRef(new Chess());
  const [fen, setFen] = useState(game.current.fen());
  const [thinking, setThinking] = useState(false);
  const [conf, setConf] = useState(null);
  const [gameOver, setGameOver] = useState(false);
  const [lastMove, setLastMove] = useState(null);

  const makeAiMove = async () => {
    if (gameOver) return;
    
    setThinking(true);
    try {
      const currentFen = game.current.fen();
      const res = await getMove(currentFen, styleMode);
      
      if (res.move) {
        try {
          const moveObj = game.current.move(res.move);
          if (moveObj) {
            setFen(game.current.fen());
            setConf(res.confidence);
            setLastMove({ from: moveObj.from, to: moveObj.to });
            
            // Check game over after AI move
            if (game.current.isGameOver()) {
              setGameOver(true);
              await submitResult({
                user: "Guest",
                result: game.current.isCheckmate() ? "AI Won" : "Draw",
                moves: game.current.history().length,
                timestamp: Math.floor(Date.now() / 1000),
              });
              if (onGameEnd) onGameEnd();
            }
          }
        } catch (e) {
          console.error("Invalid AI move:", res.move, e);
        }
      }
    } catch (error) {
      console.error("AI move error:", error);
    }
    setThinking(false);
  };

  function onDrop(sourceSquare, targetSquare) {
    if (gameOver || thinking) {
      console.log("Can't move: game over or AI thinking");
      return false;
    }
    
    try {
      // Try to make the move
      const move = game.current.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: 'q' // Always promote to queen for simplicity
      });
      
      // If move is invalid, chess.js returns null
      if (move === null) {
        console.log("Invalid move attempted:", sourceSquare, "to", targetSquare);
        return false;
      }
      
      // Move was successful, update the board
      console.log("Valid move made:", move);
      setFen(game.current.fen());
      setLastMove({ from: sourceSquare, to: targetSquare });
      setConf(null);
      
      // Check if game is over
      if (game.current.isGameOver()) {
        setGameOver(true);
        submitResult({
          user: "Guest",
          result: game.current.isCheckmate() ? "Player Won" : "Draw",
          moves: game.current.history().length,
          timestamp: Math.floor(Date.now() / 1000),
        }).then(() => {
          if (onGameEnd) onGameEnd();
        });
        return true;
      }
      
      // Trigger AI move after a short delay
      setTimeout(makeAiMove, 500);
      return true;
      
    } catch (error) {
      console.error("Move error:", error);
      return false;
    }
  }

  const resetGame = () => {
    game.current = new Chess();
    setFen(game.current.fen());
    setGameOver(false);
    setThinking(false);
    setConf(null);
    setLastMove(null);
  };

  const getStatusMessage = () => {
    if (gameOver) {
      if (game.current.isCheckmate()) {
        return game.current.turn() === "w" ? "🎉 You Won!" : "🤖 AI Won!";
      }
      if (game.current.isDraw()) return "🤝 Draw!";
      if (game.current.isStalemate()) return "🤝 Stalemate!";
    }
    if (thinking) return "🤔 AI is thinking...";
    if (conf !== null) return `🎯 AI confidence: ${(conf * 100).toFixed(1)}%`;
    if (game.current.inCheck()) return "⚠️ Check! Your move";
    return "♟️ Your move";
  };

  return (
    <div>
      <Chessboard 
        position={fen}
        onPieceDrop={onDrop}
        customSquareStyles={lastMove ? {
          [lastMove.from]: { backgroundColor: 'rgba(255, 255, 0, 0.4)' },
          [lastMove.to]: { backgroundColor: 'rgba(255, 255, 0, 0.4)' }
        } : {}}
        arePiecesDraggable={!gameOver && !thinking}
        boardWidth={560}
      />
      <div style={{ 
        marginTop: 16, 
        padding: 16, 
        background: '#f5f5f5', 
        borderRadius: 8,
        textAlign: 'center',
        fontSize: '1.1em',
        fontWeight: 500
      }}>
        {getStatusMessage()}
      </div>
      {gameOver && (
        <button 
          onClick={resetGame}
          style={{
            marginTop: 16,
            width: '100%',
            padding: 12,
            fontSize: '1.1em',
            backgroundColor: '#646cff',
            color: 'white',
            border: 'none',
            borderRadius: 8,
            cursor: 'pointer',
            fontWeight: 600
          }}
        >
          🔄 New Game
        </button>
      )}
    </div>
  );
}
