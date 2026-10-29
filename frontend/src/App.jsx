import { useEffect, useState } from "react";
import { createGame, getGame } from "./api";
import Finish from "./components/Finish.jsx";
import Home from "./components/Home.jsx";
import Play from "./components/Play.jsx";

const STORAGE_KEY = "bughunt-game";

function remember(id) {
  try {
    if (id) sessionStorage.setItem(STORAGE_KEY, id);
    else sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    /* storage can be unavailable; the game still works */
  }
}

export default function App() {
  const [screen, setScreen] = useState("home"); // home | play | finish
  const [gameId, setGameId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Pick up an unfinished game after a page refresh.
  useEffect(() => {
    let saved = null;
    try {
      saved = sessionStorage.getItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
    if (!saved) return;
    getGame(saved)
      .then((game) => {
        setGameId(saved);
        setScreen(game.finished ? "finish" : "play");
      })
      .catch(() => remember(null));
  }, []);

  async function start(language, rounds) {
    setLoading(true);
    setError("");
    try {
      const game = await createGame(language, rounds);
      remember(game.game_id);
      setGameId(game.game_id);
      setScreen("play");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function playAgain() {
    remember(null);
    setGameId(null);
    setScreen("home");
  }

  return (
    <div className="app">
      <header className="site-header">
        <div className="container header-inner">
          <button type="button" className="brand" onClick={playAgain} aria-label="BugHunt home">
            <span aria-hidden="true">🐛</span> BugHunt
          </button>
          <p className="tagline">Spot the bug. Learn why.</p>
        </div>
      </header>

      <main className="container">
        {screen === "home" && <Home onStart={start} loading={loading} error={error} />}
        {screen === "play" && <Play key={gameId} gameId={gameId} onFinished={() => setScreen("finish")} />}
        {screen === "finish" && <Finish gameId={gameId} onPlayAgain={playAgain} />}
      </main>

      <footer className="site-footer container">
        <p>No sign-up needed. The server keeps the answers secret and calculates every score.</p>
      </footer>
    </div>
  );
}
