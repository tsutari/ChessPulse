import { useState, useEffect } from "react";
import ChessBoard from "./ChessBoard.jsx";
import { getLeaderboard } from "./api";
import "./App.css";

export default function App() {
  const [styleMode, setStyleMode] = useState("classic");
  const [rows, setRows] = useState([]);

  const refresh = async () => {
    const lb = await getLeaderboard();
    setRows(lb.rows || []);
  };

  useEffect(() => { refresh(); }, []);

  return (
    <div className="app-container">
      <div className="main-section">
        <h1>♟️ ChessPulse</h1>
        <p>Play chess against a neural-network powered AI. Adjust its style:</p>
        <select 
          className="style-selector"
          value={styleMode} 
          onChange={e => setStyleMode(e.target.value)}
        >
          <option value="defensive">🛡️ Defensive</option>
          <option value="classic">⚖️ Classic</option>
          <option value="aggressive">⚔️ Aggressive</option>
        </select>
        <div className="board-container">
          <ChessBoard styleMode={styleMode} onGameEnd={refresh} />
        </div>
      </div>
      <div className="leaderboard-section">
        <h2>🏆 Leaderboard</h2>
        <button className="refresh-button" onClick={refresh}>
          ↻ Refresh
        </button>
        {rows.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#999' }}>No games yet. Be the first!</p>
        ) : (
          <ul className="leaderboard-list">
            {rows.map((r, i) => (
              <li key={i}>
                <div style={{ fontSize: '0.85em', color: '#999', marginBottom: '4px' }}>
                  {new Date((r.timestamp || 0) * 1000).toLocaleString()}
                </div>
                <div>
                  <strong>{r.user}</strong> • Result: <strong>{r.result}</strong> • {r.moves} moves
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
