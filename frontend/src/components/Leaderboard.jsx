const LANGUAGE_LABEL = { mixed: "Mixed", python: "Python", javascript: "JavaScript", sql: "SQL" };

export default function Leaderboard({ rows, highlightName }) {
  if (rows === null) return <p className="hint">Loading scores...</p>;
  if (rows.length === 0) return <p className="hint">No scores yet. Be the first on the board!</p>;
  return (
    <table className="board">
      <caption className="sr-only">Top players</caption>
      <thead>
        <tr>
          <th scope="col">#</th>
          <th scope="col">Player</th>
          <th scope="col">Mode</th>
          <th scope="col">Found</th>
          <th scope="col">Score</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.rank} className={row.name === highlightName ? "me" : undefined}>
            <td>{row.rank}</td>
            <td>{row.name}</td>
            <td>{LANGUAGE_LABEL[row.language]}</td>
            <td>
              {row.correct}/{row.total}
            </td>
            <td>{row.score}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
