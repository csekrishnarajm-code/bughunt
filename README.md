# BugHunt

BugHunt is a spot-the-bug game. You get a short snippet of Python, JavaScript or SQL with exactly one buggy line, and you have 45 seconds to click it. After each answer you see why the line is wrong and how to fix it. Scores go on a public leaderboard.

**Live demo (free hosting, the first request can take up to a minute to wake up):** https://bughunt-dxo6.onrender.com/

## Why I built this

Interviews and code reviews are full of one skill that tutorials rarely train: reading code and noticing what is wrong with it. I wanted a project that practises exactly that, and one that anyone can try in 30 seconds without signing up. It also let me build a complete React and FastAPI application with a real game loop: a timer, scoring, a leaderboard and state that survives a page refresh.

## How it plays

1. Pick a language (or Mixed) and the number of bugs.
2. Read the snippet and click the line you think has the bug. The timer is 45 seconds per bug.
3. See whether you were right, how many points you earned, the type of bug, an explanation and the exact fix.
4. At the end, add your name to the leaderboard.

Scoring: easy bugs are worth 100 points, medium 150 and hard 200. Answering quickly adds up to 50% extra. A hint costs 30% of the points for that bug. Wrong answers and timeouts score 0.

## Features

- 24 hand-written bugs across Python, JavaScript and SQL, each tagged easy, medium or hard
- Syntax highlighting written from scratch, with no library
- Keyboard support: arrow keys move between lines, Enter selects, and focus moves to "Next bug" after each answer
- Light and dark theme that follows your system setting, and reduced-motion support
- Hints, a server-side timer, and a game that you can resume after refreshing the page
- Leaderboard and simple statistics, such as which bug types players miss most

## Tech stack

- **Frontend:** React (Vite), plain CSS
- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** PostgreSQL (SQLite for local development and tests)
- **Testing:** pytest (108 tests) and Vitest with Testing Library (23 tests)
- **DevOps:** Docker (multi-stage build), Docker Compose, GitHub Actions, deployed on Render with Neon

## Run it on your machine

With Docker:

```bash
cp .env.example .env      # set POSTGRES_PASSWORD
docker compose up --build
```

Open http://localhost:8000.

Without Docker (two terminals):

```bash
# Terminal 1: API on port 8000 (uses a local SQLite file)
cd backend
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2: React dev server on port 5173
cd frontend
npm install
npm run dev
```

## API

| Method | Endpoint | What it does |
|---|---|---|
| POST | `/api/games` | start a game: `{"language": "mixed", "rounds": 5}` |
| POST | `/api/games/{id}/next` | start the next bug and its timer (calling it again returns the same bug) |
| POST | `/api/games/{id}/hint` | get a hint for the current bug |
| POST | `/api/games/{id}/answer` | `{"line": 2}`, or `{"line": null}` for a timeout. Returns the result, explanation and fix |
| GET | `/api/games/{id}` | summary of a game |
| POST | `/api/games/{id}/submit` | add a finished game to the leaderboard |
| GET | `/api/leaderboard` | top scores |
| GET | `/api/stats` | accuracy and the most-missed bug types |

Swagger docs are at `/docs`.

## Decisions I made

- **The server owns the answers and the scores.** The browser only receives the code lines. The bug line, category, explanation and fix are sent after the player has answered, never before. Points are calculated on the server, so a modified browser cannot change a score.
- **The timer runs on the server too.** The browser shows a countdown, but the server records when each bug was served and measures the time itself. A late answer scores zero even if the line is right.
- **Every bug has exactly one defensible buggy line.** I dropped ideas where two lines could be argued, such as removing items from a list while looping over it, because players would feel the game was unfair.
- **Every challenge is verified by running it.** The tests execute the buggy and the fixed code in Python, Node.js and SQLite, and check that the fixed version works and the buggy one does not. An explanation that does not match real behaviour fails the build.
- **A small custom syntax highlighter** instead of a library, to keep the bundle small and to show the JavaScript behind it.
- **One deployable service.** FastAPI also serves the built React app, so the whole project is a single Docker container.

## Tests

```bash
cd backend  && pytest -q       # 108 tests
cd frontend && npm test        # 23 tests
```

The backend tests cover scoring, game rules (no double answers, timeouts, rate limit, validation), that the answer is never leaked before answering, the leaderboard and statistics, and all 24 challenges. The frontend tests cover the highlighter, keyboard use of the code viewer, the timer, and a full game from the setup screen to the leaderboard, including errors and resuming after a refresh.

## Problems found while testing

- **Tests shared one database,** so games from one test leaked into the leaderboard and statistics checks of another. Each test now starts with empty tables.
- **A hint test compared different random challenges,** so it proved little. It now fixes the challenge, so the expected points are exact.

## Limitations

- Only 24 challenges, so regular players will see repeats
- Names on the leaderboard are not moderated
- No accounts, so anyone can submit under any name
- The rate limiter keeps its counts in memory, which is fine for one server but not for several
- The code is never executed in the game itself. The explanations come from the checked challenge data

## What I would add next

- Load challenges from a JSON file and add many more
- A daily challenge and streaks
- Accounts and personal statistics
- A mode where you also write the fix
- Alembic migrations instead of creating the tables on start

## Project structure

```
bughunt/
├── backend/
│   ├── app/            main.py, challenges.py, scoring.py, selection.py, models.py, db.py, ratelimit.py
│   ├── tests/          API tests and the challenge verification (Python, Node.js, SQLite)
│   └── requirements.txt
├── frontend/
│   └── src/            App.jsx, components/, highlight.js, api.js, tests
├── docs/DEPLOY.md
├── Dockerfile          builds the frontend, then the API that serves it
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## About me

Krishnaraj M, fresher Full Stack Developer from Hosur, Tamil Nadu.
[LinkedIn](https://www.linkedin.com/in/krishnaraj-m-2a4585371/) | [GitHub](https://github.com/csekrishnarajm-code) | csekrishnarajm@gmail.com
