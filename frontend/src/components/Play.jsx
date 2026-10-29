import { useCallback, useEffect, useRef, useState } from "react";
import { getHint, nextChallenge, sendAnswer } from "../api";
import CodeViewer from "./CodeViewer.jsx";
import ResultPanel from "./ResultPanel.jsx";
import Timer from "./Timer.jsx";

const LANGUAGE_LABEL = { python: "Python", javascript: "JavaScript", sql: "SQL" };

export default function Play({ gameId, onFinished }) {
  const [phase, setPhase] = useState("loading"); // loading | answering | revealed
  const [data, setData] = useState(null);
  const [result, setResult] = useState(null);
  const [chosen, setChosen] = useState(null);
  const [hint, setHint] = useState(null);
  const [error, setError] = useState("");
  const busy = useRef(false);

  const load = useCallback(async () => {
    setError("");
    setHint(null);
    setResult(null);
    setChosen(null);
    setPhase("loading");
    try {
      const next = await nextChallenge(gameId);
      setData(next);
      setPhase("answering");
      if (next.hint_used) setHint((await getHint(gameId)).hint); // restore after a page refresh
    } catch (err) {
      setError(err.message);
    }
  }, [gameId]);

  useEffect(() => {
    load();
  }, [load]);

  async function submit(line) {
    if (busy.current || phase !== "answering") return;
    busy.current = true;
    try {
      setChosen(line);
      setResult(await sendAnswer(gameId, line));
      setPhase("revealed");
    } catch (err) {
      setError(err.message);
    } finally {
      busy.current = false;
    }
  }
  const submitRef = useRef(submit);
  submitRef.current = submit;

  async function askHint() {
    try {
      const response = await getHint(gameId);
      setHint(response.hint);
    } catch (err) {
      setError(err.message);
    }
  }

  if (error && !data) {
    return (
      <div className="card">
        <p className="error" role="alert">
          {error}
        </p>
        <button type="button" className="btn" onClick={load}>
          Try again
        </button>
      </div>
    );
  }
  if (!data || phase === "loading") return <p role="status">Loading the next bug...</p>;

  const { challenge } = data;
  const answered = phase === "revealed";
  return (
    <div className="play">
      <div className="play-bar">
        <span>
          Bug {data.number} of {data.total}
        </span>
        <span className={`badge badge-${challenge.difficulty}`}>{challenge.difficulty}</span>
        <span className="badge">{LANGUAGE_LABEL[challenge.language]}</span>
        <span className="score" aria-label="Score">
          Score: {answered ? result.score : data.score}
        </span>
      </div>

      <Timer
        seconds={data.remaining_seconds}
        limit={data.time_limit}
        running={phase === "answering"}
        resetKey={data.number}
        onExpire={() => submitRef.current(null)}
      />

      <section className="card">
        <h2>{challenge.title}</h2>
        {challenge.context && <pre className="context">{challenge.context}</pre>}
        <p className="instruction">One line has a bug. Click it.</p>
        <CodeViewer
          lines={challenge.lines}
          language={challenge.language}
          disabled={answered}
          onSelect={submit}
          bugLine={answered ? result.bug_line : null}
          chosenLine={answered ? chosen : null}
        />
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        {!answered && (
          <div className="actions">
            <button type="button" className="btn" onClick={askHint} disabled={hint !== null}>
              {hint ? "Hint used" : "Show a hint (-30% points)"}
            </button>
          </div>
        )}
        {hint && <p className="hint-box">Hint: {hint}</p>}
      </section>

      {answered && <ResultPanel result={result} onNext={() => (result.finished ? onFinished() : load())} />}
    </div>
  );
}
