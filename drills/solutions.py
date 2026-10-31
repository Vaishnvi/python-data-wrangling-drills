"""
Reference solutions for drills.py
=================================
Open ONLY after a 25-minute attempt at the corresponding problem.
Check them against the tests with:
    DRILLS=solutions python test_drills.py
"""

from __future__ import annotations

import hashlib
import math
from bisect import bisect_left
from collections import defaultdict, deque


# 1 ---------------------------------------------------------------------------
def sessionize(events, gap_s):
    # Group timestamps per user, sort each, then one sweep comparing neighbours.
    by_user = defaultdict(list)
    for e in events:
        by_user[e["user"]].append(e["ts"])
    out = {}
    for user, ts in by_user.items():
        ts.sort()
        sessions, cur = [], [ts[0]]
        for prev, t in zip(ts, ts[1:]):  # pairs (ts[i-1], ts[i])
            if t - prev > gap_s:  # strictly greater: a gap EQUAL to the limit stays in-session
                sessions.append(cur)
                cur = [t]
            else:
                cur.append(t)
        sessions.append(cur)
        out[user] = sessions
    return out


# 2 ---------------------------------------------------------------------------
def active_segments(flags, fps):
    if fps <= 0:
        raise ValueError("fps must be > 0")
    segs, start = [], None
    for i, f in enumerate(flags):
        if f and start is None:
            start = i
        elif not f and start is not None:
            segs.append({"start_frame": start, "end_frame": i - 1, "start_s": start / fps, "end_s": i / fps})
            start = None
    if start is not None:  # close a run that reaches the end of the input
        segs.append(
            {"start_frame": start, "end_frame": len(flags) - 1, "start_s": start / fps, "end_s": len(flags) / fps}
        )
    return segs


# 3 ---------------------------------------------------------------------------
def merge_intervals(intervals):
    # Sort by start; then each interval either extends the last merged one or starts a new one.
    out = []
    for s, e in sorted(intervals):
        if s > e:
            raise ValueError(f"start > end: {(s, e)}")
        if out and s <= out[-1][1]:  # <= so touching intervals merge too
            out[-1][1] = max(out[-1][1], e)  # max handles an interval fully inside the last one
        else:
            out.append([s, e])
    return [tuple(x) for x in out]


# 4 ---------------------------------------------------------------------------
def nearest_sensor(frame_ts, sensor_ts, max_gap):
    out = []
    n = len(sensor_ts)
    for t in frame_ts:
        if n == 0:
            out.append(None)
            continue
        i = bisect_left(sensor_ts, t)  # first sensor index with ts >= t
        # The nearest reading is either just before or at/after the insertion point.
        cands = [j for j in (i - 1, i) if 0 <= j < n]
        # Rank by distance, then by index so an exact tie picks the smaller index.
        j = min(cands, key=lambda k: (abs(sensor_ts[k] - t), k))
        out.append(j if abs(sensor_ts[j] - t) <= max_gap else None)
    return out


# 5 ---------------------------------------------------------------------------
def burst_alerts(times, window_s, k):
    if k < 1 or window_s <= 0:
        raise ValueError("k >= 1 and window_s > 0")
    win, alerts = deque(), []
    for t in sorted(times):
        win.append(t)
        # Evict everything older than the window (t - window_s, t]. Each timestamp is
        # appended once and popped at most once, so the whole sweep is O(n).
        while t - win[0] > window_s:
            win.popleft()
        if len(win) >= k:
            alerts.append(t)
    return alerts


# 6 ---------------------------------------------------------------------------
def resample(samples, t0, t1, step):
    if step <= 0:
        raise ValueError("step must be > 0")
    samples = sorted(samples)
    out, j, last = [], 0, None
    t = t0
    # Two pointers: `t` walks the grid, `j` walks the samples; neither goes backwards.
    # The 1e-12 tolerances absorb float accumulation error in `t += step`.
    # (A drift-free alternative is t = t0 + i * step for integer i.)
    while t <= t1 + 1e-12:
        while j < len(samples) and samples[j][0] <= t + 1e-12:
            last = samples[j][1]  # forward fill: remember the latest sample so far
            j += 1
        out.append((round(t, 9), last))
        t += step
    return out


# 7 ---------------------------------------------------------------------------
def episode_summaries(frames):
    by_ep, dropped = defaultdict(list), 0
    for f in frames:
        if not isinstance(f, dict):
            dropped += 1
            continue
        ep, fi, st = f.get("episode_index"), f.get("frame_index"), f.get("state")
        if (
            not isinstance(ep, int)
            or not isinstance(fi, int)
            or fi < 0
            or not isinstance(st, list)
            or not st
            or any(not isinstance(x, (int, float)) or math.isnan(x) for x in st)
        ):
            dropped += 1
            continue
        by_ep[ep].append((fi, st))
    out = []
    for ep in sorted(by_ep):
        rows = sorted(by_ep[ep])
        idx = [i for i, _ in rows]
        dims = {len(s) for _, s in rows}
        out.append(
            {
                "episode_index": ep,
                "frames": len(rows),
                "first_frame": idx[0],
                "last_frame": idx[-1],
                "has_gaps": idx[-1] - idx[0] + 1 != len(rows) or len(set(idx)) != len(idx),
                "dims_consistent": len(dims) == 1,
            }
        )
    return out, dropped


# 8 ---------------------------------------------------------------------------
def split_by_episode(frames, val_frac, test_frac, salt=""):
    if val_frac < 0 or test_frac < 0 or val_frac + test_frac >= 1:
        raise ValueError("bad fractions")
    out = {"train": [], "val": [], "test": []}
    for f in frames:
        # sha1 is stable across runs, machines and Python versions. Python's built-in
        # hash() is salted per process (PYTHONHASHSEED), and random.random() depends
        # on call order, so neither gives a reproducible split.
        h = hashlib.sha1(f"{salt}:{f['episode_index']}".encode()).hexdigest()
        u = int(h[:8], 16) / 0xFFFFFFFF  # uniform-ish in [0, 1]
        split = "test" if u < test_frac else "val" if u < test_frac + val_frac else "train"
        out[split].append(f)
    return out


# 9 ---------------------------------------------------------------------------
def top_k_matches(queries, docs, k):
    def norm(v):
        n = math.sqrt(sum(x * x for x in v))
        return [x / n for x in v] if n > 0 else None  # None marks a zero vector

    # Normalise the docs once; cosine then reduces to a dot product per pair.
    dn = [(i, norm(d)) for i, d in enumerate(docs)]
    dn = [(i, d) for i, d in dn if d is not None]
    out = []
    for q in queries:
        qn = norm(q)
        if qn is None or not dn:
            out.append([])
            continue
        scored = [(sum(a * b for a, b in zip(qn, d)), i) for i, d in dn]
        scored.sort(key=lambda t: (-t[0], t[1]))  # highest score first, then smaller index
        out.append([(i, round(s, 6)) for s, i in scored[:k]])
    return out


# 10 --------------------------------------------------------------------------
def quality_drops(scores, window, min_avg):
    if window < 1:
        raise ValueError("window >= 1")
    out = {}
    for vid, vals in scores.items():
        flagged, run = [], 0.0
        for i, v in enumerate(vals):
            run += v  # add the new value...
            if i >= window:
                run -= vals[i - window]  # ...and drop the one that fell out of the window
            if i >= window - 1 and run / window < min_avg:
                flagged.append(i)
        out[vid] = flagged
    return out


# 11 --------------------------------------------------------------------------
def pivot(rows):
    cams = sorted({r["camera"] for r in rows})
    by_ep = defaultdict(dict)
    for r in rows:
        by_ep[r["episode"]][r["camera"]] = by_ep[r["episode"]].get(r["camera"], 0) + r["frames"]
    return [{"episode": ep, **{c: by_ep[ep].get(c, 0) for c in cams}} for ep in sorted(by_ep)]
