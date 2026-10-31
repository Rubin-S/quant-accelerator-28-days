# DAY 16: Sun 15 Nov 2026: BUG HUNT (I planted 3 bugs in your engine)

`03_bug_hunt/engine.py` is "v2.1, small refactors for speed". It has **3 planted bugs**. The Day 15 suite turns red on 2 tests, but red tests don't tell you where or why, and one bug turns nothing red.
**Honour rule: don't diff against Day 15** until your report is in. Real bugs don't come with a clean copy.

| Time | Block | What | Files |
|---|---|---|---|
| 20 min | Drill | Zetamac + spot-the-bug: 5 one-line pandas snippets you write yourself (`shift`, `bfill`, `resample`, `iloc`) | |
| 30 min | Read | Zeller, *The Debugging Book*: Intro to Debugging chapter (link). `bug_hunt_protocol.md` | 02_ |
| 20 min | Read | Just et al. (2014), sections 1, 5, 7 (does mutation score mean anything?) | 01_ |
| 90 min | Hunt | Run the suite + the demo, observe, hypothesise, experiment. Log every step. | 03_, 05_ |
| 30 min | Fix | Failing test FIRST, then fix, for each bug | 03_ |
| 40 min | Mutation | `python mutate.py ../03_bug_hunt/engine.py ../03_bug_hunt/test_engine.py` on your FIXED engine; kill survivors | 04_ |
| 20 min | Write | `bug-report.md` | 05_ |
| 20 min | Problems | 10 problems | 06_ |
≈ 4.5 h. That's over budget, so cut the mutation block to 25 min if you need to.

## Hints (read one at a time, only when stuck for 20+ min)
<details><summary>Hint 1</summary>Two of the bugs live in the same class.</details>
<details><summary>Hint 2</summary>One bug is invisible in the P&L and the suite. Build a one-trade scenario and compute the cash by hand.</details>
<details><summary>Hint 3</summary>Look at `res.targets`, not just `res.weights`.</details>

## Mentor's rulings
- A bug counts only with a test that fails before the fix and passes after.
- Your Day 15 suite scores **57%** on mutation testing (`BASELINE_day15_suite.md`). Its biggest holes: `metrics()` and the **holdout seal**. Close the seal hole today: that's the one thing in the engine you can't undo.
- From now on, no engine change without a failing-first test and a mutation score that doesn't drop.
- `SEALED_answer_key.zip` is password-locked. Send me your bug report and I'll give you the password.

Send me: bug report, bug-hunt log, new tests, mutation score before → after, the 10 problems, and your training-log row.
