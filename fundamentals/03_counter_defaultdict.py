"""
collections.defaultdict and collections.Counter
===============================================
Warm-up drill: the two containers that make "group by" and "count by" one-liners.

    defaultdict(list)   "when a key is missing, create it as []"  -> group values by key
    defaultdict(int)    "when a key is missing, create it as 0"   -> count by key
    Counter(iterable)   counts hashable items; .most_common(n) gives the top n

Run:
    python 03_counter_defaultdict.py
"""

from collections import Counter, defaultdict

# A plain dict raises KeyError on a missing key:
di = {"name": "VK"}
# print(di["phone"])   # KeyError: 'phone'

# ---------------------------------------------------------------------------
# defaultdict(list) - group values under a key without checking "is it there yet?"
# ---------------------------------------------------------------------------
d = defaultdict(list)

d["a"].append(1)  # "a" is missing -> created as [], then 1 appended -> [1]
d["a"].append(2)  # "a" exists -> [1, 2]
d["b"].append(10)  # "b" missing -> created as [], then 10 -> [10]

print(d)  # defaultdict(<class 'list'>, {'a': [1, 2], 'b': [10]})
print(dict(d))  # {'a': [1, 2], 'b': [10]}  plain-dict view, nicer to print
print(d["a"])  # [1, 2]

# ---------------------------------------------------------------------------
# Counter - count occurrences
# ---------------------------------------------------------------------------
tags = ["a", "b", "a", "c", "a"]
c = Counter(tags)
print(c)  # Counter({'a': 3, 'b': 1, 'c': 1})
print(c["a"])  # 3
print(c["z"])  # 0  - a missing key is 0, NOT a KeyError
print(c.most_common())  # all, most frequent first
print(c.most_common(2))  # top 2

# ---------------------------------------------------------------------------
# Applying both to a list of records
# ---------------------------------------------------------------------------
records = [
    {"clip_id": "c1", "robot": "arm-A", "score": 0.91},
    {"clip_id": "c2", "robot": "arm-B", "score": 0.40},
    {"clip_id": "c3", "robot": "arm-A", "score": 0.77},
    {"clip_id": "c4", "robot": "arm-B", "score": 0.65},
]

# Number of clips per robot: Counter over a generator expression.
clips = Counter(r["robot"] for r in records)
print(clips)

# All scores per robot: the classic group-by with defaultdict(list).
scores = defaultdict(list)
for r in records:
    scores[r["robot"]].append(r["score"])

print(dict(scores))

# Max score per robot, version 1: running max in a single pass.
# .get(key, -inf) means "the first score always wins".
max_scores = {}
for r in records:
    max_scores[r["robot"]] = max(max_scores.get(r["robot"], float("-inf")), r["score"])
print(dict(max_scores))

# Max score per robot, version 2: reduce the grouped lists.
max_scores = {}
for robot, lst in scores.items():
    print(robot, lst)
    max_scores[robot] = max(lst)

print(max_scores)

# Version 3: the same reduction as a dict comprehension (most idiomatic).
res = {robot: max(lst) for robot, lst in scores.items()}
print(res)

# Any aggregate works the same way once the data is grouped.
no_of_scores = {robot: len(lst) for robot, lst in scores.items()}
print(no_of_scores)


"""
Expected output
---------------
defaultdict(<class 'list'>, {'a': [1, 2], 'b': [10]})
{'a': [1, 2], 'b': [10]}
[1, 2]
Counter({'a': 3, 'b': 1, 'c': 1})
3
0
[('a', 3), ('b', 1), ('c', 1)]
[('a', 3), ('b', 1)]
Counter({'arm-A': 2, 'arm-B': 2})
{'arm-A': [0.91, 0.77], 'arm-B': [0.4, 0.65]}
{'arm-A': 0.91, 'arm-B': 0.65}
arm-A [0.91, 0.77]
arm-B [0.4, 0.65]
{'arm-A': 0.91, 'arm-B': 0.65}
{'arm-A': 0.91, 'arm-B': 0.65}
{'arm-A': 2, 'arm-B': 2}
"""
