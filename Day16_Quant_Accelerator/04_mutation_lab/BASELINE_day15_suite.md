# Baseline: the Day 15 suite (17 tests) vs the CLEAN Day 15 engine
`python mutate.py <clean engine.py> test_engine.py` → **51/90 mutants killed = 57%** (451 s in the sandbox).
Run this on the clean Day 15 engine, not on v2.1. These survivors aren't today's planted bugs; they're the suite's blind spots.

| Area | Survivors | Meaning | Verdict |
|---|---|---|---|
| `metrics()` (lines 183–187) | 18 | CAGR, vol, Sharpe and max-DD formulas can be flipped (`* → /`, `min → max`) and no test notices | **real gap**: the numbers you'll report on Day 20 are untested |
| holdout seal `load_frame` (line 194) | 2 | `>=` → `>` lets 2019-01-01 itself through; `max → min` disables the seal entirely | **real gap**: the seal protecting your OOS has no test |
| no-trade band / min-trade (141–143) | 6 | thresholds `<` vs `<=`, even `want + cur`, survive | gap: band edge cases unpinned |
| buy sizing loop (148–154) | 6 | `floor → ceil`, `q / 0.999` survive (the fee loop repairs them) | partly equivalent; decide each |
| Faber `iloc[:-1] → [:]` (60) | 1 | Faber would use today's close. Not a leak (it's known at the close) but it **changes your pre-registered rule** | gap: pin the spec |
| `>` vs `>=` on prices, vol, cash (33, 90, 102, 166, 174) | 5 | mostly equivalent mutants (prices never 0 here) | equivalent: document and move on |

Target after today: **≥ 80%**, every survivor either killed or written down as equivalent with a one-line reason.
