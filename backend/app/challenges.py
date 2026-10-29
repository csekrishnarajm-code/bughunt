"""The bug challenges.

Each challenge is a short snippet with exactly one buggy line. `patch` maps a line number
(1-based) to its replacement (None deletes the line; "\\n" adds extra lines).
The tests run the buggy and the fixed code to prove every challenge really behaves as
described, so add new ones together with an entry in tests/challenge_checks.py.
"""

DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2}
LANGUAGES = ("python", "javascript", "sql")

SQL_CONTEXT = "customers(id, name, city)\norders(id, customer_id, total, status, created_at)"


def _c(id, language, difficulty, title, category, code, bug_line, patch, explanation, hint, context=None):
    return {
        "id": id,
        "language": language,
        "difficulty": difficulty,
        "title": title,
        "category": category,
        "code": code,
        "bug_line": bug_line,
        "patch": patch,
        "explanation": explanation,
        "hint": hint,
        "context": context,
    }


CHALLENGES = [
    # ------------------------------------------------------------------ Python
    _c(
        "py-ignored-return", "python", "easy", "Clean the name", "Ignored return value",
        "def clean(name):\n    name.strip()\n    return name.title()",
        2, {2: "    name = name.strip()"},
        "Strings cannot be changed in place. strip() returns a new string, and this line throws it away, "
        "so the extra spaces stay. Assign the result back to the variable.",
        "Look at what happens to the value strip() produces.",
    ),
    _c(
        "py-int-division", "python", "easy", "Average score", "Integer division",
        "def average(scores):\n    total = 0\n    for score in scores:\n        total += score\n    return total // len(scores)",
        5, {5: "    return total / len(scores)"},
        "The // operator is floor division, so the average of [1, 2] comes out as 1 instead of 1.5. "
        "Use / for normal division.",
        "Check which kind of division the last line uses.",
    ),
    _c(
        "py-dict-get", "python", "easy", "Word counter", "Missing default value",
        "def count_words(words):\n    counts = {}\n    for word in words:\n        counts[word] = counts.get(word) + 1\n    return counts",
        4, {4: "        counts[word] = counts.get(word, 0) + 1"},
        "The first time a word appears, get(word) returns None, and None + 1 raises a TypeError. "
        "Give get() a default value of 0.",
        "What does get() return for a word it has not seen yet?",
    ),
    _c(
        "py-mutable-default", "python", "medium", "Shopping cart", "Mutable default argument",
        "def add_item(item, cart=[]):\n    cart.append(item)\n    return cart",
        1, {1: "def add_item(item, cart=None):\n    if cart is None:\n        cart = []"},
        "A default value is created once, when the function is defined, so every call without a cart "
        "shares the same list. Use None as the default and create a new list inside the function.",
        "Think about when a default value is created.",
    ),
    _c(
        "py-off-by-one", "python", "medium", "Latest messages", "Off-by-one error",
        "def last_n(items, n):\n    return items[len(items) - n - 1:]",
        2, {2: "    return items[len(items) - n:]"},
        "The slice starts one position too early, so it returns n + 1 items. "
        "Starting at len(items) - n returns exactly the last n items.",
        "Count how many items this slice returns.",
    ),
    _c(
        "py-is-equals", "python", "medium", "Admin check", "Identity vs equality",
        'def is_admin(user):\n    return user["role"] is "admin"',
        2, {2: '    return user["role"] == "admin"'},
        "The is operator checks whether two names point to the same object, not whether the values are equal. "
        "Two equal strings can be different objects, so this check fails unpredictably. Use == to compare values.",
        "Is this comparing values or objects?",
    ),
    _c(
        "py-late-binding", "python", "hard", "Multiplier factory", "Late-binding closure",
        "def make_multipliers():\n    funcs = []\n    for i in range(3):\n        funcs.append(lambda x: x * i)\n    return funcs",
        4, {4: "        funcs.append(lambda x, i=i: x * i)"},
        "Each lambda looks up i when it is called, not when it is created, and by then the loop has "
        "finished with i = 2. Binding i as a default argument captures the value at that moment.",
        "When does the lambda read the value of i?",
    ),
    _c(
        "py-shallow-copy", "python", "hard", "Game grid", "Shallow copy",
        "def duplicate_grid(grid):\n    return [row for row in grid]\n\n"
        "def set_cell(grid, r, c, value):\n    copy = duplicate_grid(grid)\n    copy[r][c] = value\n    return copy",
        2, {2: "    return [row[:] for row in grid]"},
        "The new list holds the same row lists as the original, so changing a cell in the copy also "
        "changes the original grid. Copy each row as well.",
        "Is the copy really independent of the original?",
    ),
    # -------------------------------------------------------------- JavaScript
    _c(
        "js-nan-equality", "javascript", "easy", "Validate input", "NaN is never equal to itself",
        "function isInvalid(n) {\n  return n === NaN;\n}",
        2, {2: "  return Number.isNaN(n);"},
        "NaN is the only JavaScript value that is not equal to itself, so n === NaN is always false. "
        "Use Number.isNaN(n).",
        "Can NaN ever be equal to anything?",
    ),
    _c(
        "js-off-by-one", "javascript", "easy", "Add them up", "Off-by-one error",
        "function sum(nums) {\n  let total = 0;\n  for (let i = 0; i <= nums.length; i++) {\n    total += nums[i];\n  }\n  return total;\n}",
        3, {3: "  for (let i = 0; i < nums.length; i++) {"},
        "Valid indexes run from 0 to length - 1. With <= the loop reads one extra element, undefined, "
        "and the total becomes NaN.",
        "Which index does the last pass of the loop read?",
    ),
    _c(
        "js-sort-numbers", "javascript", "easy", "Biggest number", "Default sort is alphabetical",
        "function largest(nums) {\n  const sorted = nums.sort();\n  return sorted[sorted.length - 1];\n}",
        2, {2: "  const sorted = [...nums].sort((a, b) => a - b);"},
        "sort() without a compare function sorts values as text, so 10 comes before 5. "
        "Pass a numeric compare function. Copying first also avoids changing the caller's array.",
        "How does sort() compare numbers when you give it nothing else?",
    ),
    _c(
        "js-var-closure", "javascript", "medium", "Counter factory", "var is function scoped",
        "function makeCounters() {\n  const fns = [];\n  for (var i = 0; i < 3; i++) {\n    fns.push(() => i);\n  }\n  return fns;\n}",
        3, {3: "  for (let i = 0; i < 3; i++) {"},
        "var gives the whole function one shared variable, so every callback sees its final value, 3. "
        "let creates a new variable for each pass of the loop.",
        "How many separate copies of i exist?",
    ),
    _c(
        "js-missing-await", "javascript", "medium", "Load a user", "Missing await",
        "async function getUserName(id) {\n  const res = await fetchUser(id);\n  const user = res.json();\n  return user.name;\n}",
        3, {3: "  const user = await res.json();"},
        "res.json() returns a promise, so user is a promise and user.name is undefined. "
        "Await it to get the parsed data.",
        "What does res.json() return?",
        context="fetchUser(id) resolves to a fetch Response.",
    ),
    _c(
        "js-reduce-initial", "javascript", "medium", "Cart total", "reduce without an initial value",
        "function totalPrice(items) {\n  return items.reduce((sum, item) => sum + item.price);\n}",
        2, {2: "  return items.reduce((sum, item) => sum + item.price, 0);"},
        "Without an initial value, reduce uses the first item, an object, as the starting sum, so the "
        "result turns into text like '[object Object]7'. Start from 0.",
        "What is the very first value of sum?",
    ),
    _c(
        "js-this-foreach", "javascript", "hard", "Ticking timer", "Lost this binding",
        "const timer = {\n  seconds: 0,\n  tick() {\n    [1, 2, 3].forEach(function () {\n      this.seconds++;\n    });\n  },\n};",
        4, {4: "    [1, 2, 3].forEach(() => {"},
        "A regular function gets its own this, which is not the timer object, so this.seconds is never "
        "updated on the timer. An arrow function keeps the this of the surrounding method.",
        "What does this point to inside a regular callback?",
    ),
    _c(
        "js-parseint-map", "javascript", "hard", "Convert to numbers", "Callback receives extra arguments",
        "function toNumbers(list) {\n  return list.map(parseInt);\n}",
        2, {2: "  return list.map((s) => parseInt(s, 10));"},
        "map passes the index as a second argument, and parseInt treats it as the radix, so "
        "['1', '2', '3'] becomes [1, NaN, NaN]. Wrap the call and pass the radix yourself.",
        "How many arguments does map give its callback?",
    ),
    # --------------------------------------------------------------------- SQL
    _c(
        "sql-null-comparison", "sql", "easy", "Customers without a city", "Comparing with NULL",
        "SELECT name\nFROM customers\nWHERE city = NULL;",
        3, {3: "WHERE city IS NULL;"},
        "Nothing is ever equal to NULL, not even NULL, so this query returns no rows. "
        "Use IS NULL to test for missing values.",
        "Can = ever match a missing value?",
        context=SQL_CONTEXT,
    ),
    _c(
        "sql-order-desc", "sql", "easy", "Top three orders", "Missing sort direction",
        "SELECT id, total\nFROM orders\nORDER BY total\nLIMIT 3;",
        3, {3: "ORDER BY total DESC"},
        "ORDER BY sorts from smallest to largest by default, so LIMIT 3 returns the three smallest orders. "
        "Add DESC to get the biggest.",
        "Which end of the sorted list does LIMIT keep?",
        context=SQL_CONTEXT,
    ),
    _c(
        "sql-count-distinct", "sql", "medium", "How many buyers?", "COUNT vs COUNT DISTINCT",
        "SELECT COUNT(customer_id) AS buyers\nFROM orders;",
        1, {1: "SELECT COUNT(DISTINCT customer_id) AS buyers"},
        "COUNT(customer_id) counts every order, so a customer with four orders is counted four times. "
        "COUNT(DISTINCT customer_id) counts each customer once.",
        "Does this count customers or orders?",
        context=SQL_CONTEXT,
    ),
    _c(
        "sql-missing-on", "sql", "medium", "Paid orders with names", "Missing join condition",
        "SELECT c.name, o.total\nFROM customers c\nJOIN orders o\nWHERE o.status = 'paid'\nORDER BY o.id;",
        3, {3: "JOIN orders o ON o.customer_id = c.id"},
        "Without an ON condition, every customer is paired with every paid order, which multiplies the rows "
        "and attaches the wrong names. Join on customer_id.",
        "How does the database know which order belongs to which customer?",
        context=SQL_CONTEXT,
    ),
    _c(
        "sql-where-aggregate", "sql", "medium", "Frequent buyers", "Aggregate in WHERE",
        "SELECT customer_id, COUNT(*) AS order_count\nFROM orders\nWHERE COUNT(*) > 2\nGROUP BY customer_id;",
        3, {3: None, 4: "GROUP BY customer_id\nHAVING COUNT(*) > 2;"},
        "WHERE filters rows before they are grouped, so it cannot use COUNT(*). "
        "Filter on a group's result with HAVING, after GROUP BY.",
        "When does WHERE run, before or after grouping?",
        context=SQL_CONTEXT,
    ),
    _c(
        "sql-left-join-where", "sql", "hard", "Paid orders per customer", "WHERE breaks a LEFT JOIN",
        "SELECT c.name, COUNT(o.id) AS paid_orders\nFROM customers c\n"
        "LEFT JOIN orders o ON o.customer_id = c.id\nWHERE o.status = 'paid'\nGROUP BY c.name\nORDER BY c.name;",
        4, {3: "LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'paid'", 4: None},
        "The goal is to list every customer, even those with no paid orders. But the WHERE removes rows "
        "where o.status is NULL, which turns the LEFT JOIN into an inner join. Move the condition into the ON clause.",
        "What happens to customers who have no orders at all?",
        context=SQL_CONTEXT,
    ),
    _c(
        "sql-and-or-precedence", "sql", "hard", "Ship Asha's orders", "AND/OR precedence",
        "UPDATE orders\nSET status = 'shipped'\nWHERE customer_id = 1\nAND status = 'paid' OR status = 'pending';",
        4, {4: "AND status IN ('paid', 'pending');"},
        "AND binds tighter than OR, so this reads (customer 1 AND paid) OR pending, and it ships every "
        "customer's pending orders. Use IN, or add parentheses.",
        "Which runs first, AND or OR?",
        context=SQL_CONTEXT,
    ),
    _c(
        "sql-date-range", "sql", "hard", "January orders", "Date range with timestamps",
        "SELECT COUNT(*) AS january_orders\nFROM orders\nWHERE created_at BETWEEN '2026-01-01' AND '2026-01-31';",
        3, {3: "WHERE created_at >= '2026-01-01' AND created_at < '2026-02-01';"},
        "created_at includes a time, so '2026-01-31 18:30:00' is greater than '2026-01-31' and is left out. "
        "Use a half-open range that ends at the first moment of the next month.",
        "What is the time part of a date written without one?",
        context=SQL_CONTEXT,
    ),
]

BY_ID = {c["id"]: c for c in CHALLENGES}


def lines_of(challenge: dict) -> list[str]:
    return challenge["code"].split("\n")


def public_view(challenge: dict) -> dict:
    """What the player may see BEFORE answering: no bug line, fix, category or explanation."""
    return {
        "id": challenge["id"],
        "language": challenge["language"],
        "difficulty": challenge["difficulty"],
        "title": challenge["title"],
        "context": challenge["context"],
        "lines": lines_of(challenge),
    }


def apply_patch(challenge: dict) -> str:
    """Return the fixed source code."""
    patch = challenge["patch"]
    fixed = []
    for number, line in enumerate(lines_of(challenge), start=1):
        if number in patch:
            if patch[number] is not None:
                fixed.extend(patch[number].split("\n"))
        else:
            fixed.append(line)
    return "\n".join(fixed)


def changes_view(challenge: dict) -> list[dict]:
    """The fix, shown after answering: which original lines change and what replaces them."""
    original = lines_of(challenge)
    return [
        {
            "line": number,
            "before": original[number - 1],
            "after": [] if new is None else new.split("\n"),
        }
        for number, new in sorted(challenge["patch"].items())
    ]
