import { useEffect, useState } from "react";
import { getGame, getLeaderboard, submitScore } from "../api";
import Leaderboard from "./Leaderboard.jsx";

const ICON = { correct: "✓", wrong: "✕", timeout: "⏱" };
const OUTCOME_TEXT = { correct: "Found it", wrong: "Missed", timeout: "Timed out" };

export default function Finish({ gameId, onPlayAgain }) {
  const [summary, setSummary] = useState(null);
  const [name, setName] = useState("");
  const [rank, setRank] = useState(null);
  const [board, setBoard] = useState(null);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getGame(gameId).then(setSummary).catch((err) => setError(err.message));
  }, [gameId]);

  useEffect(() => {
    if (summary?.submitted || rank) getLeaderboard().then(setBoard).catch(() => setBoard([]));
  }, [summary?.submitted, rank]);

  async function save(event) {
    event.preventDefault();
    setError("");
    if (!name.trim()) return setError("Enter a name for the leaderboard.");
    setSaving(true);
    try {
      const response = await submitScore(gameId, name);
      setRank(response.rank);
      setSummary((s) => ({ ...s, submitted: true, name: response.name }));
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  if (!summary) {
    return error ? (
      <p className="error" role="alert">
        {error}
      </p>
    ) : (
      <p role="status">Loading your results...</p>
    );
  }

  const accuracy = Math.round((summary.correct / summary.total) * 100);
  return (
    <>
      <section className="card finish" aria-labelledby="finish-heading">
        <h2 id="finish-heading">Game over</h2>
        <p className="final-score">{summary.score}</p>
        <p>
          You found {summary.correct} of {summary.total} bugs ({accuracy}%).
        </p>

        <ol className="breakdown-list">
          {summary.answers.map((a) => (
            <li key={a.number} className={`outcome-${a.outcome}`}>
              <span aria-hidden="true">{ICON[a.outcome]}</span>
              <span className="sr-only">{OUTCOME_TEXT[a.outcome]}: </span>
              <strong>{a.title}</strong>
              <span className="muted"> - {a.category}</span>
              <span className="pts">+{a.points}</span>
            </li>
          ))}
        </ol>

        {!summary.submitted && (
          <form className="submit-form" onSubmit={save}>
            <label htmlFor="player-name">Add your score to the leaderboard</label>
            <div className="row">
              <input
                id="player-name"
                type="text"
                maxLength={20}
                value={name}
                placeholder="Your name"
                onChange={(e) => setName(e.target.value)}
              />
              <button type="submit" className="btn primary" disabled={saving}>
                {saving ? "Saving..." : "Submit score"}
              </button>
            </div>
          </form>
        )}
        {rank && (
          <p className="rank" role="status">
            You are number {rank} on the leaderboard.
          </p>
        )}
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <div className="actions">
          <button type="button" className="btn primary" onClick={onPlayAgain}>
            Play again
          </button>
        </div>
      </section>

      {(summary.submitted || rank) && (
        <section className="card" aria-labelledby="board-heading">
          <h2 id="board-heading">Leaderboard</h2>
          <Leaderboard rows={board} highlightName={summary.name} />
        </section>
      )}
    </>
  );
}
