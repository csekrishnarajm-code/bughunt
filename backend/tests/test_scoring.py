import pytest

from app.scoring import score_answer


def test_instant_correct_answer_gets_full_speed_bonus():
    result = score_answer("easy", 0, True, False)
    assert result == {"outcome": "correct", "base_points": 100, "speed_bonus": 50, "points": 150}


def test_speed_bonus_shrinks_as_time_passes():
    fast = score_answer("medium", 5, True, False)["points"]
    slow = score_answer("medium", 40, True, False)["points"]
    assert fast > slow > 150  # still above the base because it was inside the limit


def test_no_bonus_at_the_time_limit():
    assert score_answer("hard", 45, True, False) == {
        "outcome": "correct", "base_points": 200, "speed_bonus": 0, "points": 200,
    }


def test_hint_reduces_points_by_thirty_percent():
    no_hint = score_answer("hard", 0, True, False)
    hint = score_answer("hard", 0, True, True)
    assert hint["base_points"] == 140 and no_hint["base_points"] == 200
    assert hint["points"] == 210


def test_wrong_line_scores_nothing():
    assert score_answer("easy", 3, False, False)["outcome"] == "wrong"
    assert score_answer("easy", 3, False, False)["points"] == 0


def test_answers_after_the_limit_time_out_even_if_correct():
    assert score_answer("easy", 45 + 1.5, True, False)["outcome"] == "correct"  # inside the grace period
    late = score_answer("easy", 45 + 3, True, False)
    assert late["outcome"] == "timeout" and late["points"] == 0


@pytest.mark.parametrize("difficulty,base", [("easy", 100), ("medium", 150), ("hard", 200)])
def test_base_points_by_difficulty(difficulty, base):
    assert score_answer(difficulty, 45, True, False)["base_points"] == base
