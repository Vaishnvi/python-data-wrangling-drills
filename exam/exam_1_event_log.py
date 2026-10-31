"""
Mock Exam 1 - Twelve Questions on an Event Log
==============================================
Timed drill: one small list of page-view events, twelve typical "transform these
in-memory records" questions. Each answer is a few lines of defaultdict grouping
plus a comprehension. Wrong first attempts are kept (commented) because the
mistake is instructive.

Run:
    python exam_1_event_log.py
"""

from collections import defaultdict

events = [
    {"user": "ana", "action": "click", "page": "home", "ms": 120},
    {"user": "bo", "action": "view", "page": "pricing", "ms": 300},
    {"user": "ana", "action": "view", "page": "home", "ms": 90},
    {"user": "cy", "action": "click", "page": "home", "ms": 200},
    {"user": "ana", "action": "click", "page": "pricing", "ms": 150},
    {"user": "bo", "action": "click", "page": "home", "ms": 80},
    {"user": "cy", "action": "view", "page": "pricing", "ms": 400},
    {"user": "ana", "action": "view", "page": "pricing", "ms": 110},
]

# ---------------------------------------------------------------------------
# 1. Every unique user
# ---------------------------------------------------------------------------
a1 = {e["user"] for e in events}
print(a1)

# ---------------------------------------------------------------------------
# 2. Number of events per user
# ---------------------------------------------------------------------------
# Group first, then reduce each group with len().
actions_per_user = defaultdict(list)
for e in events:
    actions_per_user[e["user"]].append(e["action"])

print(actions_per_user)

a2 = {user: len(actions) for user, actions in actions_per_user.items()}
print(a2)

# ---------------------------------------------------------------------------
# 3. All ms values for action == "click"
# ---------------------------------------------------------------------------
# WRONG first attempt: grouping by action then filtering the groups gives a
# list nested inside a list ([[120, 200, 150, 80]]), not a flat list.
#
# ms_per_actions = defaultdict(list)
# for e in events:
#     ms_per_actions[e["action"]].append(e["ms"])
# a3 = [ms for action, ms in ms_per_actions.items() if action == "click"]

# A plain filtered comprehension is all that is needed.
a3 = [e["ms"] for e in events if e["action"] == "click"]
print(a3)

# ---------------------------------------------------------------------------
# 4. Events sorted by ms, highest first
# ---------------------------------------------------------------------------
a4 = sorted(events, key=lambda e: -e["ms"])
print(a4)

# ---------------------------------------------------------------------------
# 5. Total ms per user
# ---------------------------------------------------------------------------
ms_per_user = defaultdict(list)
for e in events:
    ms_per_user[e["user"]].append(e["ms"])
print(ms_per_user)

a5 = {user: sum(ms) for user, ms in ms_per_user.items()}
print(a5)

# ---------------------------------------------------------------------------
# 6. Average ms per page
# ---------------------------------------------------------------------------
ms_per_page = defaultdict(list)
for e in events:
    ms_per_page[e["page"]].append(e["ms"])
print(ms_per_page)

a6 = {page: sum(ms) / len(ms) for page, ms in ms_per_page.items()}
print(a6)

# ---------------------------------------------------------------------------
# 7. For each user, their single slowest event (the whole record)
# ---------------------------------------------------------------------------
# WRONG first attempt: max over the ms lists returns just the number, but the
# question asks for the whole event record.
#
# a7 = {user: max(ms) for user, ms in ms_per_user.items()}

# Group the full records, then max() with a key picks the record itself.
by_user = defaultdict(list)
for e in events:
    by_user[e["user"]].append(e)
print(by_user)

a7 = {user: max(details, key=lambda e: e["ms"]) for user, details in by_user.items()}
print(a7)

# ---------------------------------------------------------------------------
# 8. Count of events per (user, action) pair
# ---------------------------------------------------------------------------
# Attempt 1: concatenating the strings as the key WORKS but is fragile -
# ("ab", "c") and ("a", "bc") would collide, and you cannot unpack it later.
user_action = defaultdict(list)

for e in events:
    user_action[e["user"] + e["action"]].append(e["action"])
print(user_action)

a8 = {key: len(value) for key, value in user_action.items()}
print(a8)

# Attempt 2: a TUPLE key is the right way to key on several fields.
user_action = defaultdict(list)

for e in events:
    user_action[(e["user"], e["action"])].append(e["action"])
print(user_action)

a8 = {key: len(value) for key, value in user_action.items()}
print(a8)

# Attempt 3 (best): defaultdict(int) counts directly, no intermediate lists.
user_action = defaultdict(int)
print("Correct:")
for e in events:
    user_action[(e["user"], e["action"])] += 1
print(user_action)

a8 = dict(user_action)
print(a8)

# ---------------------------------------------------------------------------
# 9. Top 2 users by total ms
# ---------------------------------------------------------------------------
print(ms_per_user)

l1 = [(user, sum(ms)) for user, ms in ms_per_user.items()]
print(l1)
a9 = sorted(l1, key=lambda t: -t[1])[:2]
# a9 = sorted(l1, key=lambda t: t[1], reverse=True)[:2]   # equivalent
print(a9)

# ---------------------------------------------------------------------------
# 10. For each page, the set of distinct users who touched it
# ---------------------------------------------------------------------------
dist_users_per_page = defaultdict(list)

for e in events:
    dist_users_per_page[e["page"]].append(e["user"])
print(dist_users_per_page)

a10 = {}
for k, v in dist_users_per_page.items():
    a10[k] = set(v)  # set() removes the repeats
print(a10)

# ---------------------------------------------------------------------------
# 11. {user: "fast"/"slow"}: "slow" if the user's average ms > 150
# ---------------------------------------------------------------------------
avg_ms_per_user = {user: sum(ms) / len(ms) for user, ms in ms_per_user.items()}
print(avg_ms_per_user)

a11 = {user: "slow" if sum(ms) / len(ms) > 150 else "fast" for user, ms in ms_per_user.items()}
print(a11)

# ---------------------------------------------------------------------------
# 12. The single page with the most total ms (just the name)
# ---------------------------------------------------------------------------
print(ms_per_page)

sum_ms_per_page = {page: sum(ms) for page, ms in ms_per_page.items()}
print(sum_ms_per_page)

# Two equivalent ways to take the arg-max of a dict:
a12 = max(sum_ms_per_page, key=sum_ms_per_page.get)  # iterate keys, rank by value
print(sum_ms_per_page.items())
a12 = max(sum_ms_per_page.items(), key=lambda t: t[1])  # iterate pairs, take [0] after
print(a12[0])


"""
Expected output
---------------
{'cy', 'bo', 'ana'}
defaultdict(<class 'list'>, {'ana': ['click', 'view', 'click', 'view'], 'bo': ['view', 'click'], 'cy': ['click', 'view']})
{'ana': 4, 'bo': 2, 'cy': 2}
[120, 200, 150, 80]
[{'user': 'cy', 'action': 'view', 'page': 'pricing', 'ms': 400}, {'user': 'bo', 'action': 'view', 'page': 'pricing', 'ms': 300}, {'user': 'cy', 'action': 'click', 'page': 'home', 'ms': 200}, {'user': 'ana', 'action': 'click', 'page': 'pricing', 'ms': 150}, {'user': 'ana', 'action': 'click', 'page': 'home', 'ms': 120}, {'user': 'ana', 'action': 'view', 'page': 'pricing', 'ms': 110}, {'user': 'ana', 'action': 'view', 'page': 'home', 'ms': 90}, {'user': 'bo', 'action': 'click', 'page': 'home', 'ms': 80}]
defaultdict(<class 'list'>, {'ana': [120, 90, 150, 110], 'bo': [300, 80], 'cy': [200, 400]})
{'ana': 470, 'bo': 380, 'cy': 600}
defaultdict(<class 'list'>, {'home': [120, 90, 200, 80], 'pricing': [300, 150, 400, 110]})
{'home': 122.5, 'pricing': 240.0}
defaultdict(<class 'list'>, {'ana': [{'user': 'ana', 'action': 'click', 'page': 'home', 'ms': 120}, {'user': 'ana', 'action': 'view', 'page': 'home', 'ms': 90}, {'user': 'ana', 'action': 'click', 'page': 'pricing', 'ms': 150}, {'user': 'ana', 'action': 'view', 'page': 'pricing', 'ms': 110}], 'bo': [{'user': 'bo', 'action': 'view', 'page': 'pricing', 'ms': 300}, {'user': 'bo', 'action': 'click', 'page': 'home', 'ms': 80}], 'cy': [{'user': 'cy', 'action': 'click', 'page': 'home', 'ms': 200}, {'user': 'cy', 'action': 'view', 'page': 'pricing', 'ms': 400}]})
{'ana': {'user': 'ana', 'action': 'click', 'page': 'pricing', 'ms': 150}, 'bo': {'user': 'bo', 'action': 'view', 'page': 'pricing', 'ms': 300}, 'cy': {'user': 'cy', 'action': 'view', 'page': 'pricing', 'ms': 400}}
defaultdict(<class 'list'>, {'anaclick': ['click', 'click'], 'boview': ['view'], 'anaview': ['view', 'view'], 'cyclick': ['click'], 'boclick': ['click'], 'cyview': ['view']})
{'anaclick': 2, 'boview': 1, 'anaview': 2, 'cyclick': 1, 'boclick': 1, 'cyview': 1}
defaultdict(<class 'list'>, {('ana', 'click'): ['click', 'click'], ('bo', 'view'): ['view'], ('ana', 'view'): ['view', 'view'], ('cy', 'click'): ['click'], ('bo', 'click'): ['click'], ('cy', 'view'): ['view']})
{('ana', 'click'): 2, ('bo', 'view'): 1, ('ana', 'view'): 2, ('cy', 'click'): 1, ('bo', 'click'): 1, ('cy', 'view'): 1}
Correct:
defaultdict(<class 'int'>, {('ana', 'click'): 2, ('bo', 'view'): 1, ('ana', 'view'): 2, ('cy', 'click'): 1, ('bo', 'click'): 1, ('cy', 'view'): 1})
{('ana', 'click'): 2, ('bo', 'view'): 1, ('ana', 'view'): 2, ('cy', 'click'): 1, ('bo', 'click'): 1, ('cy', 'view'): 1}
defaultdict(<class 'list'>, {'ana': [120, 90, 150, 110], 'bo': [300, 80], 'cy': [200, 400]})
[('ana', 470), ('bo', 380), ('cy', 600)]
[('cy', 600), ('ana', 470)]
defaultdict(<class 'list'>, {'home': ['ana', 'ana', 'cy', 'bo'], 'pricing': ['bo', 'ana', 'cy', 'ana']})
{'home': {'cy', 'bo', 'ana'}, 'pricing': {'cy', 'bo', 'ana'}}
{'ana': 117.5, 'bo': 190.0, 'cy': 300.0}
{'ana': 'fast', 'bo': 'slow', 'cy': 'slow'}
defaultdict(<class 'list'>, {'home': [120, 90, 200, 80], 'pricing': [300, 150, 400, 110]})
{'home': 490, 'pricing': 960}
dict_items([('home', 490), ('pricing', 960)])
pricing
"""
