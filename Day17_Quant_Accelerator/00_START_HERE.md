# DAY 17: Mon 16 Nov 2026: THE IN-SAMPLE RUN
## Describe the past honestly, count every trial, and don't touch 2019+.

The plan said "first 70%". **Overruled on Day 12: the boundary is 2019-01-01.** In-sample = 2007-09 → 2018-12-31. The holdout isn't even in this ZIP.

| Time | Block | What | Files |
|---|---|---|---|
| 20 min | Drill | Zetamac + "Sharpe 0.5, 10 yrs daily: SE?" × 5 (answer ≈ √((1 + 0.5²/2)/10) ≈ 0.34) | |
| 30 min | Read | Ledoit & Wolf (2008), sections 1 to 3 + the conclusion | 01_ |
| 20 min | Watch | StatQuest bootstrapping + standard error | links |
| 20 min | Re-read | Lo (2002) on serial correlation (Day 11 kit) | |
| 15 min | Predict | Write down your guesses for primary Sharpe, vol ratio and DD difference BEFORE running | |
| 40 min | Run | `python is_report.py --trade <your NIFTYBEES> --prereg <prereg.md> --lock <LOCK.txt>`, then `pytest test_is_report.py`, then `python crosscheck_arch.py` | 03_ |
| 45 min | Write | `IS-report-writeup.md` (1 page) + checklist | 04_ |
| 15 min | Log | trial-log.csv rows for all 4 runs; decide the N you'll use for DSR | 04_ |
| 20 min | Problems | 10 problems | 05_ |
≈ 3.9 h.

## What the demo shows (index stand-in, OECD cash, after costs, aligned start 2008-09-01)
| | CAGR | Vol | Sharpe xs cash | Max DD | Trades |
|---|---|---|---|---|---|
| Buy & hold | 8.9% | 20.7% | 0.19 | −43.9% | 2 |
| Faber 8m (grid) | 9.3% | 14.0% | 0.22 | −24.3% | 22 |
| **Faber 10m (primary)** | 8.6% | 14.2% | 0.18 | −25.6% | 22 |
| Faber 12m (grid) | 7.4% | 13.1% | 0.09 | −25.6% | 14 |

- **Sharpe:** 0.18, 90% band −0.32 to +0.64. Indistinguishable from buy & hold. No alpha, as pre-registered.
- **Vol ratio:** 0.69 (0.56 to 0.81). **DD shallower:** +18 pp, P = 94%. The risk claim holds in-sample.
- **Warm-up trap caught:** started at the data's first day, the DD edge reads +34 pp, because the filter was in cash for 10 months by construction while buy & hold ate the 2008 crash. The script now starts every run on the first day all variants can act.
- **Effective N of the 3 Faber lengths = 1.15.** They're almost one bet.
- Faber's longest time underwater (1,289 days) is longer than buy & hold's. Remember that on Day 21.

## Mentor's rulings
1. Today you describe, you don't decide. No parameter changes; 8m "looking better" is noise (problem 4).
2. Report the aligned numbers. Show the unaligned DD once, labelled as an artifact.
3. Every headline number carries a band, or it's marked "point only".
4. Decide your DSR N **today**, in writing, before Day 20. Default: total trials in the family from your log.
5. Cash leg: the OECD series is provisional for 2007 to 2012. Swap in RBI 91-day T-bills before Day 20 and log it.
6. Write your Day 20 predictions in the write-up. That's what turns Day 20 into a test.

Send me: IS_report.md + your 1-page write-up + checklist + trial-log rows + the 10 problems + training-log row.
Day 18 (Tue 17 Nov): walk-forward and the parameter-stability heat map.
