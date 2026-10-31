# DAY 15: Sat 14 Nov 2026: ENGINE v2 (event loop · NSE costs · vol sizing · no look-ahead)
## Week 3 starts: build it, then try to kill it. Tomorrow I plant 3 bugs in this engine.

| Time | Block | What | Files |
|---|---|---|---|
| 20 min | Drill | Zetamac + "EWMA by hand": update σ² with λ=0.94 for 5 returns | |
| 30 min | Read | QuantStart event-driven series, Parts I–IV (links): the architecture you're upgrading to | RESOURCES |
| 30 min | Read | Harvey et al. (2018) *Impact of Volatility Targeting*, secs 1–3. Moreira & Muir (2017), intro only. | 01_ |
| 15 min | Read | RiskMetrics (1996), the EWMA section: where λ=0.94 comes from | 01_ |
| 20 min | Read | `engine_v2_design.md` | 02_ |
| 60 min | Build | Read `engine.py` line by line, then `pytest -q` (17 green). Break one line on purpose and watch which test catches it. | 03_ |
| 40 min | Build | Plug in YOUR pre-registered strategy and settings; run on 2007–2018 only | 03_ |
| 25 min | Write | One new test of your own + the acceptance checklist | 04_ |
| 20 min | Problems | 10 problems | 05_ |
≈ 4.0 h

## What the demo shows (exploration window, index as the trade stand-in, cash 6% placeholder)
| Version | CAGR | Vol | Excess Sharpe | Max DD | Trades | Costs |
|---|---|---|---|---|---|---|
| Buy & hold | 8.0% | 22.1% | 0.20 | −59.8% | 2 | ₹187 |
| **Faber 10m** | 8.1% | 13.4% | **0.22** | −26.2% | 21 | ₹4,951 |
| + vol target 12% | 6.6% | 9.3% | 0.11 | −17.6% | **1,184** | ₹13,576 |
| + 10% band | 6.7% | 9.1% | 0.12 | −16.5% | 94 | ₹5,340 |
- Faber's 0.22 excess Sharpe matches the Day 12 number (0.21): the engine agrees with your earlier research.
- Vol targeting halves the drawdown but also halves the excess Sharpe here, and without a band it churns daily.
- Frictionless engine = vectorised one-liner to 1e-10 (test 5). So every gap between them is a friction you modelled on purpose.

## Mentor's rulings
- The engine changes **how** you test, not **what** you test. Vol targeting and bands aren't in your pre-reg → log them as trials. They're not your strategy.
- Report **excess-of-cash** Sharpe from now on. A 0%-rf Sharpe flatters any part-time-in-cash filter.
- No fills at the open, ever. No fills on the decision bar, ever.
- Trade instrument: plug in the NSE-rebuilt NIFTYBEES CSV (Day 14). The demo uses the index only as a stand-in.
- A green test suite isn't proof. Tomorrow's planted bugs measure how good your tests really are.

Send me: pytest output, your new test, your strategy's engine run table, the acceptance checklist, the 10 problems, and your training-log row.
