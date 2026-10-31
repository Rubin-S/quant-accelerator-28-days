# DAY 19: Wed 18 Nov 2026: STRESS TESTS
## Try to kill it before the holdout does

Data ≤ 2018-12-31 only. Day 20 (Thu 19 Nov) opens the holdout ONCE.

| Time | Block | What | Files |
|---|---|---|---|
| 20 min | Drill | Zetamac + "11 trades, best one = all the edge: what's the t-stat?" × 5 | |
| 30 min | Read | Hoffstein et al., *Rebalance Timing Luck* (intro, section 2, conclusion) | 01_ |
| 25 min | Read | Novy-Marx & Velikov intro + buy/hold spread section | 01_ |
| 25 min | Watch | neurotrader on permutation tests | RESOURCES |
| 15 min | Predict | Write down BEFORE running: which stress will hurt most? | |
| 45 min | Run | `python stress.py --trade <your NIFTYBEES> --vol-ratio-max <yours> --dd-edge-min <yours>`, then `pytest -q` | 03_ |
| 45 min | Write | `stress-report-writeup.md`: verdict per claim | 04_ |
| 20 min | Problems | 10 problems | 05_ |
≈ 3.8 h.

## Demo results (index stand-in, same aligned start as Day 17: 2008-09-01)
| Stress | Sharpe xs cash | Vol ratio | DD edge |
|---|---|---|---|
| Base | 0.18 | 0.69 | +18.3 pp |
| Costs ×3 | 0.16 | 0.69 | +17.9 pp |
| Delay +1 bar | 0.20 | 0.69 | +20.3 pp |
| Timing luck, decision days 1–15 | 0.18 to 0.31 | 0.63 to 0.69 | +16.7 to +23.5 pp |
| **Drop best 1 of 11 trades** | **−0.09** | n/a | n/a |
| Drop best 10 days | −0.18 | n/a | n/a |
| Cash −1 pp | 0.22 | 0.69 | +17.6 pp |

- **Costs, delay and timing barely matter.** It trades ~11 times in 10 years.
- **Returns rest on one trade.** Drop it and Sharpe goes negative. So: no return claim, ever.
- **Random-timing null:** being in cash ~30% of the time at random dates gives a vol ratio of ~0.87; the real rule gets 0.69 (p ≈ 0.06). About 40% of the vol cut is just exposure. The DD cut isn't clearly better than random timing (p ≈ 0.16).
- **Bootstrap** (placeholder lines 0.85 / 5 pp): vol falsifier met in 99% of resamples, DD in 80%.

## Mentor's rulings
1. Use YOUR locked falsifier numbers. The defaults are placeholders.
2. Stress runs aren't trials (no rule changed). Log them as `stress`, counted_in_dsr = no.
3. Verdict per claim today: keep / weaken / drop. Any v2 pre-reg must be hashed and dated **before** you open 2019+ tomorrow.
4. No fixing what a stress reveals. A fix is a new strategy, and it starts again at Day 12.

Send me: stress_report.md + charts + 1-page write-up + stress log rows + 10 problems + training-log row.
Day 20 (Thu 19 Nov): open the holdout once, run the pre-registered rule, Deflated Sharpe, and grade against your written predictions.
