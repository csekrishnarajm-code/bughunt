// Small wrapper around the FastAPI endpoints.

async function readError(res) {
  try {
    const body = await res.json();
    const detail = body.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length) return "Please check your input: " + detail.map((d) => d.msg).join(", ");
  } catch {
    /* fall through */
  }
  return `Something went wrong (error ${res.status}). Please try again.`;
}

async function request(path, options) {
  let res;
  try {
    res = await fetch(path, options);
  } catch {
    throw new Error("Cannot reach the server. Check your connection and try again.");
  }
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

const post = (path, body) =>
  request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

export const createGame = (language, rounds) => post("/api/games", { language, rounds });
export const nextChallenge = (id) => post(`/api/games/${id}/next`);
export const getHint = (id) => post(`/api/games/${id}/hint`);
export const sendAnswer = (id, line) => post(`/api/games/${id}/answer`, { line });
export const getGame = (id) => request(`/api/games/${id}`);
export const submitScore = (id, name) => post(`/api/games/${id}/submit`, { name });
export const getLeaderboard = () => request("/api/leaderboard?limit=10");
export const getStats = () => request("/api/stats");
