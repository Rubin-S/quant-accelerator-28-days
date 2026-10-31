# DAY 21: Fri 20 Nov 2026: THE RULEBOOK · GATE 3
## Write the rules while you're calm. They're for the day you aren't.

| Time | Block | What | Files |
|---|---|---|---|
| 20 min | Drill | Kelly f* = SR/σ for 5 (SR, σ) pairs; "worst day in 10 years of NIFTY?" | |
| 30 min | Read | SEC Knight order ¶1–30 + FIA section 1 | 02_ |
| 20 min | Read | SEBI circular (6 pp) + Zerodha summary | 02_, RESOURCES |
| 25 min | Read | Triple penance (sections 1–3, 6) + Carver "trading the equity curve" | 01_, RESOURCES |
| 30 min | Run | Edit `rulebook.json` → `python limits_calibrator.py --trade <NIFTYBEES IS> --sharpe-lo90 <yours>` → `pytest -q` | 03_ |
| 50 min | Write | `RULEBOOK.md`, then sign it with the json hash | 04_ |
| 15 min | Gate | `gate3-checklist.md` | 04_ |
| 20 min | Problems | 10 problems | 05_ |
≈ 3.5 h.

## What the demo calibration shows (IS data, Faber 10m, index stand-in)
- **Kelly:** 1.23× at the point Sharpe, **0× at the lower bound**, so size by risk budget, capped at 1.0×.
- **False alarms per year while nothing is wrong:** daily halt at 3% fires 41% of years, 5% fires 18%; monthly halt at 10% fires 6%, at 12% 1%; kill at 1.25× backtest DD fires 0.1%.
- The strategy's worst IS day was −5.9%, so a bootstrap can't say anything about bigger days. Real ones happen.
- **Triple penance at SR 0.18:** recovery from a bad drawdown can take decades, so no time-based retirement rule.
- **Draft kill limit on ₹20,000:** about ₹7,700 of drawdown. Change the capital, not the limit.

## Mentor's rulings
1. **Two kinds of stop:** HALT keeps the position and stops orders. KILL flattens and retires. Loss limits HALT. Only rulebook breaches KILL.
2. **Every rule is code, every rule has a test that makes it say no.** No test, no rule.
3. **Capital at risk = money you can lose.** Not money you "probably won't" lose.
4. **No overrides.** Amendments are dated, cooled off for 48 h, re-hashed, and never written during market hours.
5. **Gate 3 needs the Day 20 verdict.** If the strategy died there, write the backup decision honestly and we run Week 4 plumbing on a simple baseline.

Send me: signed RULEBOOK.md + rulebook.json + limits_report.md + pytest output + gate3-checklist + 10 problems + training-log row.
Day 22 (Sat 21 Nov): Kite Connect app, cloud VM with a static IP, IP whitelist, 2FA login flow.
