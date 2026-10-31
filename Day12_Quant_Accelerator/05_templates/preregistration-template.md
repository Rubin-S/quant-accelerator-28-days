# PRE-REGISTRATION v1: <strategy name>
Author: Rubin S · Written: Wed 11 Nov 2026 · Lock: SHA-256 in the .LOCK.txt file + git tag `prereg-v1`
Rule: once locked, never edit. Changes go in a new file (v2) that says what changed and why, and the trial count goes up.

## 0. Data status (AsPredicted Q1, honest version)
- Exploration data seen: NIFTY / NIFTYBEES 2007-09 to 2018-12-31.
- Holdout NOT seen: 2019-01-01 → latest. Opened ONCE, on Day 20 (Thu 19 Nov 2026).
- Trials so far (from trial-log.md): __ . All count toward the deflated Sharpe.
- What I already know about 2019+ from life (COVID crash, 2023–24 rally): ______ (write it down; it's a leak to account for)

## 1. Primary hypothesis (one sentence, with direction and size)
e.g. "A 10-month SMA filter on NIFTYBEES (long/cash) has annualised volatility at most 0.85× buy-and-hold over the holdout."

## 2. Mechanism / payer (from Day 8–11)
Who pays, and why it persists:

## 3. Overlay or alpha? (circle one)
OVERLAY (claim = risk reduction; no alpha claim) · ALPHA (claim = excess return; t > 3 bar applies)

## 4. Exact rules (someone else could code it from this)
- Universe/instrument:   - Signal (formula, data field, timestamp):
- When the signal is computed:   - When and how you trade (next day, limit order, which session):
- Position sizing (≤ 1.0×, no borrowing):   - Cash leg (what earns the cash return):
- Costs: Day 7 `nse_costs.py` + 5 bps spread per side; STCG 20.8% where relevant.

## 5. Parameters
- Primary (chosen from literature BEFORE seeing the grid): __
- Fixed grid for the stability check only: { __, __, __ } (max 3 values per knob, max 2 knobs)
- No other parameters may be added. Adding one = new pre-registration + trial count up.

## 6. Primary test and bar
- Metric(s): 
- Bar: ALPHA → t > 3 on the full test; OVERLAY → thresholds below, sized with `prereg_designer.py`
- Holdout length: ~7.8 years. Power from the designer table: P(pass | true) = __ %

## 7. FALSIFIER (the result that kills it, written as numbers)
KILL if any of:
1. 
2. 
3. 

## 8. Secondary checks (reported, NOT used to rescue a failed primary)
Factor betas (IIMA MF/SMB/HML/WML), 2× costs, 1-day extra delay, parameter stability heat map, DSR with N = trial count.

## 9. Kill date and live kill rules
- Research kill date: Thu 19 Nov 2026 (Day 20 holdout touch). Fail → backup.
- Paper/live retirement rule (drafted; signed in the Day 21 rulebook): e.g. drawdown > __ % or __ months worse than the falsifier band.

## 10. Backup strategy (one paragraph + its own falsifier)

## 11. What I will NOT do
No new filters after seeing the holdout. No re-running the holdout with a "fixed" bug unless the bug is logged first, the fix is pre-stated, and the count goes up. No swapping the primary metric.

Signed: ____________   Mentor review: ____________
