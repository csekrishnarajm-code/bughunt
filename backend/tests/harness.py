"""Run challenge code in Python, Node.js or SQLite and return JSON-comparable results."""
import json
import os
import sqlite3
import subprocess
import tempfile
import warnings

from .challenge_checks import SQL_SETUP


def norm(value):
    """Round-trip through JSON so tuples/lists and NaN/undefined compare like the JS output."""
    return json.loads(json.dumps(value))


def run_python(code: str, checks):
    namespace = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        exec(compile(code, "<challenge>", "exec"), namespace)
    results = []
    for expression, _ in checks:
        try:
            results.append(norm(eval(expression, namespace)))
        except Exception as exc:  # the buggy code may raise: that counts as a wrong result
            results.append({"__error": type(exc).__name__})
    return results


def run_js(code: str, checks, setup: str = ""):
    body = [setup, code, "(async () => {", "  const out = [];"]
    for expression, _ in checks:
        body.append(f"  try {{ out.push(await ({expression})); }} catch (e) {{ out.push({{ __error: String(e) }}); }}")
    body += ["  console.log(JSON.stringify(out));", "})();"]
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as handle:
        handle.write("\n".join(body))
        path = handle.name
    try:
        done = subprocess.run(["node", path], capture_output=True, text=True, timeout=15)
    finally:
        os.unlink(path)
    if done.returncode != 0:
        return [{"__error": done.stderr.strip()[:200]}]
    return json.loads(done.stdout.strip().splitlines()[-1])


def run_sql(code: str, after: str | None = None):
    con = sqlite3.connect(":memory:")
    con.executescript(SQL_SETUP)
    try:
        if code.lstrip().upper().startswith("SELECT"):
            rows = con.execute(code).fetchall()
        else:
            con.executescript(code)
            rows = con.execute(after).fetchall()
    except sqlite3.Error as exc:
        return [{"__error": str(exc)}]
    finally:
        con.close()
    return [list(row) for row in rows]
