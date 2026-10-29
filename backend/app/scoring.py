"""Scoring is calculated on the server, so the browser cannot change it.

points = base(difficulty) x 0.7 if a hint was used, plus a speed bonus of up to 50% of that.
Wrong answers and timeouts score 0.
"""
from . import config

BASE_POINTS = {"easy": 100, "medium": 150, "hard": 200}
HINT_FACTOR = 0.7
MAX_SPEED_BONUS = 0.5


def score_answer(difficulty: str, elapsed_seconds: float, line_is_correct: bool, hint_used: bool) -> dict:
    timed_out = elapsed_seconds > config.TIME_LIMIT_SECONDS + config.GRACE_SECONDS
    if timed_out:
        return {"outcome": "timeout", "base_points": 0, "speed_bonus": 0, "points": 0}
    if not line_is_correct:
        return {"outcome": "wrong", "base_points": 0, "speed_bonus": 0, "points": 0}

    base = round(BASE_POINTS[difficulty] * (HINT_FACTOR if hint_used else 1.0))
    remaining = 1 - min(max(elapsed_seconds, 0), config.TIME_LIMIT_SECONDS) / config.TIME_LIMIT_SECONDS
    bonus = round(base * MAX_SPEED_BONUS * remaining)
    return {"outcome": "correct", "base_points": base, "speed_bonus": bonus, "points": base + bonus}
