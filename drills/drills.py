"""
Standard-Library Drills - Time-Series and Sequence Shapes
=========================================================
Eleven problems that complement robot_episodes/robot_episode_problems.py:
sessionize, run-length segments, merge intervals, nearest timestamp (bisect),
sliding window (deque), resample-to-grid, validated per-episode summaries,
hash-based split, cosine top-k, rolling average, pivot.

This is a WORKBOOK. Problems 2, 7 and 11 are solved here; the rest raise
NotImplementedError until you fill them in. Reference answers are in
solutions.py.

How to use (one problem = 25 minutes):
  1. Read ONLY the docstring. Say the edge cases out loud. Say the Big-O before typing.
  2. Write 2 tiny examples of your own with expected outputs, as asserts.
  3. Implement. Run:   python test_drills.py <problem_number>   (no number = all)
  4. Only after it passes, or after 25 minutes, open solutions.py for that one problem.

Vocabulary (LeRobot-style datasets):
  episode = one recorded attempt;  frame_index restarts at 0 per episode;  fps = frames/second;
  timestamps are FLOAT SECONDS;  state = list of joint floats;  camera = a video stream name.
"""

from __future__ import annotations

import math
from collections import defaultdict


# ===========================================================================
# 1. Sessionize events per user by idle gap            (sort, then sweep)
# ===========================================================================
def sessionize(events: list[dict], gap_s: float) -> dict[str, list[list[float]]]:
    """
    events: [{"user": str, "ts": float}], UNSORTED, users interleaved.
    A new session starts when the gap to the previous event of the SAME user exceeds gap_s.
    Return {user: [[ts, ts, ...], [ts, ...], ...]} with timestamps ascending inside each session,
    sessions in time order.  A user with one event has one session of one timestamp.
    Empty input -> {}.
    Time O(n log n) (the per-user sort), space O(n).
    """
    raise NotImplementedError


# ===========================================================================
# 2. Per-frame booleans -> contiguous segments          (run-length encoding)
# ===========================================================================
def active_segments(flags: list[bool], fps: float) -> list[dict]:
    """
    flags: one bool per frame of ONE episode, in frame order (e.g. is_active).
    Return one dict per maximal run of True:
      {"start_frame", "end_frame" (inclusive), "start_s" = start_frame/fps, "end_s" = (end_frame+1)/fps}
    so that end_s - start_s is the segment duration.  Empty flags or all-False -> [].
    fps <= 0 -> ValueError.   Time O(n), space O(segments).
    """
    if fps <= 0:
        raise ValueError("fps must be > 0")
    start = None  # index where the current run of True began, or None if not in a run
    segs = []

    for i, flag in enumerate(flags):
        if flag and start is None:
            start = i  # a run begins
        elif not flag and start is not None:
            # The run ended on the previous frame. end_s uses i (= end_frame + 1)
            # so the segment covers the full duration of its last frame.
            segs.append({"start_frame": start, "end_frame": i - 1, "start_s": start / fps, "end_s": i / fps})
            start = None
    # A run that is still open when the input ends must be closed too.
    if start is not None:
        segs.append(
            {"start_frame": start, "end_frame": len(flags) - 1, "start_s": start / fps, "end_s": len(flags) / fps}
        )

    return segs


# ===========================================================================
# 3. Merge overlapping / touching intervals
# ===========================================================================
def merge_intervals(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """
    intervals: [(start, end)] in any order; closed intervals; touching ones ([0,5] and [5,9]) MERGE.
    Return merged, sorted by start, as tuples.  start > end -> ValueError.  Empty -> [].
    Time O(n log n), space O(n).
    """
    raise NotImplementedError


# ===========================================================================
# 4. Nearest sensor reading for each camera frame       (bisect)
# ===========================================================================
def nearest_sensor(frame_ts: list[float], sensor_ts: list[float], max_gap: float) -> list[int | None]:
    """
    sensor_ts is SORTED ascending (a ~1 kHz stream).  frame_ts is any order.
    For each frame timestamp return the INDEX into sensor_ts of the closest reading,
    or None if the closest is farther than max_gap.  Ties -> the smaller index.
    Empty sensor_ts -> all None.
    Time O(f log s), space O(f).  (A linear scan is O(f*s): say why that's worse at 1 kHz.)
    """
    raise NotImplementedError


# ===========================================================================
# 5. Burst detection with a sliding time window         (deque)
# ===========================================================================
def burst_alerts(times: list[float], window_s: float, k: int) -> list[float]:
    """
    times: event timestamps, any order.  Return the timestamps t at which, counting events in
    (t - window_s, t], there are >= k events.  Each qualifying t appears once, ascending.
    k < 1 or window_s <= 0 -> ValueError.  Time O(n log n) (sort) + O(n) sweep, space O(k).
    """
    raise NotImplementedError


# ===========================================================================
# 6. Resample an irregular stream onto a fixed grid     (two pointers, forward fill)
# ===========================================================================
def resample(
    samples: list[tuple[float, float]], t0: float, t1: float, step: float
) -> list[tuple[float, float | None]]:
    """
    samples: [(t, value)] any order, irregular.  Grid: t0, t0+step, ..., <= t1.
    At each grid time return the value of the LAST sample with t <= grid time (forward fill),
    or None if no sample has happened yet.  step <= 0 -> ValueError.
    Return [(grid_t, value)].  Time O(n log n + g), space O(g).
    Follow-up to be ready for: why can float accumulation (t += step) drift, and what's the fix?
    """
    raise NotImplementedError


# ===========================================================================
# 7. Validated per-episode summaries                    (parse/clean + group)
# ===========================================================================
def bad_state(st) -> bool:
    """True if `st` is not a non-empty list of finite numbers.

    Rejects: not a list, empty list, any element that is not int/float
    (so None and strings fail), and NaN. Note bool is a subclass of int, which
    is accepted here; tighten the check if that matters.
    """
    return not isinstance(st, list) or not st or any(not isinstance(x, (int, float)) or math.isnan(x) for x in st)


def episode_summaries(frames: list) -> tuple[list[dict], int]:
    """
    frames: list of MESSY records.  A valid record is a dict with int episode_index, int frame_index >= 0,
    and a non-empty list `state` of finite numbers (no None, no NaN, no strings).  Anything else is dropped.
    Return (summaries sorted by episode_index, dropped_count) where each summary is
      {"episode_index", "frames", "first_frame", "last_frame",
       "has_gaps": True if frame indices are not exactly first..last with no duplicates,
       "dims_consistent": True if every state in the episode has the same length}
    Time O(n log n), space O(n).
    """
    by_ep = defaultdict(list)
    dropped_count = 0
    for r in frames:
        # Guard the type BEFORE calling .get, otherwise None / "junk" would raise.
        if not isinstance(r, dict):
            dropped_count += 1
            continue
        ep, fi, st = r.get("episode_index"), r.get("frame_index"), r.get("state")
        if not isinstance(ep, int) or not isinstance(fi, int) or fi < 0 or bad_state(st):
            dropped_count += 1
            continue
        by_ep[ep].append((fi, st))

    out = []
    for ep in sorted(by_ep):
        rows = sorted(by_ep[ep])  # tuples sort by frame_index first
        idx = [fi for fi, _ in rows]
        dims = {len(st) for _, st in rows}
        out.append(
            {
                "episode_index": ep,
                "frames": len(rows),
                "first_frame": idx[0],
                "last_frame": idx[-1],
                # Contiguous AND unique <=> span equals count AND no duplicates.
                "has_gaps": (idx[-1] - idx[0] + 1) != len(idx) or len(set(idx)) != len(idx),
                "dims_consistent": len(dims) == 1,
            }
        )
    return out, dropped_count


# ===========================================================================
# 8. Deterministic train/val/test split by episode      (hashing, no leakage)
# ===========================================================================
def split_by_episode(
    frames: list[dict], val_frac: float, test_frac: float, salt: str = ""
) -> dict[str, list[dict]]:
    """
    Every frame of an episode must land in the SAME split (adjacent frames are near-duplicates).
    The split must be deterministic across runs and machines and must not depend on input order:
    hash f"{salt}:{episode_index}" with hashlib.sha1, take the first 8 hex chars as an int,
    u = int / 0xFFFFFFFF in [0,1];  u < test_frac -> "test"; < test_frac+val_frac -> "val"; else "train".
    Return {"train": [...], "val": [...], "test": [...]} preserving input order within each.
    Fractions negative or summing >= 1 -> ValueError.  Time O(n), space O(n).
    Why not random.random()?  Why not Python's built-in hash()?
    """
    raise NotImplementedError


# ===========================================================================
# 9. Cosine top-k matches, pure Python                   (embedding search)
# ===========================================================================
def top_k_matches(queries: list[list[float]], docs: list[list[float]], k: int) -> list[list[tuple[int, float]]]:
    """
    queries, docs: lists of equal-length float vectors.  For each query return the k docs with the
    highest cosine similarity as [(doc_index, score)], score rounded to 6 dp, highest first,
    ties -> smaller index first.  A zero vector (norm 0) matches nothing / is never matched.
    Time O(q * d * D + q * d log d), space O(d * D) for the normalised docs.
    """
    raise NotImplementedError


# ===========================================================================
# 10. Rolling average per video, flag quality drops      (running sum)
# ===========================================================================
def quality_drops(scores: dict[str, list[float]], window: int, min_avg: float) -> dict[str, list[int]]:
    """
    scores: {video_id: [per-frame score]} in frame order.  For each video return the frame indices i
    (i >= window-1) where the mean of the last `window` scores ending at i is < min_avg.
    Must be O(total frames) -- a running sum, NOT sum(slice) per frame.  window < 1 -> ValueError.
    """
    raise NotImplementedError


# ===========================================================================
# 11. Pivot long rows into a wide table                  (reshape, fill 0)
# ===========================================================================
def pivot(rows: list[dict]) -> list[dict]:
    """
    rows: [{"episode": int, "camera": str, "frames": int}],
    possibly several rows per (episode, camera) -> SUM them.
    Return one dict per episode, sorted by episode, with a column per camera (cameras sorted),
    missing (episode, camera) filled with 0:  {"episode": 3, "cam_left": 120, "cam_wrist": 0}
    Time O(n + e*c), space O(e*c).
    """
    # Output columns: every camera that appears anywhere, in a stable order.
    cams = sorted({r["camera"] for r in rows})

    # Sum frames per (episode, camera) cell.
    cell = {}
    for r in rows:
        key = (r["episode"], r["camera"])
        cell[key] = cell.get(key, 0) + r["frames"]

    # One row per episode with EVERY camera column present (0 when absent).
    episodes = sorted({r["episode"] for r in rows})
    out = []
    for ep in episodes:
        row = {"episode": ep}
        for c in cams:
            row[c] = cell.get((ep, c), 0)
        out.append(row)
    return out
