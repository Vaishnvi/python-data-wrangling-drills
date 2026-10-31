"""
Problem Family 3 - De-duplication
=================================
Three flavours of "remove duplicates" that come up constantly:
    (a) exact duplicate rows      -> seen-set of a tuple key, keep first
    (b) latest row per key        -> dict keyed by user, overwrite when newer
    (c) first row per (key, key)  -> dict keyed by tuple, never overwrite

Why not set(rows)? Dicts are unhashable, so they cannot go in a set. Build a
tuple of the fields that define identity and use THAT as the key. The loop
also preserves input order, which list(set(...)) would destroy.
All three are O(n) time, O(n) space.

Run:
    python 03_dedupe.py
"""

rows = [
    {"user": "ana", "page": "home", "ts": "2026-03-01T10:00:00", "ms": 120},
    {"user": "bo", "page": "pricing", "ts": "2026-03-01T10:00:05", "ms": 300},
    {"user": "ana", "page": "home", "ts": "2026-03-01T10:00:00", "ms": 120},  # exact dup of row 0
    {"user": "ana", "page": "pricing", "ts": "2026-03-01T10:02:00", "ms": 150},
    {"user": "cy", "page": "home", "ts": "2026-03-01T10:03:00", "ms": 200},
    {"user": "bo", "page": "home", "ts": "2026-03-01T09:59:00", "ms": 80},  # older than bo's first
    {"user": "ana", "page": "home", "ts": "2026-03-01T10:04:00", "ms": 90},
]

# ---------------------------------------------------------------------------
# Warm-up: dedupe on (user, page, ms), ignoring the timestamp
# ---------------------------------------------------------------------------
seen, out = set(), []

for r in rows:
    key = (r["user"], r["page"], r["ms"])
    if key in seen:
        continue
    seen.add(key)
    out.append(r)

print(out, len(out))

# Warm-up: latest row per user. ISO-8601 timestamps sort correctly as plain
# strings, so a `>` comparison on the ts string is enough here.
best = {}
for r in rows:
    k = r["user"]
    if k not in best or r["ts"] > best[k]["ts"]:
        best[k] = r
out = list(best.values())
print(out)

# ---------------------------------------------------------------------------
# (a) Dedupe EXACT rows - every field is part of the key
# ---------------------------------------------------------------------------
seen, out = set(), []
for r in rows:
    key = (r["user"], r["page"], r["ts"], r["ms"])
    if key in seen:
        continue
    seen.add(key)
    out.append(r)
print(out, len(out))

# ---------------------------------------------------------------------------
# (b) Latest row per user - overwrite whenever a newer ts shows up
# ---------------------------------------------------------------------------
best = {}

for r in rows:
    user = r["user"]
    if user not in best or r["ts"] > best[user]["ts"]:
        best[user] = r
out = list(best.values())
print(out)

# ---------------------------------------------------------------------------
# (c) FIRST row per (user, page) - only insert when the key is new
# ---------------------------------------------------------------------------
best = {}

for r in rows:
    key = (r["user"], r["page"])
    if key not in best:
        best[key] = r
out = list(best.values())
print(out)


"""
Expected output
---------------
[{'user': 'ana', 'page': 'home', 'ts': '2026-03-01T10:00:00', 'ms': 120}, {'user': 'bo', 'page': 'pricing', 'ts': '2026-03-01T10:00:05', 'ms': 300}, {'user': 'ana', 'page': 'pricing', 'ts': '2026-03-01T10:02:00', 'ms': 150}, {'user': 'cy', 'page': 'home', 'ts': '2026-03-01T10:03:00', 'ms': 200}, {'user': 'bo', 'page': 'home', 'ts': '2026-03-01T09:59:00', 'ms': 80}, {'user': 'ana', 'page': 'home', 'ts': '2026-03-01T10:04:00', 'ms': 90}] 6
[{'user': 'ana', 'page': 'home', 'ts': '2026-03-01T10:04:00', 'ms': 90}, {'user': 'bo', 'page': 'pricing', 'ts': '2026-03-01T10:00:05', 'ms': 300}, {'user': 'cy', 'page': 'home', 'ts': '2026-03-01T10:03:00', 'ms': 200}]
[{'user': 'ana', 'page': 'home', 'ts': '2026-03-01T10:00:00', 'ms': 120}, {'user': 'bo', 'page': 'pricing', 'ts': '2026-03-01T10:00:05', 'ms': 300}, {'user': 'ana', 'page': 'pricing', 'ts': '2026-03-01T10:02:00', 'ms': 150}, {'user': 'cy', 'page': 'home', 'ts': '2026-03-01T10:03:00', 'ms': 200}, {'user': 'bo', 'page': 'home', 'ts': '2026-03-01T09:59:00', 'ms': 80}, {'user': 'ana', 'page': 'home', 'ts': '2026-03-01T10:04:00', 'ms': 90}] 6
[{'user': 'ana', 'page': 'home', 'ts': '2026-03-01T10:04:00', 'ms': 90}, {'user': 'bo', 'page': 'pricing', 'ts': '2026-03-01T10:00:05', 'ms': 300}, {'user': 'cy', 'page': 'home', 'ts': '2026-03-01T10:03:00', 'ms': 200}]
[{'user': 'ana', 'page': 'home', 'ts': '2026-03-01T10:00:00', 'ms': 120}, {'user': 'bo', 'page': 'pricing', 'ts': '2026-03-01T10:00:05', 'ms': 300}, {'user': 'ana', 'page': 'pricing', 'ts': '2026-03-01T10:02:00', 'ms': 150}, {'user': 'cy', 'page': 'home', 'ts': '2026-03-01T10:03:00', 'ms': 200}, {'user': 'bo', 'page': 'home', 'ts': '2026-03-01T09:59:00', 'ms': 80}]
"""
