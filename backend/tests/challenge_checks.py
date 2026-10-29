"""Behaviour checks for every challenge.

For Python and JavaScript: (expression, expected value) pairs, evaluated after the code runs.
For SQL: the rows the query must return (or, for UPDATE, the rows `after` returns).
The FIXED code must pass every check and the BUGGY code must fail at least one.
"""

SQL_SETUP = """
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, total INTEGER, status TEXT, created_at TEXT);
INSERT INTO customers VALUES (1,'Asha','Pune'),(2,'Ravi',NULL),(3,'Meena','Chennai'),(4,'Karan',NULL);
INSERT INTO orders VALUES
 (1,1,500,'paid','2026-01-05 10:00:00'),
 (2,1,300,'pending','2026-01-31 18:30:00'),
 (3,1,700,'paid','2026-02-01 09:00:00'),
 (4,2,200,'paid','2026-01-12 11:00:00'),
 (5,3,900,'pending','2026-01-20 12:00:00'),
 (6,3,100,'cancelled','2026-01-21 13:00:00'),
 (7,1,400,'paid','2026-01-15 14:00:00');
"""

JS_FETCH_SETUP = (
    'function fetchUser(id) { return Promise.resolve({ json: () => Promise.resolve({ name: "Ada" }) }); }'
)

CHECKS = {
    # ------------------------------------------------------------------ Python
    "py-ignored-return": {"checks": [("clean('  ada lovelace ')", "Ada Lovelace")]},
    "py-int-division": {"checks": [("average([1, 2])", 1.5)]},
    "py-dict-get": {"checks": [('count_words(["a", "b", "a"])', {"a": 2, "b": 1})]},
    "py-mutable-default": {"checks": [("[add_item(1), add_item(2)]", [[1], [2]])]},
    "py-off-by-one": {
        "checks": [("last_n([1, 2, 3, 4, 5], 2)", [4, 5]), ("last_n([1, 2, 3], 0)", [])]
    },
    "py-is-equals": {"checks": [('is_admin({"role": "".join(["ad", "min"])})', True)]},
    "py-late-binding": {"checks": [("[f(10) for f in make_multipliers()]", [0, 10, 20])]},
    "py-shallow-copy": {
        "checks": [
            (
                "(lambda g: [set_cell(g, 0, 0, 9), g])([[0, 0], [0, 0]])",
                [[[9, 0], [0, 0]], [[0, 0], [0, 0]]],
            )
        ]
    },
    # -------------------------------------------------------------- JavaScript
    "js-nan-equality": {"checks": [("isInvalid(NaN)", True), ("isInvalid(5)", False)]},
    "js-off-by-one": {"checks": [("sum([1, 2, 3])", 6)]},
    "js-sort-numbers": {"checks": [("largest([5, 10, 9])", 10)]},
    "js-var-closure": {"checks": [("makeCounters().map((f) => f())", [0, 1, 2])]},
    "js-missing-await": {"setup": JS_FETCH_SETUP, "checks": [("getUserName(1)", "Ada")]},
    "js-reduce-initial": {"checks": [("totalPrice([{ price: 5 }, { price: 7 }])", 12)]},
    "js-this-foreach": {"checks": [("(timer.tick(), timer.seconds)", 3)]},
    "js-parseint-map": {"checks": [('toNumbers(["1", "2", "3"])', [1, 2, 3])]},
    # --------------------------------------------------------------------- SQL
    "sql-null-comparison": {"expected": [["Ravi"], ["Karan"]]},
    "sql-order-desc": {"expected": [[5, 900], [3, 700], [1, 500]]},
    "sql-count-distinct": {"expected": [[3]]},
    "sql-missing-on": {"expected": [["Asha", 500], ["Asha", 700], ["Ravi", 200], ["Asha", 400]]},
    "sql-where-aggregate": {"expected": [[1, 4]]},
    "sql-left-join-where": {
        "expected": [["Asha", 3], ["Karan", 0], ["Meena", 0], ["Ravi", 1]]
    },
    "sql-and-or-precedence": {
        "after": "SELECT id, status FROM orders ORDER BY id",
        "expected": [
            [1, "shipped"], [2, "shipped"], [3, "shipped"], [4, "paid"],
            [5, "pending"], [6, "cancelled"], [7, "shipped"],
        ],
    },
    "sql-date-range": {"expected": [[6]]},
}
