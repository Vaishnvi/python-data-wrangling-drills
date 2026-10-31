"""
Problem Family 5 - Sessionize Events by Idle Gap
================================================
A "session" is a run of a user's events where no two consecutive events are more
than GAP apart. Classic shape: group by user, sort each user's timestamps, sweep
once comparing each timestamp to the previous one.

    datetime.fromisoformat("2026-03-01T10:10:00")  -> datetime
    datetime - datetime                            -> timedelta
    timedelta(minutes=30)                          -> comparable gap

Time O(n log n) for the per-user sorts, space O(n).

Run:
    python 05_sessionize.py
"""

from collections import defaultdict
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# datetime arithmetic basics
# ---------------------------------------------------------------------------
a = datetime.fromisoformat("2026-03-01T10:10:00")
b = datetime.fromisoformat("2026-03-01T11:00:00")

gap = b - a  # a timedelta
print(gap)  # 0:50:00
print(gap > timedelta(minutes=30))  # True

# ---------------------------------------------------------------------------
# Data: users interleaved and out of time order
# ---------------------------------------------------------------------------
events = [
    {"user": "ana", "ts": "2026-03-01T10:00:00"},
    {"user": "ana", "ts": "2026-03-01T10:10:00"},
    {"user": "bo", "ts": "2026-03-01T09:00:00"},
    {"user": "ana", "ts": "2026-03-01T11:00:00"},
    {"user": "bo", "ts": "2026-03-01T09:20:00"},
    {"user": "ana", "ts": "2026-03-01T11:05:00"},
    {"user": "bo", "ts": "2026-03-01T12:00:00"},
    {"user": "cy", "ts": "2026-03-01T08:00:00"},
    {"user": "ana", "ts": "2026-03-01T09:50:00"},
]

# Step 1: group timestamps by user.
by_user = defaultdict(list)
for e in events:
    by_user[e["user"]].append(e["ts"])

print(by_user)

# ---------------------------------------------------------------------------
# Step 2: sessionize ONE user to get the sweep right
# ---------------------------------------------------------------------------
GAP = timedelta(minutes=30)
ts = sorted(by_user["ana"])  # ISO strings sort chronologically
current = [ts[0]]  # the session being built
sessions = []

for i in range(1, len(ts)):
    cur = datetime.fromisoformat(ts[i])
    prev = datetime.fromisoformat(ts[i - 1])
    if cur - prev > GAP:  # idle too long -> close the session, start a new one
        sessions.append(current)
        current = [ts[i]]
    else:
        current.append(ts[i])
sessions.append(current)  # don't forget the last open session

print(sessions)

# ---------------------------------------------------------------------------
# Step 3: the same sweep for every user
# ---------------------------------------------------------------------------
result = {}

for user, ts_list in by_user.items():
    ts = sorted(ts_list)
    current = [ts[0]]
    sessions = []
    for i in range(1, len(ts)):
        cur = datetime.fromisoformat(ts[i])
        prev = datetime.fromisoformat(ts[i - 1])
        if cur - prev > GAP:
            sessions.append(current)
            current = [ts[i]]
        else:
            current.append(ts[i])
    sessions.append(current)
    result[user] = sessions

print({u: len(s) for u, s in result.items()})  # sessions per user

# Flatten {user: [sessions]} into one list of sessions and find the longest.
all_sessions = [s for sessions in result.values() for s in sessions]
print(max(all_sessions, key=len))


"""
Expected output
---------------
0:50:00
True
defaultdict(<class 'list'>, {'ana': ['2026-03-01T10:00:00', '2026-03-01T10:10:00', '2026-03-01T11:00:00', '2026-03-01T11:05:00', '2026-03-01T09:50:00'], 'bo': ['2026-03-01T09:00:00', '2026-03-01T09:20:00', '2026-03-01T12:00:00'], 'cy': ['2026-03-01T08:00:00']})
[['2026-03-01T09:50:00', '2026-03-01T10:00:00', '2026-03-01T10:10:00'], ['2026-03-01T11:00:00', '2026-03-01T11:05:00']]
{'ana': 2, 'bo': 2, 'cy': 1}
['2026-03-01T09:50:00', '2026-03-01T10:00:00', '2026-03-01T10:10:00']
"""
