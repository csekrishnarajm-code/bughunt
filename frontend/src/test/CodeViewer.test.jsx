import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import CodeViewer from "../components/CodeViewer.jsx";

const LINES = ["def clean(name):", "    name.strip()", "    return name.title()"];

describe("CodeViewer", () => {
  it("shows every line as a button with a helpful name", () => {
    render(<CodeViewer lines={LINES} language="python" onSelect={() => {}} />);
    expect(screen.getAllByRole("button")).toHaveLength(3);
    expect(screen.getByRole("button", { name: "Line 2: name.strip()" })).toBeInTheDocument();
  });

  it("reports the clicked line number", async () => {
    const onSelect = vi.fn();
    render(<CodeViewer lines={LINES} language="python" onSelect={onSelect} />);
    await userEvent.click(screen.getByRole("button", { name: /Line 3/ }));
    expect(onSelect).toHaveBeenCalledWith(3);
  });

  it("works with the keyboard: arrow keys move, Enter selects", async () => {
    const onSelect = vi.fn();
    render(<CodeViewer lines={LINES} language="python" onSelect={onSelect} />);
    screen.getByRole("button", { name: /Line 1/ }).focus();
    await userEvent.keyboard("{ArrowDown}");
    expect(screen.getByRole("button", { name: /Line 2/ })).toHaveFocus();
    await userEvent.keyboard("{ArrowDown}{ArrowDown}");
    expect(screen.getByRole("button", { name: /Line 3/ })).toHaveFocus(); // stops at the last line
    await userEvent.keyboard("{ArrowUp}{Enter}");
    expect(onSelect).toHaveBeenCalledWith(2);
  });

  it("cannot be clicked after the answer is shown, and marks the bug and the wrong pick", async () => {
    const onSelect = vi.fn();
    render(<CodeViewer lines={LINES} language="python" onSelect={onSelect} disabled bugLine={2} chosenLine={3} />);
    await userEvent.click(screen.getByRole("button", { name: /Line 1/ }));
    expect(onSelect).not.toHaveBeenCalled();
    expect(screen.getByText("bug")).toBeInTheDocument();
    expect(screen.getByText("your pick")).toBeInTheDocument();
  });
});
