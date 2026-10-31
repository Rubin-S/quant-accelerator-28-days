# 28-Day Quant Accelerator — v2 (active)

Sat 31 Oct – Fri 27 Nov 2026. Day = ≤4 h deep work + ~2 h light (reading/setup) + 30 min drill + 15 min review with mentor.
Universe: index ETFs / NIFTY index, daily (or hourly) bars. Every test goes in the trial log.
NSE closed: Tue 10 Nov (Diwali-Balipratipada), Tue 24 Nov (Guru Nanak Jayanti). Muhurat session Sun 8 Nov.
Gates every Friday. Fail = fix over the weekend before moving on.

## Week 1 — Foundations (Sat 31 Oct – Fri 6 Nov)
| Day | Date | Deep work | Deliverable |
|---|---|---|---|
| 1 | Sat 31 Oct | Why retail loses (SEBI study), 3 sources of edge. Set up repo, training log, trial log | 1-page "Why should anyone pay me?" |
| 2 | Sun 1 Nov | EV, variance, Bayes, small-sample traps | 10 solved problems + coin-flip sim |
| 3 | Mon 2 Nov | Kelly sizing; simulate full vs half Kelly vs 2x Kelly to ruin | Kelly notebook with ruin chart |
| 4 | Tue 3 Nov | Real NIFTY data: log returns, vol, correlation, fat tails | Stats notebook on 10+ yrs NIFTY |
| 5 | Wed 4 Nov | Overfitting: 20 noise strategies, deflated Sharpe, minimum backtest length | Proof the best noise strategy is fake |
| 6 | Thu 5 Nov | Microstructure: book, spread, adverse selection, slippage on your orderbook repo | Naive market maker that loses, and why |
| 7 | Fri 6 Nov | NSE cost stack (brokerage, STT, exchange fee, GST, stamp duty, SEBI fee) | Cost calculator in code. **GATE 1** |

Gate 1: Kelly sim, noise proof, cost calculator within 20% of a broker contract note. Daily drill: mental math + 1 market-making game.

## Week 2 — Ideas and paper tests (Sat 7 Nov – Fri 13 Nov)
| Day | Date | Deep work | Deliverable |
|---|---|---|---|
| 8 | Sat 7 Nov | Edge families: trend, mean reversion, momentum, carry, events, pairs. Idea-card template | 3 idea cards |
| 9 | Sun 8 Nov (Diwali) | Light day: read 2 papers (Chan ch.1–2, one SSRN paper) | 3 more idea cards |
| 10 | Mon 9 Nov | Mentor kills cards; you defend | 4 more cards (10 total), ~3 survive |
| 11 | Tue 10 Nov (market shut) | 8-point paper checklist on survivors | Checklist scored per idea |
| 12 | Wed 11 Nov | Pick ONE + backup. Write hypothesis, falsifier, kill date, FIXED small parameter grid, t > 3 bar | Pre-registration doc (locked) |
| 13 | Thu 12 Nov | Data pipeline: ETF/index daily data, adjustments, Parquet, timezone checks | Clean dataset |
| 14 | Fri 13 Nov | Data audit: gaps, bad ticks, look-ahead traps | Audit report. **GATE 2** |

Gate 2: one idea passes all 8 checks; pre-registration locked; clean data.

## Week 3 — Build it, try to kill it (Sat 14 Nov – Fri 20 Nov)
| Day | Date | Deep work | Deliverable |
|---|---|---|---|
| 15 | Sat 14 Nov | Upgrade backtester: event loop, cost model, vol sizing, no look-ahead | Engine v2 with tests |
| 16 | Sun 15 Nov | Mentor plants 3 bugs; find them | Bug report |
| 17 | Mon 16 Nov | In-sample run on first 70%; last 30% locked | IS report + trial count |
| 18 | Tue 17 Nov | Walk-forward; parameter stability heat map | Stability report |
| 19 | Wed 18 Nov | Stress: 2x costs, 1-bar delay, drop best 10 trades; bootstrap | Stress report |
| 20 | Thu 19 Nov | Factor check (market, size, value, momentum); open OOS ONCE; deflated Sharpe with your trial count | Full research report |
| 21 | Fri 20 Nov | Rulebook: vol sizing, capped Kelly, daily/monthly loss limits, no-override, retirement rule | Signed rulebook. **GATE 3** |

Gate 3: survives OOS + stress, reproducible report, signed rulebook. If it dies, the backup runs D17–20 compressed over the weekend, or we go to W4 with the plumbing on a simple baseline and say so honestly.

## Week 4 — Deploy and run (Sat 21 Nov – Fri 27 Nov)
| Day | Date | Deep work | Deliverable |
|---|---|---|---|
| 22 | Sat 21 Nov | Kite Connect app (₹500 data plan), cloud VM with static IP, IP whitelist, 2FA login flow | Authenticated API on server |
| 23 | Sun 22 Nov | Pipeline: data → signal → risk checks → paper-fill simulator → logs. Limit orders / market protection only | Pipeline passing dry run |
| 24 | Mon 23 Nov | Kill switch, duplicate-order guard, reconciliation, phone alerts. Paper session 1 | Session 1 log |
| 25 | Tue 24 Nov (market shut) | Review session 1; fix bugs; write monitoring dashboard | Fixes + dashboard |
| 26 | Wed 25 Nov | Paper session 2; compare signals, fills, slippage with backtest | Live-vs-backtest diff |
| 27 | Thu 26 Nov | Paper session 3; failure drills (kill switch, lost connection, rejected order) | Drill log |
| 28 | Fri 27 Nov | Paper session 4; post-mortem on decisions; go/no-go memo | Memo. **GRADUATION** |

Graduation: zero unexplained orders, live signals match backtest signals, slippage within assumption, failure drills pass, memo written (size, limits, kill rule).

## After Day 28
Keep paper running 3+ weeks, then the smallest real size you can afford to lose, capped by the rulebook. Paper P&L is NOT the evidence; plumbing and discipline are.
