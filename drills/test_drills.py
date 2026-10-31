"""
Tests for drills.py
===================
    python test_drills.py                      -> run all 11
    python test_drills.py 4                    -> problem 4 only
    python test_drills.py 2 7 11               -> several
    DRILLS=solutions python test_drills.py     -> check the reference solutions instead

Each test prints PASS / FAIL (with the failing assertion) / "not attempted" for a
stub that still raises NotImplementedError, and keeps going to the next one.
"""

from __future__ import annotations

import importlib
import os
import sys
import traceback

# Make the module importable no matter which directory the script is run from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

M = importlib.import_module(os.environ.get("DRILLS", "drills"))


def t1():
    ev = [
        {"user": "ana", "ts": 10.0},
        {"user": "ana", "ts": 70.0},
        {"user": "bo", "ts": 5.0},
        {"user": "ana", "ts": 4000.0},
        {"user": "bo", "ts": 20.0},
        {"user": "ana", "ts": 4010.0},
        {"user": "bo", "ts": 9000.0},
        {"user": "cy", "ts": 1.0},
        {"user": "ana", "ts": 0.0},
    ]
    got = M.sessionize(ev, gap_s=1800)
    assert got["ana"] == [[0.0, 10.0, 70.0], [4000.0, 4010.0]], got["ana"]
    assert got["bo"] == [[5.0, 20.0], [9000.0]], got["bo"]
    assert got["cy"] == [[1.0]]
    assert M.sessionize([], 10) == {}
    # a gap EQUAL to the limit stays in the same session
    assert M.sessionize([{"user": "x", "ts": 1.0}, {"user": "x", "ts": 11.0}], gap_s=10) == {"x": [[1.0, 11.0]]}


def t2():
    f = [False, True, True, False, False, True, False, True]
    got = M.active_segments(f, fps=4)
    assert [(s["start_frame"], s["end_frame"]) for s in got] == [(1, 2), (5, 5), (7, 7)], got
    assert got[0]["start_s"] == 0.25 and got[0]["end_s"] == 0.75
    assert M.active_segments([], 4) == [] and M.active_segments([False, False], 4) == []
    assert [(s["start_frame"], s["end_frame"]) for s in M.active_segments([True, True], 4)] == [(0, 1)]
    try:
        M.active_segments([True], 0)
        assert False, "fps=0 must raise"
    except ValueError:
        pass


def t3():
    assert M.merge_intervals([(5, 9), (0, 5), (12, 13)]) == [(0, 9), (12, 13)]
    assert M.merge_intervals([(1, 4), (2, 3)]) == [(1, 4)]  # contained
    assert M.merge_intervals([(1, 2), (3, 4)]) == [(1, 2), (3, 4)]  # disjoint
    assert M.merge_intervals([]) == []
    assert M.merge_intervals([(2, 2)]) == [(2, 2)]
    try:
        M.merge_intervals([(3, 1)])
        assert False, "start>end must raise"
    except ValueError:
        pass


def t4():
    s = [0.0, 0.1, 0.2, 0.3]
    assert M.nearest_sensor([0.13, 0.0, 0.35, 0.251], s, max_gap=0.06) == [1, 0, 3, 3]  # 0.251 nearer 0.3
    assert M.nearest_sensor([0.15], s, max_gap=1.0) == [1]  # exact tie -> smaller index
    assert M.nearest_sensor([9.0], s, max_gap=0.5) == [None]  # too far
    assert M.nearest_sensor([0.1], [], max_gap=1.0) == [None]
    assert M.nearest_sensor([], s, 1.0) == []


def t5():
    t = [0, 10, 20, 30, 100, 101, 102, 103]
    assert M.burst_alerts(t, window_s=25, k=3) == [20, 30, 102, 103], M.burst_alerts(t, 25, 3)
    assert M.burst_alerts([5, 1, 3], window_s=10, k=3) == [5]  # unsorted input
    assert M.burst_alerts([1, 2], 10, 3) == []
    assert M.burst_alerts([], 10, 1) == []
    try:
        M.burst_alerts([1], 0, 1)
        assert False
    except ValueError:
        pass


def t6():
    s = [(0.0, 1.0), (0.25, 2.0), (1.0, 3.0)]
    assert M.resample(s, 0.0, 1.0, 0.5) == [(0.0, 1.0), (0.5, 2.0), (1.0, 3.0)]
    assert M.resample([(0.3, 7.0)], 0.0, 0.6, 0.3) == [(0.0, None), (0.3, 7.0), (0.6, 7.0)]  # None before first
    assert M.resample([(0.9, 2.0), (0.1, 1.0)], 0.0, 1.0, 1.0) == [(0.0, None), (1.0, 2.0)]  # unsorted input
    assert M.resample([], 0.0, 0.2, 0.1) == [(0.0, None), (0.1, None), (0.2, None)]
    try:
        M.resample(s, 0, 1, 0)
        assert False
    except ValueError:
        pass


def t7():
    fr = [
        {"episode_index": 1, "frame_index": 1, "state": [0.1, 0.2]},
        {"episode_index": 1, "frame_index": 0, "state": [0.0, 0.0]},
        {"episode_index": 1, "frame_index": 3, "state": [0.0, 0.0]},  # gap at 2
        {"episode_index": 0, "frame_index": 0, "state": [1.0]},
        {"episode_index": 0, "frame_index": 1, "state": [1.0, 2.0]},  # dims differ
        {"episode_index": 2, "frame_index": 0, "state": [float("nan")]},  # dropped: NaN
        {"episode_index": 2, "frame_index": 1, "state": []},  # dropped: empty
        {"episode_index": "3", "frame_index": 0, "state": [1.0]},  # dropped: str episode
        {"episode_index": 3, "frame_index": -1, "state": [1.0]},  # dropped: negative
        {"episode_index": 3, "frame_index": 0, "state": [1.0, None]},  # dropped: None inside
        None,
        "junk",
    ]
    got, dropped = M.episode_summaries(fr)
    assert dropped == 7, dropped
    assert [g["episode_index"] for g in got] == [0, 1]
    assert got[1] == {
        "episode_index": 1,
        "frames": 3,
        "first_frame": 0,
        "last_frame": 3,
        "has_gaps": True,
        "dims_consistent": True,
    }, got[1]
    assert got[0]["has_gaps"] is False and got[0]["dims_consistent"] is False
    assert M.episode_summaries([]) == ([], 0)


def t8():
    fr = [{"episode_index": e, "frame_index": i} for e in range(50) for i in range(3)]
    sp = M.split_by_episode(fr, val_frac=0.2, test_frac=0.2)
    assert sum(len(v) for v in sp.values()) == len(fr)
    for name, rows in sp.items():  # whole episodes stay together
        eps = {r["episode_index"] for r in rows}
        assert all(sum(1 for r in rows if r["episode_index"] == e) == 3 for e in eps), name
    sp2 = M.split_by_episode(list(reversed(fr)), 0.2, 0.2)
    for name in sp:  # order-independent membership
        assert {r["episode_index"] for r in sp[name]} == {r["episode_index"] for r in sp2[name]}
    assert 10 <= len({r["episode_index"] for r in sp["test"]}) <= 30  # roughly 20% of 50 episodes
    try:
        M.split_by_episode(fr, 0.6, 0.5)
        assert False
    except ValueError:
        pass


def t9():
    docs = [[1, 0], [0, 1], [1, 1], [0, 0]]
    got = M.top_k_matches([[1, 0], [1, 1]], docs, k=2)
    assert got[0] == [(0, 1.0), (2, 0.707107)], got[0]
    assert got[1][0][0] == 2 and got[1][0][1] == 1.0 and {got[1][1][0]} <= {0, 1}
    assert M.top_k_matches([[0, 0]], docs, 2) == [[]]  # zero query matches nothing
    assert M.top_k_matches([[1, 0]], [[0, 0]], 2) == [[]]  # zero doc never matched
    assert M.top_k_matches([[1, 0]], docs, 10)[0][0] == (0, 1.0)  # k > docs is fine
    assert M.top_k_matches([], docs, 2) == []


def t10():
    sc = {"v1": [1, 1, 1, 0, 0, 0, 1], "v2": [0.2, 0.2], "v3": []}
    got = M.quality_drops(sc, window=3, min_avg=0.5)
    # windows ending at 4: (1,0,0)=.33   5: (0,0,0)=0   6: (0,0,1)=.33
    assert got["v1"] == [4, 5, 6], got["v1"]
    assert got["v2"] == [] and got["v3"] == []
    assert M.quality_drops({"a": [0, 0, 0]}, window=1, min_avg=0.5)["a"] == [0, 1, 2]
    try:
        M.quality_drops(sc, 0, 0.5)
        assert False
    except ValueError:
        pass


def t11():
    rows = [
        {"episode": 1, "camera": "wrist", "frames": 10},
        {"episode": 0, "camera": "left", "frames": 5},
        {"episode": 1, "camera": "left", "frames": 7},
        {"episode": 1, "camera": "wrist", "frames": 2},
    ]
    assert M.pivot(rows) == [{"episode": 0, "left": 5, "wrist": 0}, {"episode": 1, "left": 7, "wrist": 12}]
    assert M.pivot([]) == []


TESTS = {1: t1, 2: t2, 3: t3, 4: t4, 5: t5, 6: t6, 7: t7, 8: t8, 9: t9, 10: t10, 11: t11}

if __name__ == "__main__":
    which = [int(a) for a in sys.argv[1:]] or sorted(TESTS)
    ok = 0
    for n in which:
        try:
            TESTS[n]()
            print(f"{n:2d} PASS")
            ok += 1
        except NotImplementedError:
            print(f"{n:2d} ---- not attempted")
        except AssertionError as e:
            print(f"{n:2d} FAIL  {e if str(e) else ''}")
            tb = traceback.extract_tb(sys.exc_info()[2])[-1]
            print(f"      at test line {tb.lineno}: {tb.line}")
        except Exception as e:
            print(f"{n:2d} ERROR {type(e).__name__}: {e}")
    print(f"\n{ok}/{len(which)} passed")
