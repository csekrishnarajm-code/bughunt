import json

from app import config
from app.challenges import BY_ID


def new_game(client, **body):
    body = {"language": "python", "rounds": 5, **body}
    return client.post("/api/games", json=body).json()


def next_challenge(client, game_id):
    return client.post(f"/api/games/{game_id}/next").json()


def bug_line_of(challenge_id):
    return BY_ID[challenge_id]["bug_line"]


# --------------------------------------------------------------------- basics
def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_create_game_validates_input(client):
    assert client.post("/api/games", json={"language": "cobol", "rounds": 5}).status_code == 422
    assert client.post("/api/games", json={"language": "sql", "rounds": 2}).status_code == 422
    assert client.post("/api/games", json={"language": "sql", "rounds": 11}).status_code == 422
    game = new_game(client, language="sql", rounds=10)
    assert game["total"] == 8  # only 8 SQL challenges exist


def test_unknown_game_is_404(client):
    assert client.post("/api/games/nope/next").status_code == 404
    assert client.get("/api/games/nope").status_code == 404


# ------------------------------------------------------ the answer stays secret
def test_next_challenge_never_reveals_the_answer(client):
    game = new_game(client)
    data = next_challenge(client, game["game_id"])
    assert data["number"] == 1 and data["total"] == 5 and data["time_limit"] == config.TIME_LIMIT_SECONDS
    assert set(data["challenge"]) == {"id", "language", "difficulty", "title", "context", "lines"}
    secret = BY_ID[data["challenge"]["id"]]
    text = json.dumps(data).lower()
    assert secret["category"].lower() not in text
    assert secret["explanation"][:30].lower() not in text
    assert "bug_line" not in text


def test_summary_and_hint_do_not_leak_the_answer(client):
    game = new_game(client)
    current = next_challenge(client, game["game_id"])
    summary = client.get(f"/api/games/{game['game_id']}").json()
    assert summary["answers"] == [] and summary["answered"] == 0
    hint = client.post(f"/api/games/{game['game_id']}/hint").json()
    assert hint["hint"] == BY_ID[current["challenge"]["id"]]["hint"]
    assert "category" not in hint and "bug_line" not in hint


def test_next_is_repeatable_and_keeps_the_same_timer(client, clock):
    game = new_game(client)
    first = next_challenge(client, game["game_id"])
    clock.advance(10)
    again = next_challenge(client, game["game_id"])
    assert again["challenge"]["id"] == first["challenge"]["id"]
    assert first["remaining_seconds"] == 45 and again["remaining_seconds"] == 35


# ------------------------------------------------------------------ answering
def test_correct_answer_scores_and_explains(client, clock):
    game = new_game(client)
    current = next_challenge(client, game["game_id"])
    secret = BY_ID[current["challenge"]["id"]]
    clock.advance(9)
    result = client.post(f"/api/games/{game['game_id']}/answer", json={"line": secret["bug_line"]}).json()
    assert result["outcome"] == "correct"
    assert result["base_points"] > 0 and result["speed_bonus"] > 0
    assert result["points"] == result["base_points"] + result["speed_bonus"] == result["score"]
    assert result["category"] == secret["category"]
    assert result["explanation"] == secret["explanation"]
    assert result["bug_line"] == secret["bug_line"]
    assert result["changes"] and result["number"] == 1 and result["finished"] is False


def test_wrong_answer_scores_nothing_but_still_explains(client, clock):
    game = new_game(client)
    current = next_challenge(client, game["game_id"])
    secret = BY_ID[current["challenge"]["id"]]
    wrong = 1 if secret["bug_line"] != 1 else 2
    result = client.post(f"/api/games/{game['game_id']}/answer", json={"line": wrong}).json()
    assert result["outcome"] == "wrong" and result["points"] == 0
    assert result["explanation"] == secret["explanation"]


def test_hint_lowers_the_points(client, clock, monkeypatch):
    import app.main

    monkeypatch.setattr(app.main, "pick_challenges", lambda language, rounds: ["js-nan-equality"])  # easy: 100 base
    points = {}
    for use_hint in (False, True):
        game = client.post("/api/games", json={"language": "javascript", "rounds": 3}).json()
        next_challenge(client, game["game_id"])
        if use_hint:
            client.post(f"/api/games/{game['game_id']}/hint")
        result = client.post(f"/api/games/{game['game_id']}/answer", json={"line": 2}).json()
        points[use_hint] = (result["base_points"], result["speed_bonus"], result["points"])
    assert points[False] == (100, 50, 150)
    assert points[True] == (70, 35, 105)


def test_running_out_of_time_scores_nothing(client, clock):
    game = new_game(client)
    current = next_challenge(client, game["game_id"])
    line = bug_line_of(current["challenge"]["id"])
    clock.advance(60)
    late = client.post(f"/api/games/{game['game_id']}/answer", json={"line": line}).json()
    assert late["outcome"] == "timeout" and late["points"] == 0

    current = next_challenge(client, game["game_id"])
    skipped = client.post(f"/api/games/{game['game_id']}/answer", json={"line": None}).json()
    assert skipped["outcome"] == "timeout"


def test_answer_rules(client):
    game = new_game(client)
    gid = game["game_id"]
    # cannot answer before the challenge was served
    assert client.post(f"/api/games/{gid}/answer", json={"line": 1}).status_code == 409
    next_challenge(client, gid)
    # a line that does not exist
    assert client.post(f"/api/games/{gid}/answer", json={"line": 99}).status_code == 422
    assert client.post(f"/api/games/{gid}/answer", json={"line": 0}).status_code == 422
    # cannot answer the same challenge twice
    assert client.post(f"/api/games/{gid}/answer", json={"line": 1}).status_code == 200
    assert client.post(f"/api/games/{gid}/answer", json={"line": 1}).status_code == 409


def test_a_game_ends_after_its_last_challenge(client, play):
    gid, last = play(correct=True, rounds=3)
    assert last["finished"] is True and last["number"] == 3
    assert client.post(f"/api/games/{gid}/next").status_code == 409
    assert client.post(f"/api/games/{gid}/hint").status_code == 409
    summary = client.get(f"/api/games/{gid}").json()
    assert summary["finished"] is True and summary["correct"] == 3
    assert [a["outcome"] for a in summary["answers"]] == ["correct"] * 3
    assert summary["score"] == sum(a["points"] for a in summary["answers"])


# ---------------------------------------------------------------- leaderboard
def test_submit_score_and_rank(client, play):
    perfect, _ = play(correct=True, rounds=5)
    poor, _ = play(correct=False, rounds=5)

    first = client.post(f"/api/games/{perfect}/submit", json={"name": "  Krishna   M "}).json()
    second = client.post(f"/api/games/{poor}/submit", json={"name": "Zero"}).json()
    assert first["name"] == "Krishna M" and first["rank"] == 1
    assert second["rank"] == 2 and second["score"] == 0

    board = client.get("/api/leaderboard").json()
    assert [row["name"] for row in board] == ["Krishna M", "Zero"]
    assert board[0]["rank"] == 1 and board[0]["correct"] == 5 and board[0]["total"] == 5


def test_submit_rules(client, play, clock):
    unfinished = new_game(client)["game_id"]
    next_challenge(client, unfinished)
    assert client.post(f"/api/games/{unfinished}/submit", json={"name": "Ann"}).status_code == 409

    done, _ = play(rounds=3)
    for bad in ["", "   ", "x" * 21, "<script>", "bad/name"]:
        assert client.post(f"/api/games/{done}/submit", json={"name": bad}).status_code == 422, bad
    assert client.post(f"/api/games/{done}/submit", json={"name": "Ann"}).status_code == 200
    assert client.post(f"/api/games/{done}/submit", json={"name": "Ann"}).status_code == 409


def test_unsubmitted_games_are_not_on_the_leaderboard(client, play):
    play(rounds=3)
    assert client.get("/api/leaderboard").json() == []


# ---------------------------------------------------------------------- stats
def test_stats_report_accuracy_and_hardest_bugs(client, play):
    assert client.get("/api/stats").json() == {"games_played": 0, "bugs_attempted": 0, "accuracy": 0, "hardest": []}
    for _ in range(3):
        play(correct=False, rounds=8)
    stats = client.get("/api/stats").json()
    assert stats["games_played"] == 3 and stats["bugs_attempted"] == 24 and stats["accuracy"] == 0
    assert len(stats["hardest"]) == 5
    assert all(item["miss_rate"] == 100 and item["attempts"] == 3 for item in stats["hardest"])


# ----------------------------------------------------------------- rate limit
def test_starting_too_many_games_is_limited(client, monkeypatch):
    monkeypatch.setattr(config, "RATE_LIMIT_PER_MIN", 2)
    codes = [client.post("/api/games", json={"language": "sql", "rounds": 3}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]
