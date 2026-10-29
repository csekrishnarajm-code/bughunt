import re
import secrets
from contextlib import asynccontextmanager
from datetime import timezone
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from . import clock, config
from .challenges import BY_ID, changes_view, lines_of, public_view
from .db import Base, engine, get_db
from .models import Answer, Game
from .ratelimit import rate_limit
from .schemas import AnswerIn, NewGame, SubmitIn
from .scoring import score_answer
from .selection import pick_challenges


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # creates the tables on first start
    yield


app = FastAPI(
    title="BugHunt API",
    description="A spot-the-bug game. The server picks the challenges, keeps the answers secret and "
    "calculates every score.",
    version="1.0.0",
    lifespan=lifespan,
)


# ------------------------------------------------------------------- helpers
def _aware(moment):
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def _get_game(db: Session, game_id: str) -> Game:
    game = db.get(Game, game_id)
    if game is None:
        raise HTTPException(404, "Game not found.")
    return game


def _current_challenge(game: Game) -> dict:
    return BY_ID[game.challenge_ids[game.position]]


def _summary(game: Game) -> dict:
    return {
        "game_id": game.id,
        "language": game.language,
        "total": game.total,
        "answered": game.position,
        "score": game.score,
        "correct": game.correct,
        "finished": game.finished,
        "submitted": game.name is not None,
        "name": game.name,
        "answers": [
            {
                "number": index,
                "title": BY_ID[a.challenge_id]["title"],
                "language": a.language,
                "difficulty": a.difficulty,
                "category": a.category,
                "outcome": a.outcome,
                "points": a.points,
            }
            for index, a in enumerate(game.answers, start=1)
        ],
    }


# ----------------------------------------------------------------- endpoints
@app.get("/api/health", tags=["system"])
def health():
    return {"status": "ok"}


@app.post("/api/games", tags=["game"], dependencies=[Depends(rate_limit)])
def create_game(body: NewGame, db: Session = Depends(get_db)):
    ids = pick_challenges(body.language, body.rounds)
    game = Game(id=secrets.token_urlsafe(9), language=body.language, total=len(ids), challenge_ids=ids)
    db.add(game)
    db.commit()
    return {"game_id": game.id, "language": game.language, "total": game.total}


@app.post("/api/games/{game_id}/next", tags=["game"])
def next_challenge(game_id: str, db: Session = Depends(get_db)):
    """Start the next challenge. Calling it again before answering returns the same one."""
    game = _get_game(db, game_id)
    if game.finished:
        raise HTTPException(409, "This game is finished.")
    if game.question_started_at is None:
        game.question_started_at = clock.now()
        game.hint_used = False
        db.commit()
    elapsed = (clock.now() - _aware(game.question_started_at)).total_seconds()
    return {
        "number": game.position + 1,
        "total": game.total,
        "time_limit": config.TIME_LIMIT_SECONDS,
        "remaining_seconds": max(0.0, round(config.TIME_LIMIT_SECONDS - elapsed, 1)),
        "hint_used": game.hint_used,
        "score": game.score,
        "challenge": public_view(_current_challenge(game)),
    }


@app.post("/api/games/{game_id}/hint", tags=["game"])
def get_hint(game_id: str, db: Session = Depends(get_db)):
    """A hint makes the bug worth 30% fewer points."""
    game = _get_game(db, game_id)
    if game.finished or game.question_started_at is None:
        raise HTTPException(409, "There is no active challenge.")
    game.hint_used = True
    db.commit()
    return {"hint": _current_challenge(game)["hint"], "hint_used": True}


@app.post("/api/games/{game_id}/answer", tags=["game"])
def answer(game_id: str, body: AnswerIn, db: Session = Depends(get_db)):
    game = _get_game(db, game_id)
    if game.finished:
        raise HTTPException(409, "This game is finished.")
    if game.question_started_at is None:
        raise HTTPException(409, "Request the next challenge first.")

    challenge = _current_challenge(game)
    if body.line is not None and not 1 <= body.line <= len(lines_of(challenge)):
        raise HTTPException(422, "That line does not exist.")

    elapsed = (clock.now() - _aware(game.question_started_at)).total_seconds()
    result = score_answer(
        challenge["difficulty"],
        elapsed,
        line_is_correct=body.line == challenge["bug_line"],
        hint_used=game.hint_used,
    )
    if body.line is None and result["outcome"] != "timeout":
        result = {"outcome": "timeout", "base_points": 0, "speed_bonus": 0, "points": 0}

    db.add(
        Answer(
            game_id=game.id,
            challenge_id=challenge["id"],
            language=challenge["language"],
            difficulty=challenge["difficulty"],
            category=challenge["category"],
            outcome=result["outcome"],
            points=result["points"],
            time_ms=int(elapsed * 1000),
            hint_used=game.hint_used,
            line=body.line,
        )
    )
    game.score += result["points"]
    game.correct += 1 if result["outcome"] == "correct" else 0
    game.position += 1
    game.question_started_at = None
    game.hint_used = False
    db.commit()
    db.refresh(game)

    return {
        **result,
        "bug_line": challenge["bug_line"],
        "category": challenge["category"],
        "explanation": challenge["explanation"],
        "changes": changes_view(challenge),
        "number": game.position,
        "total": game.total,
        "score": game.score,
        "correct_count": game.correct,
        "finished": game.finished,
    }


@app.get("/api/games/{game_id}", tags=["game"])
def game_summary(game_id: str, db: Session = Depends(get_db)):
    return _summary(_get_game(db, game_id))


@app.post("/api/games/{game_id}/submit", tags=["leaderboard"])
def submit_score(game_id: str, body: SubmitIn, db: Session = Depends(get_db)):
    game = _get_game(db, game_id)
    if not game.finished:
        raise HTTPException(409, "Finish the game before submitting your score.")
    if game.name is not None:
        raise HTTPException(409, "This score was already submitted.")
    name = " ".join(body.name.split())
    if not re.match(config.NAME_PATTERN, name):
        raise HTTPException(422, "Use 1 to 20 letters, numbers, spaces, dots, dashes or underscores.")

    game.name = name
    game.submitted_at = clock.now()
    db.commit()
    better = db.scalar(
        select(func.count(Game.id)).where(
            Game.name.is_not(None),
            (Game.score > game.score)
            | ((Game.score == game.score) & (Game.submitted_at < game.submitted_at)),
        )
    )
    return {"name": name, "score": game.score, "rank": (better or 0) + 1}


@app.get("/api/leaderboard", tags=["leaderboard"])
def leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    limit = max(1, min(limit, config.LEADERBOARD_MAX))
    rows = db.scalars(
        select(Game)
        .where(Game.name.is_not(None))
        .order_by(Game.score.desc(), Game.submitted_at.asc())
        .limit(limit)
    ).all()
    return [
        {"rank": rank, "name": g.name, "score": g.score, "correct": g.correct, "total": g.total, "language": g.language}
        for rank, g in enumerate(rows, start=1)
    ]


@app.get("/api/stats", tags=["leaderboard"])
def stats(db: Session = Depends(get_db)):
    attempts = db.scalar(select(func.count(Answer.id))) or 0
    solved = db.scalar(select(func.count(Answer.id)).where(Answer.outcome == "correct")) or 0
    games = db.scalar(select(func.count(Game.id)).where(Game.position >= Game.total)) or 0
    per_category = db.execute(
        select(
            Answer.category,
            Answer.language,
            func.count(Answer.id).label("attempts"),
            func.sum(case((Answer.outcome == "correct", 1), else_=0)).label("solved"),
        )
        .group_by(Answer.category, Answer.language)
        .having(func.count(Answer.id) >= 3)
    ).all()
    hardest = sorted(
        (
            {
                "category": r.category,
                "language": r.language,
                "attempts": r.attempts,
                "miss_rate": round(100 - (r.solved or 0) / r.attempts * 100),
            }
            for r in per_category
        ),
        key=lambda item: (-item["miss_rate"], -item["attempts"]),
    )[:5]
    return {
        "games_played": games,
        "bugs_attempted": attempts,
        "accuracy": round(solved / attempts * 100) if attempts else 0,
        "hardest": hardest,
    }


# Serve the built React app (present in Docker; absent during API-only development).
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")
