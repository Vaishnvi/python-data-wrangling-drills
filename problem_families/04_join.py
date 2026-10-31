"""
Problem Family 4 - Joining Two Tables (Hash Join)
=================================================
Joining in pure Python = build a dict (hash index) on the smaller table's key,
then stream through the other table doing O(1) lookups. Total O(n + m).

    inner join -> skip rows with no match
    left join  -> keep every left row, fill missing right fields with None

Real-world wrinkles handled below:
    * keys that differ only by case / whitespace -> normalise BOTH sides
    * duplicate keys in the lookup table -> the LAST one wins (acts as an update)

{**e, "plan": ...} builds a new merged dict without mutating the original row.

Run:
    python 04_join.py
"""

from collections import defaultdict

# ---------------------------------------------------------------------------
# Minimal inner join
# ---------------------------------------------------------------------------
events = [{"user": "ana", "ms": 120}, {"user": "bo", "ms": 300}, {"user": "zed", "ms": 50}]
users = [{"user": "ana", "plan": "pro"}, {"user": "bo", "plan": "free"}, {"user": "cy", "plan": "pro"}]

# Index the users table by its key.
by_user = {u["user"]: u for u in users}
print(by_user)

joined = []
for e in events:
    u = by_user.get(e["user"])
    if u is None:  # "zed" has no user row -> dropped (inner join)
        continue
    joined.append({**e, "plan": u["plan"]})
print(joined)

# ---------------------------------------------------------------------------
# Messier data
# ---------------------------------------------------------------------------
events = [
    {"user": "ana", "page": "home", "ms": 120},
    {"user": "BO", "page": "pricing", "ms": 300},  # wrong case
    {"user": "cy", "page": "home", "ms": 200},
    {"user": "ana", "page": "pricing", "ms": 150},
    {"user": "dee", "page": "home", "ms": 90},  # no such user
    {"user": " bo ", "page": "home", "ms": 80},  # whitespace
]
users = [
    {"user": "ana", "plan": "pro", "country": "US"},
    {"user": "bo", "plan": "free", "country": "IN"},
    {"user": "cy", "plan": "pro", "country": "UK"},
    {"user": "bo", "plan": "pro", "country": "IN"},  # duplicate: later row is the update
]


def norm(s):
    """Canonical form of a key so 'BO', ' bo ' and 'bo' all match."""
    return s.strip().lower()


# ---------------------------------------------------------------------------
# (a) Inner join on the normalised key
# ---------------------------------------------------------------------------
# Building the dict in input order means the second "bo" overwrites the first.
by_user = {norm(u["user"]): u for u in users}
print(by_user)

joined = []
for e in events:
    key = norm(e["user"])
    u = by_user.get(key)
    if u is None:
        continue
    # Also write the normalised key back so the output is clean.
    joined.append({**e, "user": key, "plan": u["plan"], "country": u["country"]})
print(joined, len(joined))

# ---------------------------------------------------------------------------
# (b) Left join - unmatched events are kept with None for the missing fields
# ---------------------------------------------------------------------------
by_user = {norm(u["user"]): u for u in users}
print(by_user)

joined_left = []
for e in events:
    key = norm(e["user"])
    u = by_user.get(key)
    if u is None:
        joined_left.append({**e, "user": key, "plan": None, "country": None})
    else:
        joined_left.append({**e, "user": key, "plan": u["plan"], "country": u["country"]})
print(joined_left, len(joined_left))

# ---------------------------------------------------------------------------
# (c) Aggregate the joined result: total ms per plan
# ---------------------------------------------------------------------------
ms_per_plan = defaultdict(list)
for j in joined:
    ms_per_plan[j["plan"]].append(j["ms"])
print(ms_per_plan)

total_ms_per_plan = {plan: sum(ms) for plan, ms in ms_per_plan.items()}
print(total_ms_per_plan)


"""
Expected output
---------------
{'ana': {'user': 'ana', 'plan': 'pro'}, 'bo': {'user': 'bo', 'plan': 'free'}, 'cy': {'user': 'cy', 'plan': 'pro'}}
[{'user': 'ana', 'ms': 120, 'plan': 'pro'}, {'user': 'bo', 'ms': 300, 'plan': 'free'}]
{'ana': {'user': 'ana', 'plan': 'pro', 'country': 'US'}, 'bo': {'user': 'bo', 'plan': 'pro', 'country': 'IN'}, 'cy': {'user': 'cy', 'plan': 'pro', 'country': 'UK'}}
[{'user': 'ana', 'page': 'home', 'ms': 120, 'plan': 'pro', 'country': 'US'}, {'user': 'bo', 'page': 'pricing', 'ms': 300, 'plan': 'pro', 'country': 'IN'}, {'user': 'cy', 'page': 'home', 'ms': 200, 'plan': 'pro', 'country': 'UK'}, {'user': 'ana', 'page': 'pricing', 'ms': 150, 'plan': 'pro', 'country': 'US'}, {'user': 'bo', 'page': 'home', 'ms': 80, 'plan': 'pro', 'country': 'IN'}] 5
{'ana': {'user': 'ana', 'plan': 'pro', 'country': 'US'}, 'bo': {'user': 'bo', 'plan': 'pro', 'country': 'IN'}, 'cy': {'user': 'cy', 'plan': 'pro', 'country': 'UK'}}
[{'user': 'ana', 'page': 'home', 'ms': 120, 'plan': 'pro', 'country': 'US'}, {'user': 'bo', 'page': 'pricing', 'ms': 300, 'plan': 'pro', 'country': 'IN'}, {'user': 'cy', 'page': 'home', 'ms': 200, 'plan': 'pro', 'country': 'UK'}, {'user': 'ana', 'page': 'pricing', 'ms': 150, 'plan': 'pro', 'country': 'US'}, {'user': 'dee', 'page': 'home', 'ms': 90, 'plan': None, 'country': None}, {'user': 'bo', 'page': 'home', 'ms': 80, 'plan': 'pro', 'country': 'IN'}] 6
defaultdict(<class 'list'>, {'pro': [120, 300, 200, 150, 80]})
{'pro': 850}
"""
