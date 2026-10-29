import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App.jsx";

const FIRST = {
  number: 1, total: 2, time_limit: 45, remaining_seconds: 45, hint_used: false, score: 0,
  challenge: {
    id: "py-ignored-return", language: "python", difficulty: "easy", title: "Clean the name", context: null,
    lines: ["def clean(name):", "    name.strip()", "    return name.title()"],
  },
};
const SECOND = {
  number: 2, total: 2, time_limit: 45, remaining_seconds: 45, hint_used: false, score: 150,
  challenge: {
    id: "py-is-equals", language: "python", difficulty: "medium", title: "Admin check", context: null,
    lines: ["def is_admin(user):", '    return user["role"] is "admin"'],
  },
};
const CORRECT = {
  outcome: "correct", base_points: 100, speed_bonus: 50, points: 150, bug_line: 2,
  category: "Ignored return value",
  explanation: "Strings cannot be changed in place, so the result of strip() must be assigned.",
  changes: [{ line: 2, before: "    name.strip()", after: ["    name = name.strip()"] }],
  number: 1, total: 2, score: 150, correct_count: 1, finished: false,
};
const WRONG_LAST = {
  outcome: "wrong", base_points: 0, speed_bonus: 0, points: 0, bug_line: 2, category: "Identity vs equality",
  explanation: "The is operator compares objects, not values.",
  changes: [{ line: 2, before: '    return user["role"] is "admin"', after: ['    return user["role"] == "admin"'] }],
  number: 2, total: 2, score: 150, correct_count: 1, finished: true,
};
const SUMMARY = {
  game_id: "g1", language: "python", total: 2, answered: 2, score: 150, correct: 1, finished: true,
  submitted: false, name: null,
  answers: [
    { number: 1, title: "Clean the name", language: "python", difficulty: "easy", category: "Ignored return value", outcome: "correct", points: 150 },
    { number: 2, title: "Admin check", language: "python", difficulty: "medium", category: "Identity vs equality", outcome: "wrong", points: 0 },
  ],
};
const BOARD = [{ rank: 1, name: "Ada", score: 900, correct: 5, total: 5, language: "python" }];
const STATS = {
  games_played: 3, bugs_attempted: 40, accuracy: 62,
  hardest: [{ category: "Shallow copy", language: "python", attempts: 5, miss_rate: 80 }],
};

function mockApi(overrides = {}) {
  const calls = [];
  const queues = { next: [FIRST, SECOND], answer: [CORRECT, WRONG_LAST] };
  const handlers = {
    "GET /api/leaderboard?limit=10": () => BOARD,
    "GET /api/stats": () => STATS,
    "POST /api/games": () => ({ game_id: "g1", language: "python", total: 2 }),
    "POST /api/games/g1/next": () => queues.next.shift(),
    "POST /api/games/g1/hint": () => ({ hint: "Look at what strip() returns.", hint_used: true }),
    "POST /api/games/g1/answer": () => queues.answer.shift(),
    "GET /api/games/g1": () => SUMMARY,
    "POST /api/games/g1/submit": () => ({ name: "Krish", score: 150, rank: 2 }),
    ...overrides,
  };
  globalThis.fetch = vi.fn(async (url, options = {}) => {
    const key = `${options.method || "GET"} ${url}`;
    const body = options.body ? JSON.parse(options.body) : undefined;
    calls.push({ key, body });
    if (!handlers[key]) throw new Error(`Unexpected request: ${key}`);
    const data = handlers[key](body);
    if (data && data.__status) return { ok: false, status: data.__status, json: async () => ({ detail: data.detail }) };
    return { ok: true, status: 200, json: async () => data };
  });
  return calls;
}

async function startGame() {
  await userEvent.click(screen.getByRole("button", { name: "Start hunting" }));
  await screen.findByRole("heading", { name: "Clean the name" });
}

beforeEach(() => sessionStorage.clear());
afterEach(() => vi.useRealTimers());

describe("BugHunt", () => {
  it("shows the setup form, the leaderboard and the stats", async () => {
    mockApi();
    render(<App />);
    expect(screen.getByRole("heading", { name: "Can you spot the bug?" })).toBeInTheDocument();
    expect(await screen.findByText("Ada")).toBeInTheDocument();
    expect(await screen.findByText(/Hardest so far: Shallow copy \(80% missed\)/)).toBeInTheDocument();
  });

  it("starts a game with the chosen options", async () => {
    const calls = mockApi();
    render(<App />);
    await userEvent.click(screen.getByLabelText("SQL"));
    await userEvent.click(screen.getByLabelText("8"));
    await startGame();
    expect(calls.find((c) => c.key === "POST /api/games").body).toEqual({ language: "sql", rounds: 8 });
    expect(screen.getByText("Bug 1 of 2")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Line 2: name.strip()" })).toBeInTheDocument();
  });

  it("shows the explanation and the fix after a correct answer", async () => {
    const calls = mockApi();
    render(<App />);
    await startGame();
    await userEvent.click(screen.getByRole("button", { name: /Line 2/ }));

    expect(await screen.findByRole("heading", { name: /Correct!/ })).toHaveTextContent("+150");
    expect(screen.getByText("100 base + 50 speed bonus")).toBeInTheDocument();
    expect(screen.getByText("Bug type: Ignored return value")).toBeInTheDocument();
    expect(screen.getByText(/result of strip\(\) must be assigned/)).toBeInTheDocument();
    expect(screen.getByText("name = name.strip()")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Next bug" })).toHaveFocus();
    expect(calls.find((c) => c.key === "POST /api/games/g1/answer").body).toEqual({ line: 2 });
  });

  it("lets you use a hint once", async () => {
    mockApi();
    render(<App />);
    await startGame();
    await userEvent.click(screen.getByRole("button", { name: /Show a hint/ }));
    expect(await screen.findByText("Hint: Look at what strip() returns.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Hint used" })).toBeDisabled();
  });

  it("plays a whole game, submits the score and shows the leaderboard", async () => {
    mockApi();
    render(<App />);
    await startGame();
    await userEvent.click(screen.getByRole("button", { name: /Line 2/ }));
    await userEvent.click(await screen.findByRole("button", { name: "Next bug" }));

    await screen.findByRole("heading", { name: "Admin check" });
    await userEvent.click(screen.getByRole("button", { name: /Line 1/ }));
    expect(await screen.findByRole("heading", { name: "Not quite" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "See my results" }));

    expect(await screen.findByRole("heading", { name: "Game over" })).toBeInTheDocument();
    expect(screen.getByText("You found 1 of 2 bugs (50%).")).toBeInTheDocument();
    expect(screen.getByText("Clean the name")).toBeInTheDocument();

    await userEvent.type(screen.getByLabelText("Add your score to the leaderboard"), "Krish");
    await userEvent.click(screen.getByRole("button", { name: "Submit score" }));
    expect(await screen.findByText("You are number 2 on the leaderboard.")).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Leaderboard", level: 2 })).toBeInTheDocument();
  });

  it("answers automatically when the time runs out", async () => {
    vi.useFakeTimers({ toFake: ["setInterval", "clearInterval", "Date"] });
    const calls = mockApi({ "POST /api/games/g1/answer": () => ({ ...CORRECT, outcome: "timeout", points: 0, base_points: 0, speed_bonus: 0 }) });
    render(<App />);
    await startGame();
    await act(async () => {
      vi.advanceTimersByTime(46000);
    });
    expect(await screen.findByRole("heading", { name: "Time's up" })).toBeInTheDocument();
    expect(calls.find((c) => c.key === "POST /api/games/g1/answer").body).toEqual({ line: null });
  });

  it("shows server errors from starting a game", async () => {
    mockApi({ "POST /api/games": () => ({ __status: 429, detail: "Too many games started. Please wait a minute and try again." }) });
    render(<App />);
    await userEvent.click(screen.getByRole("button", { name: "Start hunting" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Too many games started");
  });

  it("explains a network failure", async () => {
    mockApi();
    render(<App />);
    globalThis.fetch.mockImplementationOnce(async () => {
      throw new TypeError("Failed to fetch");
    });
    await userEvent.click(screen.getByRole("button", { name: "Start hunting" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Cannot reach the server");
  });

  it("resumes an unfinished game after a refresh", async () => {
    sessionStorage.setItem("bughunt-game", "g1");
    mockApi({ "GET /api/games/g1": () => ({ ...SUMMARY, finished: false, answered: 0 }) });
    render(<App />);
    expect(await screen.findByRole("heading", { name: "Clean the name" })).toBeInTheDocument();
  });

  it("forgets a game the server no longer knows", async () => {
    sessionStorage.setItem("bughunt-game", "gone");
    mockApi({ "GET /api/games/gone": () => ({ __status: 404, detail: "Game not found." }) });
    render(<App />);
    expect(screen.getByRole("heading", { name: "Can you spot the bug?" })).toBeInTheDocument();
    await waitFor(() => expect(sessionStorage.getItem("bughunt-game")).toBeNull());
  });
});
