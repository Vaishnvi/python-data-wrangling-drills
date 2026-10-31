"""
Robot-Episode Data Problems (Python standard library only)
==========================================================
Seven "transform in-memory records" problems modelled on a physical-AI data
curation pipeline: motion-based trimming, metadata joins, sensor summaries,
reward-model quality gates and hand-visibility statistics. Each is solved in
plain Python with explicit Big-O, and verified by the asserts at the bottom.

Vocabulary (LeRobot-style datasets):
    episode  = one recorded attempt at a task (e.g. "open the drawer")
    frame    = one timestep of an episode; frame_index restarts at 0 in every episode
    state    = the robot's joint positions at that frame, a list of floats (one per joint)
    index    = a GLOBAL row number across the whole dataset

How to practise: read only the docstring of a problem, set a 25-minute timer,
write your own asserts first, state the Big-O, implement, then compare.

Run:
    python robot_episode_problems.py
"""

from __future__ import annotations

import math
from bisect import bisect_left
from collections import defaultdict
from typing import Any


# ===========================================================================
# 1. Motion energy per frame (how much did the arm move since the last frame?)
# ===========================================================================
def motion_energy(frames: list[dict]) -> tuple[dict[tuple[int, int], float], list[float]]:
    """
    frames: [{"episode_index": int, "frame_index": int, "state": [float, ...]}], unsorted,
            several episodes mixed together; every state has the same length D.
    Steps:
      a) Within each episode (sorted by frame_index), delta_i = state_i(t) - state_i(t-1).
         NEVER diff across episodes: the first frame of an episode has no previous frame.
      b) scale_i = root-mean-square of all delta_i over the whole dataset (floor 1e-9),
         so a fast wrist joint and a slow shoulder joint count comparably.
      c) energy(t) = sqrt( sum_i (delta_i / scale_i)^2 ); first frame of each episode -> 0.0.
    Return ({(episode_index, frame_index): energy}, scale).
    Time O(n log n + n*D), space O(n).
    Why RMS and not std? An arm moving at constant speed has big steps but zero variation.
    """
    # Group frames by episode so we never difference across an episode boundary.
    by_ep: dict[int, list[dict]] = defaultdict(list)
    for f in frames:
        by_ep[f["episode_index"]].append(f)
    if not by_ep:
        return {}, []
    dims = len(frames[0]["state"])

    # Pass 1: per-frame deltas (None for the first frame of an episode) and the
    # running sum of squares per joint, needed for the RMS scale.
    deltas: dict[tuple[int, int], list[float] | None] = {}
    sq_sum = [0.0] * dims
    count = 0
    for ep, rows in by_ep.items():
        rows.sort(key=lambda r: r["frame_index"])
        prev = None
        for r in rows:
            key = (ep, r["frame_index"])
            if prev is None:
                deltas[key] = None
            else:
                d = [a - b for a, b in zip(r["state"], prev)]
                deltas[key] = d
                for i, x in enumerate(d):
                    sq_sum[i] += x * x
                count += 1
            prev = r["state"]

    # Per-joint RMS, floored so a joint that never moves cannot cause a divide-by-zero.
    scale = [max(math.sqrt(s / count), 1e-9) if count else 1e-9 for s in sq_sum]

    # Pass 2: normalised L2 norm of each delta.
    energy = {
        k: 0.0 if d is None else math.sqrt(sum((x / s) ** 2 for x, s in zip(d, scale)))
        for k, d in deltas.items()
    }
    return energy, scale


# ===========================================================================
# 2. Active frames = inside a run of >= k consecutive frames over a threshold
# ===========================================================================
def is_active(energies: list[float], threshold: float, run: int = 3) -> list[bool]:
    """
    energies: one value per frame of ONE episode, in frame order.
    A single frame over the threshold is sensor noise. A frame is active only if it lies in a
    stretch of >= `run` consecutive frames that are all > threshold.
    Return a list of booleans, same length.
    Time O(n), space O(n).
    """
    if run < 1:
        raise ValueError("run must be >= 1")
    n = len(energies)
    out = [False] * n
    i = 0
    while i < n:
        if energies[i] <= threshold:
            i += 1
            continue
        # energies[i] is over the threshold: extend j to the end of this run.
        j = i
        while j + 1 < n and energies[j + 1] > threshold:
            j += 1
        # Only mark the run if it is long enough to be real motion.
        if j - i + 1 >= run:
            for t in range(i, j + 1):
                out[t] = True
        i = j + 1  # jump past the run; every index is visited once -> O(n)
    return out


# ===========================================================================
# 3. Trim window per episode: drop idle set-up at the start and idle time at the end
# ===========================================================================
def trim_windows(frames: list[dict], fps: float, pad_s: float = 0.25) -> list[dict]:
    """
    frames: [{"episode_index", "frame_index", "is_active": bool}], unsorted, several episodes.
    For each episode return one contiguous window from the first active frame to the last,
    padded by pad = round(pad_s * fps) frames on each side and clipped to [0, last_frame].
    Episodes with NO active frame keep their full span and get never_active=True
    (don't trim an aborted take down to nothing -- flag it instead).
    Output per episode, sorted by episode_index:
      {"episode_index", "start_frame", "end_frame", "kept_frames", "trim_fraction",
       "start_ts", "end_ts", "never_active"}
      trim_fraction = 1 - kept_frames / (last_frame + 1);  ts = frame / fps
    Time O(n) for a single grouping pass (+ sort of episodes), space O(episodes).
    """
    if fps <= 0:
        raise ValueError("fps must be > 0")
    if pad_s < 0:
        raise ValueError("pad_s must be >= 0")
    pad = round(pad_s * fps)

    # One pass: per episode track the last frame index and the first/last ACTIVE index.
    # Using .get(ep, i) as the default means the first value seen always wins.
    last: dict[int, int] = {}
    first_act: dict[int, int] = {}
    last_act: dict[int, int] = {}
    for f in frames:
        ep, i = f["episode_index"], f["frame_index"]
        last[ep] = max(last.get(ep, i), i)
        if f["is_active"]:
            first_act[ep] = min(first_act.get(ep, i), i)
            last_act[ep] = max(last_act.get(ep, i), i)

    out = []
    for ep in sorted(last):
        never = ep not in first_act
        start = 0 if never else max(first_act[ep] - pad, 0)  # clip at 0
        end = last[ep] if never else min(last_act[ep] + pad, last[ep])  # clip at last frame
        kept = end - start + 1
        out.append(
            {
                "episode_index": ep,
                "start_frame": start,
                "end_frame": end,
                "kept_frames": kept,
                "trim_fraction": 1 - kept / (last[ep] + 1),
                "start_ts": start / fps,
                "end_ts": end / fps,
                "never_active": never,
            }
        )
    return out


# ===========================================================================
# 4. Join episode metadata to frames and drop orphan rows (a real DROID data quirk)
# ===========================================================================
def drop_orphan_frames(episodes: list[dict], frames: list[dict]) -> tuple[list[dict], dict[str, int]]:
    """
    episodes: [{"episode_index", "dataset_from_index"}]  -- where the episode starts globally
    frames:   [{"index", "episode_index", "frame_index", ...}]
    Some episodes carry an orphan second recording under the same episode_index. A canonical
    frame satisfies  index == dataset_from_index + frame_index ; orphans never do.
    Also drop frames whose episode_index has no metadata row.
    Return (kept frames sorted by index, {"orphan": n, "unknown_episode": m}).
    Hash join on episode_index: time O(e + n log n) (the sort), space O(e).
    """
    # Hash index on the small table.
    start = {e["episode_index"]: e["dataset_from_index"] for e in episodes}
    kept, stats = [], {"orphan": 0, "unknown_episode": 0}
    for f in frames:
        s = start.get(f["episode_index"])
        if s is None:
            stats["unknown_episode"] += 1
        elif f["index"] != s + f["frame_index"]:
            stats["orphan"] += 1
        else:
            kept.append(f)
    kept.sort(key=lambda f: f["index"])
    return kept, stats


# ===========================================================================
# 5. Summarize a high-rate sensor inside labelled action segments
# ===========================================================================
def force_per_segment(
    segments: list[dict], ts: list[float], force: list[tuple[float, float, float]]
) -> list[dict]:
    """
    segments: [{"segment_index", "text", "start", "end"}] in seconds (e.g. "insert peg").
    ts, force: a ~1 kHz force/torque stream; ts sorted ascending, force[i] = (fx, fy, fz).
    For each segment: number of samples with start <= t < end, and the peak force magnitude
    sqrt(fx^2+fy^2+fz^2) inside it (None if no samples).
    Return rows sorted by segment_index: {"segment_index", "text", "samples", "peak_force_n"}.
    bisect to find each window: O(s log m + samples inside windows), space O(s).
    Follow-up: segments overlap heavily and there are millions of them -- what changes?
    """
    if len(ts) != len(force):
        raise ValueError("ts and force must have the same length")
    out = []
    for seg in sorted(segments, key=lambda s: s["segment_index"]):
        # bisect_left gives the first index with ts >= value, so [lo, hi) is exactly
        # the half-open window start <= t < end.
        lo, hi = bisect_left(ts, seg["start"]), bisect_left(ts, seg["end"])
        peak = None
        for fx, fy, fz in force[lo:hi]:
            m = math.sqrt(fx * fx + fy * fy + fz * fz)
            peak = m if peak is None or m > peak else peak
        out.append(
            {
                "segment_index": seg["segment_index"],
                "text": seg["text"],
                "samples": hi - lo,
                "peak_force_n": peak,
            }
        )
    return out


# ===========================================================================
# 6. Quality-gate episodes using a reward model's per-frame scores
# ===========================================================================
def flag_episodes(
    episodes: list[dict], min_success: float = 0.5, min_progress_range: float = 0.1
) -> list[dict]:
    """
    episodes: [{"episode_index", "task", "progress": [0..1 per sampled frame],
                "success": [0..1 per sampled frame]}]
    A healthy episode's progress climbs toward 1. Flag reasons (an episode can have several):
      "no_scores"     -- progress or success list missing/empty
      "low_success"   -- final success < min_success  (likely failed: review before training)
      "flat_progress" -- max(progress) - min(progress) < min_progress_range
                         (stalled, or the task text is wrong / mislabeled)
    Return only flagged episodes: [{"episode_index", "task", "reasons": [...]}], by episode_index.
    Time O(total scores), space O(flagged).
    """
    out = []
    for e in sorted(episodes, key=lambda e: e["episode_index"]):
        # `or []` turns both a missing key and an explicit None into an empty list.
        p, s = e.get("progress") or [], e.get("success") or []
        if not p or not s:
            reasons = ["no_scores"]
        else:
            reasons = []
            if s[-1] < min_success:
                reasons.append("low_success")
            if max(p) - min(p) < min_progress_range:
                reasons.append("flat_progress")
        if reasons:
            out.append({"episode_index": e["episode_index"], "task": e.get("task"), "reasons": reasons})
    return out


# ===========================================================================
# 7. Hand-visibility stats from per-frame hand detections
# ===========================================================================
def hand_visibility(frames: list[dict], min_conf: float = 0.5) -> dict[int, dict[str, Any]]:
    """
    frames: [{"episode_index", "frame_index",
              "hands": [{"handedness": "left"|"right"|"unknown", "confidence": float}, ...] or None}]
    Only detections with confidence >= min_conf count.
    Per episode (frames sorted by frame_index):
      "frames"            -- number of frames
      "any_hand_frac"     -- fraction of frames with >= 1 confident hand
      "both_hands_frac"   -- fraction with a confident "left" AND a confident "right"
      "longest_gap"       -- longest run of consecutive frames with no confident hand
    Fractions rounded to 3 decimals. Time O(n log n), space O(n).
    Useful for curation: "egocentric clips where both hands are visible > 80% of the time".
    """
    by_ep: dict[int, list[dict]] = defaultdict(list)
    for f in frames:
        by_ep[f["episode_index"]].append(f)

    out = {}
    for ep in sorted(by_ep):
        rows = sorted(by_ep[ep], key=lambda r: r["frame_index"])
        any_n = both_n = gap = longest = 0
        for r in rows:
            # Set of confidently-detected sides on this frame. `or []` / `or 0`
            # tolerate hands=None and confidence=None.
            sides = {
                h.get("handedness")
                for h in (r.get("hands") or [])
                if (h.get("confidence") or 0) >= min_conf
            }
            if sides:
                any_n += 1
                gap = 0  # a visible hand ends the current gap
            else:
                gap += 1
                longest = max(longest, gap)
            if {"left", "right"} <= sides:  # subset test: both sides present
                both_n += 1
        n = len(rows)
        out[ep] = {
            "frames": n,
            "any_hand_frac": round(any_n / n, 3),
            "both_hands_frac": round(both_n / n, 3),
            "longest_gap": longest,
        }
    return out


# ===========================================================================
# Tests
# ===========================================================================
def _tests() -> None:
    # 1 -- two episodes; ep1's first frame must NOT diff against ep0's last frame
    frames = [
        {"episode_index": 0, "frame_index": 1, "state": [1.0, 0.0]},
        {"episode_index": 0, "frame_index": 0, "state": [0.0, 0.0]},
        {"episode_index": 1, "frame_index": 0, "state": [50.0, 50.0]},
        {"episode_index": 1, "frame_index": 1, "state": [50.0, 49.0]},
    ]
    energy, scale = motion_energy(frames)
    # deltas: ep0 -> (1,0); ep1 -> (0,-1). RMS per dim = sqrt(1/2) each.
    assert all(abs(s - math.sqrt(0.5)) < 1e-12 for s in scale)
    assert energy[(0, 0)] == 0.0 and energy[(1, 0)] == 0.0  # no cross-episode spike
    assert abs(energy[(0, 1)] - math.sqrt(2)) < 1e-12 and abs(energy[(1, 1)] - math.sqrt(2)) < 1e-12
    assert motion_energy([]) == ({}, [])

    # 2
    e = [0.0, 0.5, 0.0, 0.5, 0.5, 0.5, 0.0, 0.5, 0.5]
    assert is_active(e, threshold=0.1, run=3) == [False, False, False, True, True, True, False, False, False]
    assert is_active(e, threshold=0.1, run=1) == [x > 0.1 for x in e]
    assert is_active([], 0.1) == []

    # 3 -- fps 4, pad 0.25 s -> 1 frame
    rows = [{"episode_index": 7, "frame_index": i, "is_active": i in (3, 4, 5)} for i in range(10)]
    rows += [{"episode_index": 2, "frame_index": i, "is_active": False} for i in range(4)]
    rows += [{"episode_index": 9, "frame_index": i, "is_active": i == 0} for i in range(3)]
    w = {r["episode_index"]: r for r in trim_windows(rows, fps=4)}
    assert (w[7]["start_frame"], w[7]["end_frame"], w[7]["kept_frames"]) == (2, 6, 5)
    assert abs(w[7]["trim_fraction"] - 0.5) < 1e-12 and w[7]["start_ts"] == 0.5
    assert w[2]["never_active"] and (w[2]["start_frame"], w[2]["end_frame"]) == (0, 3)
    assert w[9]["start_frame"] == 0  # clipped at 0
    assert [r["episode_index"] for r in trim_windows(rows, fps=4)] == [2, 7, 9]

    # 4
    eps = [{"episode_index": 0, "dataset_from_index": 0}, {"episode_index": 1, "dataset_from_index": 3}]
    fr = [
        {"index": 0, "episode_index": 0, "frame_index": 0},
        {"index": 1, "episode_index": 0, "frame_index": 1},
        {"index": 2, "episode_index": 0, "frame_index": 0},  # orphan re-recording
        {"index": 4, "episode_index": 1, "frame_index": 1},
        {"index": 3, "episode_index": 1, "frame_index": 0},
        {"index": 9, "episode_index": 5, "frame_index": 0},  # no metadata
    ]
    kept, stats = drop_orphan_frames(eps, fr)
    assert [f["index"] for f in kept] == [0, 1, 3, 4] and stats == {"orphan": 1, "unknown_episode": 1}

    # 5
    ts = [0.0, 0.5, 1.0, 1.5, 2.0]
    force = [(0, 0, 1), (3, 4, 0), (0, 0, 2), (0, 0, 0), (0, 0, 9)]
    segs = [
        {"segment_index": 1, "text": "insert", "start": 1.0, "end": 2.0},
        {"segment_index": 0, "text": "reach", "start": 0.0, "end": 1.0},
        {"segment_index": 2, "text": "idle", "start": 3.0, "end": 4.0},
    ]
    got = force_per_segment(segs, ts, force)
    assert [(g["segment_index"], g["samples"], g["peak_force_n"]) for g in got] == [
        (0, 2, 5.0),
        (1, 2, 2.0),
        (2, 0, None),
    ]

    # 6
    eps6 = [
        {"episode_index": 1, "task": "bowl", "progress": [0.1, 0.2, 0.8], "success": [0.1, 0.2, 0.49]},
        {"episode_index": 0, "task": "drawer", "progress": [0.1, 0.5, 0.9], "success": [0.1, 0.5, 0.97]},
        {"episode_index": 2, "task": "wrong text", "progress": [0.02, 0.03, 0.05], "success": [0.1, 0.1, 0.1]},
        {"episode_index": 3, "task": "x", "progress": [], "success": None},
    ]
    assert flag_episodes(eps6) == [
        {"episode_index": 1, "task": "bowl", "reasons": ["low_success"]},
        {"episode_index": 2, "task": "wrong text", "reasons": ["low_success", "flat_progress"]},
        {"episode_index": 3, "task": "x", "reasons": ["no_scores"]},
    ]

    # 7
    L, R = {"handedness": "left", "confidence": 0.9}, {"handedness": "right", "confidence": 0.9}
    weak = {"handedness": "right", "confidence": 0.2}
    hv = hand_visibility(
        [
            {"episode_index": 0, "frame_index": 3, "hands": [L, R]},
            {"episode_index": 0, "frame_index": 0, "hands": [L, R]},
            {"episode_index": 0, "frame_index": 1, "hands": [weak]},
            {"episode_index": 0, "frame_index": 2, "hands": None},
            {"episode_index": 1, "frame_index": 0, "hands": [R]},
        ]
    )
    assert hv[0] == {"frames": 4, "any_hand_frac": 0.5, "both_hands_frac": 0.5, "longest_gap": 2}
    assert hv[1] == {"frames": 1, "any_hand_frac": 1.0, "both_hands_frac": 0.0, "longest_gap": 0}

    print("All 7 robot-episode problems pass.")


if __name__ == "__main__":
    _tests()
