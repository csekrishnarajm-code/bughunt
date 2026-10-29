import random

from .challenges import CHALLENGES, DIFFICULTY_ORDER


def pick_challenges(language: str, rounds: int, rng: random.Random | None = None) -> list[str]:
    """Random challenges for one game, ordered from easy to hard."""
    rng = rng or random.Random()
    pool = [c for c in CHALLENGES if language == "mixed" or c["language"] == language]
    chosen = rng.sample(pool, min(rounds, len(pool)))
    # shuffle first so equal difficulties come in random order, then sort (stable) by difficulty
    chosen.sort(key=lambda c: DIFFICULTY_ORDER[c["difficulty"]])
    return [c["id"] for c in chosen]
