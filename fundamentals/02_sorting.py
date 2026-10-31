"""
Sorting Records
===============
Warm-up drill: sorted() with a key function on lists of dicts.

Things to remember:
    sorted(xs)                 returns a NEW list; xs.sort() sorts in place
    key=lambda r: r["field"]   sort by one field
    reverse=True               descending
    key=lambda r: -r["num"]    descending for a NUMERIC field (handy inside tuples)
    key=lambda r: (a, b)       sort by a, then break ties by b
                               (mix directions by negating the numeric parts)

Python's sort is stable: records that compare equal keep their input order.

Run:
    python 02_sorting.py
"""

nums = [3, 2, 1]
nums_sort = sorted(nums)  # new list, original untouched
print(nums_sort)
nums.sort()  # in place
print(nums)

# ---------------------------------------------------------------------------
# Sorting dicts by a field
# ---------------------------------------------------------------------------
records = [
    {"robot": "arm-A", "score": 0.91},
    {"robot": "arm-B", "score": 0.40},
    {"robot": "arm-A", "score": 0.77},
]

# Ascending by score.
n1 = sorted(records, key=lambda r: r["score"])
print(n1)

# Descending by score.
n2 = sorted(records, key=lambda r: r["score"], reverse=True)
print(n2)

# Multi-key: robot ascending (alphabetical), then score DESCENDING within a robot.
# Negating the number flips its direction while the string stays ascending.
n3 = sorted(records, key=lambda r: (r["robot"], -r["score"]))
print(n3)

# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
people = [
    {"name": "Ana", "age": 30, "city": "NYC"},
    {"name": "Bo", "age": 25, "city": "SF"},
    {"name": "Cy", "age": 30, "city": "SF"},
    {"name": "Di", "age": 25, "city": "NYC"},
]

# (a) by age, youngest first
p_age = sorted(people, key=lambda r: r["age"])
print(p_age)

# (b) by age, descending. Two equivalent ways:
# p_age_des = sorted(people, key=lambda r: r["age"], reverse=True)
p_age_des = sorted(people, key=lambda r: -r["age"])
print(p_age_des)

# (c) city ascending, and within the same city age descending
p_c_a = sorted(people, key=lambda r: (r["city"], -r["age"]))
print(p_c_a)


"""
Expected output
---------------
[1, 2, 3]
[1, 2, 3]
[{'robot': 'arm-B', 'score': 0.4}, {'robot': 'arm-A', 'score': 0.77}, {'robot': 'arm-A', 'score': 0.91}]
[{'robot': 'arm-A', 'score': 0.91}, {'robot': 'arm-A', 'score': 0.77}, {'robot': 'arm-B', 'score': 0.4}]
[{'robot': 'arm-A', 'score': 0.91}, {'robot': 'arm-A', 'score': 0.77}, {'robot': 'arm-B', 'score': 0.4}]
[{'name': 'Bo', 'age': 25, 'city': 'SF'}, {'name': 'Di', 'age': 25, 'city': 'NYC'}, {'name': 'Ana', 'age': 30, 'city': 'NYC'}, {'name': 'Cy', 'age': 30, 'city': 'SF'}]
[{'name': 'Ana', 'age': 30, 'city': 'NYC'}, {'name': 'Cy', 'age': 30, 'city': 'SF'}, {'name': 'Bo', 'age': 25, 'city': 'SF'}, {'name': 'Di', 'age': 25, 'city': 'NYC'}]
[{'name': 'Ana', 'age': 30, 'city': 'NYC'}, {'name': 'Di', 'age': 25, 'city': 'NYC'}, {'name': 'Cy', 'age': 30, 'city': 'SF'}, {'name': 'Bo', 'age': 25, 'city': 'SF'}]
"""
