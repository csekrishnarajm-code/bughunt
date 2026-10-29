import { act, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import Timer from "../components/Timer.jsx";

beforeEach(() => vi.useFakeTimers());
afterEach(() => vi.useRealTimers());

describe("Timer", () => {
  it("counts down and calls onExpire exactly once", () => {
    const onExpire = vi.fn();
    render(<Timer seconds={3} limit={45} running resetKey={1} onExpire={onExpire} />);
    expect(screen.getByRole("timer")).toHaveTextContent("0:03");
    act(() => vi.advanceTimersByTime(1000));
    expect(screen.getByRole("timer")).toHaveTextContent("0:02");
    expect(onExpire).not.toHaveBeenCalled();
    act(() => vi.advanceTimersByTime(5000));
    expect(screen.getByRole("timer")).toHaveTextContent("0:00");
    expect(onExpire).toHaveBeenCalledTimes(1);
  });

  it("does not run, and does not expire, while paused", () => {
    const onExpire = vi.fn();
    render(<Timer seconds={2} limit={45} running={false} resetKey={1} onExpire={onExpire} />);
    act(() => vi.advanceTimersByTime(10000));
    expect(onExpire).not.toHaveBeenCalled();
    expect(screen.getByRole("timer")).toHaveTextContent("0:02");
  });

  it("turns urgent in the last ten seconds", () => {
    render(<Timer seconds={9} limit={45} running resetKey={1} onExpire={() => {}} />);
    act(() => vi.advanceTimersByTime(300));
    expect(screen.getByRole("timer")).toHaveClass("urgent");
  });

  it("freezes the display when the bug is answered", () => {
    const { rerender } = render(<Timer seconds={20} limit={45} running resetKey={1} onExpire={() => {}} />);
    act(() => vi.advanceTimersByTime(5000));
    rerender(<Timer seconds={20} limit={45} running={false} resetKey={1} onExpire={() => {}} />);
    act(() => vi.advanceTimersByTime(5000));
    expect(screen.getByRole("timer")).toHaveTextContent("0:15");
  });
});
