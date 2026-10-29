import { useRef } from "react";
import { tokenize } from "../highlight";

export default function CodeViewer({ lines, language, onSelect, disabled, bugLine, chosenLine }) {
  const buttons = useRef([]);

  function onKeyDown(event, index) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      buttons.current[Math.min(index + 1, lines.length - 1)]?.focus();
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      buttons.current[Math.max(index - 1, 0)]?.focus();
    }
  }

  return (
    <ol className="code" aria-label="Code. Choose the line that contains the bug.">
      {lines.map((text, index) => {
        const number = index + 1;
        const isBug = bugLine === number;
        const isWrong = chosenLine === number && chosenLine !== bugLine;
        const classes = ["code-line", isBug && "is-bug", isWrong && "is-wrong"].filter(Boolean).join(" ");
        return (
          <li key={number}>
            <button
              type="button"
              ref={(el) => (buttons.current[index] = el)}
              className={classes}
              disabled={disabled}
              aria-label={`Line ${number}: ${text.trim() || "blank"}`}
              onClick={() => onSelect(number)}
              onKeyDown={(event) => onKeyDown(event, index)}
            >
              <span className="ln" aria-hidden="true">
                {number}
              </span>
              <code>
                {text === "" ? "\u00a0" : tokenize(text, language).map((t, i) => (
                  <span key={i} className={`tok-${t.type}`}>
                    {t.text}
                  </span>
                ))}
              </code>
              {isBug && <span className="flag flag-bug">bug</span>}
              {isWrong && <span className="flag flag-wrong">your pick</span>}
            </button>
          </li>
        );
      })}
    </ol>
  );
}
