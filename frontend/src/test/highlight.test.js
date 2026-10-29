import { describe, expect, it } from "vitest";
import { tokenize } from "../highlight";

const types = (line, language) => tokenize(line, language).filter((t) => t.type !== "plain").map((t) => [t.type, t.text]);

describe("tokenize", () => {
  it("colours Python keywords, calls, strings and numbers", () => {
    expect(types('return user["role"] is "admin"', "python")).toEqual([
      ["keyword", "return"],
      ["punct", "["],
      ["string", '"role"'],
      ["punct", "]"],
      ["keyword", "is"],
      ["string", '"admin"'],
    ]);
    expect(types("total += len(scores) + 2", "python")).toContainEqual(["function", "len"]);
    expect(types("x = 3.5", "python")).toContainEqual(["number", "3.5"]);
  });

  it("treats the rest of the line as a comment", () => {
    expect(types("x = 1  # note", "python").pop()).toEqual(["comment", "# note"]);
    expect(types("let a = 1; // note", "javascript").pop()).toEqual(["comment", "// note"]);
    expect(types("SELECT 1 -- note", "sql").pop()).toEqual(["comment", "-- note"]);
  });

  it("matches SQL keywords in any case", () => {
    const kinds = types("select name FROM customers where city is null", "sql").filter((t) => t[0] === "keyword");
    expect(kinds.map((t) => t[1])).toEqual(["select", "FROM", "where", "is", "null"]);
  });

  it("handles template strings and unfinished strings without crashing", () => {
    expect(types("const s = `hi ${name}`;", "javascript")).toContainEqual(["string", "`hi ${name}`"]);
    expect(() => tokenize("print('oops", "python")).not.toThrow();
  });

  it("never loses or adds characters", () => {
    const line = '  funcs.append(lambda x, i=i: x * i)  # keep';
    expect(tokenize(line, "python").map((t) => t.text).join("")).toBe(line);
  });
});
