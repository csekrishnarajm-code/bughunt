// A tiny syntax highlighter for the three languages in the game.

const KEYWORDS = {
  python: "def return for in if elif else is not and or None True False lambda class import from while pass",
  javascript:
    "function return const let var for of in if else async await class new this true false null undefined",
  sql: "select from where join left on group by order having limit update set and or not null is in as distinct between desc asc count",
};

const SETS = Object.fromEntries(Object.entries(KEYWORDS).map(([k, v]) => [k, new Set(v.split(" "))]));
const COMMENT = { python: "#", javascript: "//", sql: "--" };

export function tokenize(line, language) {
  const keywords = SETS[language] || new Set();
  const tokens = [];
  let rest = line;
  while (rest.length) {
    let match;
    if (rest.startsWith(COMMENT[language] || "\u0000")) {
      tokens.push({ type: "comment", text: rest });
      break;
    } else if ((match = /^(["'`])(?:\\.|(?!\1).)*\1?/.exec(rest))) {
      tokens.push({ type: "string", text: match[0] });
    } else if ((match = /^\d+(\.\d+)?/.exec(rest))) {
      tokens.push({ type: "number", text: match[0] });
    } else if ((match = /^[A-Za-z_][A-Za-z0-9_]*/.exec(rest))) {
      const word = match[0];
      const isKeyword = keywords.has(language === "sql" ? word.toLowerCase() : word);
      const isCall = !isKeyword && /^\s*\(/.test(rest.slice(word.length));
      tokens.push({ type: isKeyword ? "keyword" : isCall ? "function" : "plain", text: word });
    } else if ((match = /^\s+/.exec(rest))) {
      tokens.push({ type: "plain", text: match[0] });
    } else {
      match = [rest[0]];
      tokens.push({ type: "punct", text: rest[0] });
    }
    rest = rest.slice(match[0].length);
  }
  return tokens;
}
