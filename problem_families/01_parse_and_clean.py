"""
Problem Family 1a - Parse and Clean Messy Records
=================================================
Real data has missing keys, wrong types, junk strings and whole rows that are None.
The pattern: a tiny `to_float` helper that never raises, a `clean()` pass that
keeps good rows and COUNTS the dropped ones, then aggregate only the clean rows.

Tools:
    dict.get(key, default)   safe lookup, no KeyError
    isinstance(x, (int, float))
    try/except around float(x)

Run:
    python 01_parse_and_clean.py
"""

from collections import defaultdict

# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------
r = {"user": "ana"}  # no "ms" key
# r["ms"]                  # KeyError
print(r.get("ms"))  # None  (safe)
print(r.get("ms", 0))  # 0     (safe, with a fallback)

print(isinstance(5, int))  # True
print(isinstance("5", int))  # False - a numeric-looking string is still a str
print(isinstance(5.0, (int, float)))  # True - a tuple checks several types at once


def to_float(x):
    """Convert to float, returning None for anything that cannot be converted.

    float("300") works, float("n/a") raises ValueError, float(None) raises
    TypeError. Catching both means the caller never has to try/except itself.
    """
    try:
        return float(x)
    except (ValueError, TypeError):
        return None


print(to_float("abc"))  # None


# ---------------------------------------------------------------------------
# First version: only validate user and ms
# ---------------------------------------------------------------------------
def clean(records):
    good, dropped = [], 0
    for r in records:
        user = r.get("user")
        ms = to_float(r.get("ms"))
        if user is None or ms is None:
            dropped += 1
            continue
        good.append({"user": user, "ms": ms})
    return good, dropped


# ---------------------------------------------------------------------------
# Full version on a deliberately messy input
# ---------------------------------------------------------------------------
raw = [
    {"user": "ana", "page": "home", "ms": 120},
    {"user": "bo", "page": "pricing", "ms": "300"},  # ms is a string -> coerce
    {"user": "cy", "page": "home"},  # ms missing       -> drop
    {"user": "ana", "page": "pricing", "ms": "n/a"},  # ms junk          -> drop
    {"page": "home", "ms": 90},  # user missing     -> drop
    {"user": "bo", "page": "home", "ms": -50},  # negative ms      -> drop
    {"user": "cy", "page": "pricing", "ms": 400},
    None,  # whole row is None -> drop
]


def clean_data(raw):
    """Return (good_records, dropped_count).

    A good record has a non-empty user and page and a non-negative numeric ms.
    Each good record is rebuilt with only the fields we need, so downstream code
    can rely on exactly those keys being present with the right types.
    """
    good_records, dropped = [], 0
    for r in raw:
        if r is None:  # guard BEFORE calling .get on it
            dropped += 1
            continue
        user = r.get("user")
        page = r.get("page")
        ms = to_float(r.get("ms"))
        # `not user` also rejects "" (empty string), which `is None` would let through.
        if not user or not page or ms is None or ms < 0:
            dropped += 1
            continue
        good_records.append({"user": user, "page": page, "ms": ms})
    return good_records, dropped


good, dropped = clean_data(raw)
print("good:", good, "dropped:", dropped)

# Aggregate only the clean rows: average ms per page.
ms_per_page = defaultdict(list)
for r in good:
    ms_per_page[r["page"]].append(r["ms"])
print(ms_per_page)

ans = {page: sum(ms) / len(ms) for page, ms in ms_per_page.items()}
print(ans)


"""
Expected output
---------------
None
0
True
False
True
None
good: [{'user': 'ana', 'page': 'home', 'ms': 120.0}, {'user': 'bo', 'page': 'pricing', 'ms': 300.0}, {'user': 'cy', 'page': 'pricing', 'ms': 400.0}] dropped: 5
defaultdict(<class 'list'>, {'home': [120.0], 'pricing': [300.0, 400.0]})
{'home': 120.0, 'pricing': 350.0}
"""
