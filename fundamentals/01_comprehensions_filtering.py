"""
Comprehensions and Filtering
============================
Warm-up drill: turning "for each record, if condition, collect X" into a single
comprehension. This shape shows up in almost every data-wrangling question.

Patterns practised:
    [expr for x in xs]                  transform
    [expr for x in xs if cond]          filter
    {expr for x in xs}                  distinct values (set)
    {k: v for x in xs}                  build a lookup (dict)
    [a if cond else b for x in xs]      label each item (conditional expression)

Run:
    python 01_comprehensions_filtering.py
"""

# ---------------------------------------------------------------------------
# Basics on a flat list
# ---------------------------------------------------------------------------
nums = [1, 2, 3, 4]

n1 = [n * 2 for n in nums]  # transform every item
print(n1)

n2 = [n for n in nums if n % 2 == 0]  # keep only the even ones
print(n2)

# ---------------------------------------------------------------------------
# Same ideas on a list of records (list of dicts)
# ---------------------------------------------------------------------------
records = [
    {"clip_id": "c1", "robot": "arm-A", "score": 0.91},
    {"clip_id": "c2", "robot": "arm-B", "score": 0.40},
    {"clip_id": "c3", "robot": "arm-A", "score": 0.77},
    {"clip_id": "c4", "robot": "arm-B", "score": 0.65},
]

# Scores for one robot only: filter on one field, project another.
r1 = [r["score"] for r in records if r["robot"] == "arm-A"]
print(r1)

# Whole records above a threshold.
r2 = [r for r in records if r["score"] > 0.5]
print(r2)

# Distinct robots -> set comprehension de-duplicates for free.
s1 = {r["robot"] for r in records}
print(s1)

# Lookup table clip_id -> score. Dict comprehensions are the idiom for "index by".
s2 = {r["clip_id"]: r["score"] for r in records}
print(s2)

# Filter + project in one go.
l1 = [r["score"] for r in records if r["score"] > 0.5]
print(l1)

# Label every record. NOTE: the `if ... else` goes BEFORE the `for` here
# because it is an expression that produces a value, not a filter.
l2 = ["high" if r["score"] > 0.5 else "low" for r in records]
print(l2)

# ---------------------------------------------------------------------------
# Self-test: five questions on a small people table
# ---------------------------------------------------------------------------
people = [
    {"name": "Ana", "age": 30, "city": "NYC"},
    {"name": "Bo", "age": 25, "city": "SF"},
    {"name": "Cy", "age": 30, "city": "SF"},
    {"name": "Di", "age": 25, "city": "NYC"},
]

# (a) list of just the names
l1 = [p["name"] for p in people]
print(l1)

# (b) names of people in SF only
l2 = [p["name"] for p in people if p["city"] == "SF"]
print(l2)

# (c) set of distinct cities
s1 = {p["city"] for p in people}
print(s1)

# (d) label each person "senior" if age >= 30 else "junior"
l3 = ["senior" if p["age"] >= 30 else "junior" for p in people]
print(l3)

# (e) dict {name: age} for people under 30 only
d1 = {p["name"]: p["age"] for p in people if p["age"] < 30}
print(d1)


"""
Expected output
---------------
[2, 4, 6, 8]
[2, 4]
[0.91, 0.77]
[{'clip_id': 'c1', 'robot': 'arm-A', 'score': 0.91}, {'clip_id': 'c3', 'robot': 'arm-A', 'score': 0.77}, {'clip_id': 'c4', 'robot': 'arm-B', 'score': 0.65}]
{'arm-A', 'arm-B'}
{'c1': 0.91, 'c2': 0.4, 'c3': 0.77, 'c4': 0.65}
[0.91, 0.77, 0.65]
['high', 'low', 'high', 'high']
['Ana', 'Bo', 'Cy', 'Di']
['Bo', 'Cy']
{'SF', 'NYC'}
['senior', 'junior', 'senior', 'junior']
{'Bo': 25, 'Di': 25}
"""
