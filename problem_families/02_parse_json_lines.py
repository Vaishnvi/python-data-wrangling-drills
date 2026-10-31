"""
Problem Family 1b - Parse Raw Text / JSON Lines
===============================================
Same clean-and-aggregate idea as 01, but the input is raw STRINGS: a CSV-ish line
and then a list of JSON-lines records where some lines are blank, malformed, or
valid JSON that is not an object.

Tools:
    str.split(",") + str.strip()
    json.loads inside try/except
    isinstance(obj, dict) to reject JSON arrays/scalars

Run:
    python 02_parse_json_lines.py
"""

import json
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# Splitting a delimited line
# ---------------------------------------------------------------------------
line = " ana, home , 120 \n"
parts = [p.strip() for p in line.split(",")]
print(parts)  # ['ana', 'home', '120']

# .split(",") cuts on commas; .strip() removes surrounding spaces/newlines from
# each piece. A line with the wrong number of pieces (len(parts) != 3) is a bad row.
#
# GOTCHA: "".split(",") is [""] - ONE empty piece, not an empty list - so blank
# lines show up as a single empty string. Guard for them explicitly.

# ---------------------------------------------------------------------------
# JSON lines with every kind of defect
# ---------------------------------------------------------------------------
lines = [
    '{"user": "ana", "page": "home", "ms": 120}',
    '{"user": "bo", "page": "pricing", "ms": "300"}',  # ms is a string -> coerce
    "",  # blank line
    '{"user": "cy", "page": "home"}',  # ms missing
    "this is not json",  # malformed
    '{"user": "", "page": "home", "ms": 90}',  # empty user
    '{"user": "bo", "page": "home", "ms": -50}',  # negative ms
    '{"user": "cy", "page": "pricing", "ms": 400}',
    '{"user": "ana", "page": "pricing", "ms": 150, "extra": true}',  # extra field is fine
    '["a", "list", "not", "an", "object"]',  # valid JSON but not a dict
]


def to_float(x):
    """float(x) or None if x cannot be converted."""
    try:
        return float(x)
    except (ValueError, TypeError):
        return None


def parse_json(x):
    """json.loads(x) or None if x is not valid JSON.

    json.JSONDecodeError is a subclass of ValueError, and TypeError covers
    non-string input (e.g. None). Listing all three is explicit and harmless.
    """
    try:
        return json.loads(x)
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def clean_data(lines):
    """Return (good_records, dropped_count) from a list of JSON-line strings."""
    good_records, dropped = [], 0
    for raw_line in lines:
        obj = parse_json(raw_line)
        # Valid JSON is not enough: '["a", "b"]' parses fine but has no .get().
        if obj is None or not isinstance(obj, dict):
            dropped += 1
            continue
        user = obj.get("user")
        page = obj.get("page")
        ms = to_float(obj.get("ms"))
        if not user or not page or ms is None or ms < 0:
            dropped += 1
            continue
        good_records.append({"user": user, "page": page, "ms": ms})
    return good_records, dropped


good_records, dropped = clean_data(lines)
print("good_records:", good_records, "dropped:", dropped)

# ---------------------------------------------------------------------------
# Count good rows per page - two ways
# ---------------------------------------------------------------------------
# 1. Group with defaultdict(list), then take len() of each group.
good_rows_per_page = defaultdict(list)
for g in good_records:
    good_rows_per_page[g["page"]].append(g)

print(good_rows_per_page)

count_good_rows_per_page = {page: len(rows) for page, rows in good_rows_per_page.items()}
print(count_good_rows_per_page)

# 2. Counter does the grouping and counting in one line.
count_good_rows_per_page = Counter(r["page"] for r in good_records)
print(count_good_rows_per_page)


"""
Expected output
---------------
['ana', 'home', '120']
good_records: [{'user': 'ana', 'page': 'home', 'ms': 120.0}, {'user': 'bo', 'page': 'pricing', 'ms': 300.0}, {'user': 'cy', 'page': 'pricing', 'ms': 400.0}, {'user': 'ana', 'page': 'pricing', 'ms': 150.0}] dropped: 6
defaultdict(<class 'list'>, {'home': [{'user': 'ana', 'page': 'home', 'ms': 120.0}], 'pricing': [{'user': 'bo', 'page': 'pricing', 'ms': 300.0}, {'user': 'cy', 'page': 'pricing', 'ms': 400.0}, {'user': 'ana', 'page': 'pricing', 'ms': 150.0}]})
{'home': 1, 'pricing': 3}
Counter({'pricing': 3, 'home': 1})
"""
