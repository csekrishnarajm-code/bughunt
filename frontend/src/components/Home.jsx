import { useEffect, useState } from "react";
import { getLeaderboard, getStats } from "../api";
import Leaderboard from "./Leaderboard.jsx";

const MODES = [
  ["mixed", "Mixed"],
  ["python", "Python"],
  ["javascript", "JavaScript"],
  ["sql", "SQL"],
];

export default function Home({ onStart, loading, error }) {
  const [language, setLanguage] = useState("mixed");
  const [rounds, setRounds] = useState(5);
  const [board, setBoard] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    getLeaderboard().then(setBoard).catch(() => setBoard([]));
    getStats().then(setStats).catch(() => setStats(null));
  }, []);

  const hardest = stats?.hardest?.[0];
  return (
    <>
      <section className="card hero">
        <h2>Can you spot the bug?</h2>
        <p>
          You get short code snippets in Python, JavaScript and SQL. Each one has exactly one buggy line. Click it
          before the timer runs out, then see why it is wrong and how to fix it.
        </p>

        <form
          className="setup"
          onSubmit={(event) => {
            event.preventDefault();
            onStart(language, rounds);
          }}
        >
          <fieldset>
            <legend>Language</legend>
            {MODES.map(([value, label]) => (
              <label key={value} className={language === value ? "option selected" : "option"}>
                <input type="radio" name="language" value={value} checked={language === value} onChange={() => setLanguage(value)} />
                {label}
              </label>
            ))}
          </fieldset>
          <fieldset>
            <legend>Bugs per game</legend>
            {[5, 8, 10].map((n) => (
              <label key={n} className={rounds === n ? "option selected" : "option"}>
                <input type="radio" name="rounds" value={n} checked={rounds === n} onChange={() => setRounds(n)} />
                {n}
              </label>
            ))}
          </fieldset>
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          <button type="submit" className="btn primary big" disabled={loading}>
            {loading ? "Starting..." : "Start hunting"}
          </button>
        </form>

        <details className="rules">
          <summary>How scoring works</summary>
          <ul>
            <li>Easy bugs are worth 100 points, medium 150 and hard 200.</li>
            <li>Answer fast for a speed bonus of up to 50% extra. You have 45 seconds per bug.</li>
            <li>A hint costs 30% of the points for that bug.</li>
            <li>Wrong answers and timeouts score 0. The server checks every answer, so scores cannot be faked.</li>
            <li>Single-language games have 8 bugs, so 10 bugs is only available in Mixed.</li>
          </ul>
        </details>
      </section>

      <section className="card" aria-labelledby="board-heading">
        <h2 id="board-heading">Leaderboard</h2>
        <Leaderboard rows={board} />
      </section>

      {stats && stats.bugs_attempted > 0 && (
        <p className="hint stats">
          Players have attempted {stats.bugs_attempted} bugs with {stats.accuracy}% found.
          {hardest && ` Hardest so far: ${hardest.category} (${hardest.miss_rate}% missed).`}
        </p>
      )}
    </>
  );
}
