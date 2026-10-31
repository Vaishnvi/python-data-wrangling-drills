# Python Data-Wrangling Drills

Interview-style practice in **pure Python (standard library only)**: take a list of
in-memory records, clean it, group it, join it, reshape it, and return the answer
with a stated Big-O. Every file is runnable, heavily commented, and either ends with
its expected output or verifies itself with asserts.

## Layout

| Folder | What is in it |
|--------|---------------|
| [`fundamentals/`](fundamentals) | Warm-ups: comprehensions, `sorted(key=...)`, `defaultdict` / `Counter` |
| [`problem_families/`](problem_families) | The recurring shapes: parse & clean, JSON lines, dedupe, hash join, sessionize, pivot |
| [`exam/`](exam) | A timed 12-question mock on one event log, with the wrong first attempts kept as comments |
| [`robot_episodes/`](robot_episodes) | Seven harder problems on robot-episode data (motion energy, trimming, orphan frames, sensor windows, quality gates, hand visibility), self-tested |
| [`drills/`](drills) | An 11-problem workbook with stubs, a test runner, and reference solutions |

### fundamentals/
| File | Topic |
|------|-------|
| `01_comprehensions_filtering.py` | list / set / dict comprehensions, filter vs conditional expression |
| `02_sorting.py` | `sorted()` with lambdas, multi-key and mixed-direction sorts |
| `03_counter_defaultdict.py` | group-by with `defaultdict(list)`, counting with `Counter`, reducing groups |

### problem_families/
| File | Topic |
|------|-------|
| `01_parse_and_clean.py` | safe `.get()`, `to_float()` that never raises, keep good rows and count dropped |
| `02_parse_json_lines.py` | `str.split/strip`, `json.loads` in try/except, rejecting non-dict JSON |
| `03_dedupe.py` | exact-row dedupe with a tuple key, latest-per-key, first-per-(key, key) |
| `04_join.py` | hash join (inner and left), key normalisation, duplicate keys as updates |
| `05_sessionize.py` | `datetime` / `timedelta`, group-sort-sweep sessionization |
| `06_pivot.py` | long-to-wide reshape with summed cells and a fill value |

### drills/
```bash
python drills/test_drills.py            # run all 11 against your drills.py
python drills/test_drills.py 4          # one problem
DRILLS=solutions python drills/test_drills.py   # check the reference solutions
```
`drills.py` has problems 2, 7 and 11 solved; the others raise `NotImplementedError`
until you fill them in. Suggested rhythm: read only the docstring, say the edge cases
and the Big-O out loud, write two asserts of your own, implement, then and only then
open `solutions.py`.

## Running

Python 3.9+ and no third-party packages.

```bash
git clone https://github.com/Vaishnvi/python-data-wrangling-drills.git
cd python-data-wrangling-drills
python fundamentals/01_comprehensions_filtering.py
python robot_episodes/robot_episode_problems.py
python drills/test_drills.py
```

Every script can be run from any working directory.

## Conventions

- A module docstring at the top of each file states the problem shape, the tools used and the complexity.
- `# ----` banners separate the sub-questions within a file.
- Inline comments explain the *why* (edge cases, gotchas, why one container over another), not just the what.
- Drill scripts end with an `Expected output` block captured from an actual run; the problem sets verify themselves with asserts instead.
