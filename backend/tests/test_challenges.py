import shutil

import pytest

from app.challenges import BY_ID, CHALLENGES, LANGUAGES, apply_patch, changes_view, lines_of, public_view

from .challenge_checks import CHECKS, JS_FETCH_SETUP
from .harness import norm, run_js, run_python, run_sql

NODE = shutil.which("node")


# ------------------------------------------------------------------ structure
def test_ids_are_unique_and_every_challenge_has_checks():
    ids = [c["id"] for c in CHALLENGES]
    assert len(ids) == len(set(ids))
    assert set(ids) == set(CHECKS), "every challenge needs an entry in tests/challenge_checks.py"


def test_enough_challenges_per_language_and_difficulty():
    for language in LANGUAGES:
        mine = [c for c in CHALLENGES if c["language"] == language]
        assert len(mine) >= 8
        assert {c["difficulty"] for c in mine} == {"easy", "medium", "hard"}


@pytest.mark.parametrize("challenge", CHALLENGES, ids=lambda c: c["id"])
def test_challenge_is_well_formed(challenge):
    lines = lines_of(challenge)
    assert 2 <= len(lines) <= 14
    assert challenge["bug_line"] in challenge["patch"]
    assert 1 <= challenge["bug_line"] <= len(lines)
    assert all(1 <= n <= len(lines) for n in challenge["patch"])
    assert apply_patch(challenge) != challenge["code"]
    assert challenge["explanation"].endswith(".") and len(challenge["explanation"]) > 40
    assert challenge["hint"][-1] in ".?"
    # the hint and title must not give the answer away
    assert challenge["category"].lower() not in (challenge["hint"] + challenge["title"]).lower()


@pytest.mark.parametrize("challenge", CHALLENGES, ids=lambda c: c["id"])
def test_public_view_hides_the_answer(challenge):
    shown = public_view(challenge)
    assert set(shown) == {"id", "language", "difficulty", "title", "context", "lines"}
    text = str(shown).lower()
    assert challenge["category"].lower() not in text
    assert challenge["explanation"][:30].lower() not in text


def test_changes_view_describes_the_fix():
    changes = changes_view(BY_ID["sql-where-aggregate"])
    assert changes[0] == {"line": 3, "before": "WHERE COUNT(*) > 2", "after": []}
    assert changes[1]["after"] == ["GROUP BY customer_id", "HAVING COUNT(*) > 2;"]


# ------------------------------------------------------------------ behaviour
def _python_cases():
    return [c for c in CHALLENGES if c["language"] == "python"]


def _js_cases():
    return [c for c in CHALLENGES if c["language"] == "javascript"]


def _sql_cases():
    return [c for c in CHALLENGES if c["language"] == "sql"]


@pytest.mark.parametrize("challenge", _python_cases(), ids=lambda c: c["id"])
def test_python_fixed_code_works_and_buggy_code_does_not(challenge):
    checks = CHECKS[challenge["id"]]["checks"]
    expected = [norm(e) for _, e in checks]
    assert run_python(apply_patch(challenge), checks) == expected
    assert run_python(challenge["code"], checks) != expected


@pytest.mark.skipif(NODE is None, reason="Node.js is not installed")
@pytest.mark.parametrize("challenge", _js_cases(), ids=lambda c: c["id"])
def test_javascript_fixed_code_works_and_buggy_code_does_not(challenge):
    spec = CHECKS[challenge["id"]]
    checks, setup = spec["checks"], spec.get("setup", "")
    expected = [norm(e) for _, e in checks]
    assert run_js(apply_patch(challenge), checks, setup) == expected
    assert run_js(challenge["code"], checks, setup) != expected


@pytest.mark.parametrize("challenge", _sql_cases(), ids=lambda c: c["id"])
def test_sql_fixed_query_works_and_buggy_query_does_not(challenge):
    spec = CHECKS[challenge["id"]]
    after = spec.get("after")
    assert run_sql(apply_patch(challenge), after) == spec["expected"]
    assert run_sql(challenge["code"], after) != spec["expected"]
