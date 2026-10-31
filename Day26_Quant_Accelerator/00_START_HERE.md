# DAY 26: Wed 25 Nov 2026: PAPER SESSION 2 + LIVE vs BACKTEST
## Same days, same rule: did live do what the backtest says it would?

| Time | Block | What | Files |
|---|---|---|---|
| 08:30–09:20 | Pre-market | login → preflight → dashboard check | Day 24–25 tools |
| 20 min | Drill | Compute 3 slippage numbers by hand (fill vs close, in bps, signed) | |
| 40 min | Read | Frazzini–Israel–Moskowitz "Trading Costs": intro + shortfall definition + figures | 01_papers |
| 15 min | Read | NIFTYBEES product note: benchmark, unit size, TRI vs price index | 02_reference |
| 20 min | Demo | `python demo_paper_weeks.py` → read `demo_out/diff_report.md` | 03_ |
| evening | **Session 2** | `run_live.py` → `session_review.py` → `dashboard.py` | 03_ |
| 30 min | Diff | `python live_vs_backtest.py --journal … --bars … --signal …` on sessions 1–2 → fill the template | 03_, 04_ |
| 20 min | Problems | 10 problems | 05_ |
≈ 3.5 h, split around the market.

## The five diffs (check in order)
D1 signal → D2 position → D3 fills → D4 fees → D5 return attribution:
**live = backtest(index) + timing/sizing + ETF-vs-index + slippage + fees + residual**

## Demo result (25 sessions over the 3 Dec 2018 decision)
D1 1/1 match · D2 0 mismatch days · D3 1 fill, excess 0.0 bps (paper, by construction) · D4 fee ₹3.72 = model · D5: live −0.30% = backtest −0.06% + timing 0.00% + ETF-vs-index −0.17% + slippage −0.05% + fees −0.02% + residual 0.00%.

## Honest limits
- Week 4 has **no decision day**, so D1 will be empty for your real sessions; that's expected, not a pass.
- One or two fills **can't** test slippage. At ~8 bps spread per fill you need about 11 fills to decide at a 5 bps tolerance, roughly 5–6 years at this strategy's pace. Write that into the memo.

## Mentor's rulings
1. **An unexplained mismatch in D1/D2, or a residual above 5 bps, stops the system.** Slippage and tracking within known bands get logged.
2. **Measure against the TRI-tracking instrument, not the price index you signal on.** The gap is real money (dividends).
3. **"Undecided" is a valid, honest result.** Never round it up to "pass".

Send me: diff template filled + diff_report.md + session-2 review + 10 problems + training-log row.
Day 27 (Thu 26 Nov): paper session 3 + failure drills (kill switch, lost connection, rejected order).
