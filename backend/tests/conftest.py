import os
import tempfile
from datetime import datetime, timedelta, timezone

# Must be set BEFORE the app is imported so tests use a throwaway database.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import clock as app_clock  # noqa: E402
from app.challenges import BY_ID  # noqa: E402
from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.ratelimit import limiter  # noqa: E402


class FakeClock:
    def __init__(self):
        self.time = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)

    def __call__(self):
        return self.time

    def advance(self, seconds: float):
        self.time += timedelta(seconds=seconds)


@pytest.fixture(autouse=True)
def _reset_limiter():
    limiter.reset()


@pytest.fixture(autouse=True)
def _clean_database():
    """Every test starts with empty tables."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def clock(monkeypatch):
    fake = FakeClock()
    monkeypatch.setattr(app_clock, "now", fake)
    return fake


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def play(client, clock):
    """Play a whole game and return (game_id, last_answer_response)."""

    def _play(correct=True, rounds=5, language="python", seconds_per_bug=5):
        game = client.post("/api/games", json={"language": language, "rounds": rounds}).json()
        last = None
        for _ in range(game["total"]):
            current = client.post(f"/api/games/{game['game_id']}/next").json()
            bug_line = BY_ID[current["challenge"]["id"]]["bug_line"]
            wrong_line = 1 if bug_line != 1 else 2
            clock.advance(seconds_per_bug)
            last = client.post(
                f"/api/games/{game['game_id']}/answer", json={"line": bug_line if correct else wrong_line}
            ).json()
        return game["game_id"], last

    return _play
