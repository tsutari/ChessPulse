const BASE = import.meta.env.VITE_API;

export async function getMove(fen, style="classic") {
  const res = await fetch(`${BASE}/move?fen=${encodeURIComponent(fen)}&style=${style}`);
  return res.json();
}

export async function getLeaderboard() {
  const res = await fetch(`${BASE}/leaderboard`);
  return res.json();
}

export async function submitResult(data) {
  await fetch(`${BASE}/submit_result`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(data)
  });
}
