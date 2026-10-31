# DAY 18: Tue 17 Nov 2026: WALK-FORWARD AND THE STABILITY HEAT MAP
## Does the result depend on a lucky parameter, or a lucky start date?

Exploration window only (≤ 2018-12-31). The holdout isn't in this ZIP.

| Time | Block | What | Files |
|---|---|---|---|
| 20 min | Drill | Zetamac + "3 near-identical rules, best Sharpe 0.22: what's the haircut?" × 5 | |
| 30 min | Listen | Pardo Part II on walk-forward analysis (first 30 min) | RESOURCES |
| 25 min | Read | Carver, "The three kinds of (over) fitting" + FPP3 §5.10 | links |
| 25 min | Read | Bergmeir, Hyndman & Koo, sections 1, 2 and 5 | 01_ |
| 15 min | Predict | Will WF-reselection beat fixed 10m? Will the DD edge survive a different start? Write it down | |
| 40 min | Run | `python walk_forward.py --trade <your NIFTYBEES>` then `pytest -q` | 03_ |
| 45 min | Write | `stability-report-writeup.md` (1 page) | 04_ |
| 10 min | Log | Add today's 11 trials to trial-log.csv | 04_ |
| 20 min | Problems | 10 problems | 05_ |
≈ 3.8 h.

## What the demo shows (index stand-in, OECD cash, after costs, common start 2008-11-03)
| Test years 2011–2018 | CAGR | Vol | Sharpe xs cash | Max DD |
|---|---|---|---|---|
| Re-pick each Jan (expanding) | 4.8% | 11.1% | −0.19 | −22.5% |
| Re-pick each Jan (rolling 5y) | 4.6% | 11.2% | −0.20 | −22.5% |
| **Fixed 10m (pre-registered)** | 4.0% | 11.5% | −0.24 | −23.9% |
| Buy & hold | 7.7% | 15.5% | 0.08 | −26.2% |

- **Re-picking doesn't clearly help.** The expanding scheme picked 8m every single year; the gap to 10m is noise. Walk-forward efficiency is only 0.38 to 0.43.
- **Plateau, not spike:** across 6 to 14 months, full-period Sharpe runs 0.05 to 0.22; 10m sits in the middle (0.18).
- **Hansen SPA:** p ≈ 0.91. The best of the grid does NOT beat buy & hold once you pay for the search.
- **The big one: start-date stability.** The vol ratio stays 0.69 to 0.84 for every start from Sep 2008 to Dec 2009. The drawdown edge is **+18 pp if you start in Sep 2008 and +2 pp from Nov 2008 onward.** One crash month carries the whole DD claim.

## Mentor's rulings
1. No parameter changes. WF is a diagnostic, not a picker. 10m stays.
2. The neighbourhood scan is allowed **once**, logged as trials, never selectable.
3. The start-date finding goes in the write-up in bold. If you want a v2 pre-reg that leans on the vol falsifier over the DD falsifier, write it **before** Day 20, with the reason and trials up. Doing it after you look is fraud.
4. Report what WF did to the trial count: today adds 11.

Send me: stability_report.md + charts + 1-page write-up + trial-log rows + the 10 problems + training-log row.
Day 19 (Wed 18 Nov): stress tests: 2× costs, 1-bar delay, drop the best trades, bootstrap.
