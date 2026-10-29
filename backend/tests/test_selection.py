import random

from app.challenges import BY_ID, DIFFICULTY_ORDER
from app.selection import pick_challenges


def test_challenges_are_ordered_easy_to_hard():
    ids = pick_challenges("mixed", 10, random.Random(1))
    levels = [DIFFICULTY_ORDER[BY_ID[i]["difficulty"]] for i in ids]
    assert levels == sorted(levels)


def test_language_filter_and_size():
    ids = pick_challenges("sql", 5, random.Random(2))
    assert len(ids) == 5 and len(set(ids)) == 5
    assert {BY_ID[i]["language"] for i in ids} == {"sql"}


def test_cannot_ask_for_more_than_exist():
    assert len(pick_challenges("python", 10, random.Random(3))) == 8


def test_same_seed_gives_same_game_and_different_seeds_differ():
    assert pick_challenges("mixed", 8, random.Random(5)) == pick_challenges("mixed", 8, random.Random(5))
    assert pick_challenges("mixed", 8, random.Random(5)) != pick_challenges("mixed", 8, random.Random(6))
