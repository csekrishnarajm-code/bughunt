import { useEffect, useRef } from "react";

const HEADINGS = { correct: "Correct!", wrong: "Not quite", timeout: "Time's up" };

export default function ResultPanel({ result, onNext }) {
  const nextButton = useRef(null);
  useEffect(() => nextButton.current?.focus(), []);

  return (
    <section className={`card result result-${result.outcome}`} aria-live="polite" aria-labelledby="result-heading">
      <h2 id="result-heading">
        {HEADINGS[result.outcome]}
        {result.points > 0 && <span className="points"> +{result.points}</span>}
      </h2>
      {result.outcome === "correct" && (
        <p className="breakdown">
          {result.base_points} base + {result.speed_bonus} speed bonus
        </p>
      )}
      <p>
        <span className="chip">Bug type: {result.category}</span>
      </p>
      <p>{result.explanation}</p>
      <div className="diff" role="group" aria-label="The fix">
        {result.changes.map((change) => (
          <div key={change.line}>
            <pre className="diff-removed">
              <span aria-hidden="true">- </span>
              <span className="sr-only">Remove line {change.line}: </span>
              {change.before}
            </pre>
            {change.after.length === 0 ? (
              <pre className="diff-note">(line removed)</pre>
            ) : (
              change.after.map((text, i) => (
                <pre key={i} className="diff-added">
                  <span aria-hidden="true">+ </span>
                  <span className="sr-only">Add: </span>
                  {text}
                </pre>
              ))
            )}
          </div>
        ))}
      </div>
      <button ref={nextButton} type="button" className="btn primary" onClick={onNext}>
        {result.finished ? "See my results" : "Next bug"}
      </button>
    </section>
  );
}
