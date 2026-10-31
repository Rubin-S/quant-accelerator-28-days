# DAY 23: Sun 22 Nov 2026: THE PIPES, PART 2
## data → signal → risk → paper broker → logs. Proven to match the backtest.

| Time | Block | What | Files |
|---|---|---|---|
| 20 min | Drill | Trace 3 journal days by hand · "which guard stops this?" × 5 | |
| 25 min | Read | Kite Orders (tag, market_protection, statuses) + Portfolio | RESOURCES |
| 20 min | Read | Stripe idempotency + SRE ch. 6 (golden signals section) | RESOURCES |
| 30 min | Study | `pipeline.py` top to bottom; map each guard to Knight/FIA (Day 21) | 03_ |
| 30 min | Run | `pytest -q` → `python replay.py` (~2 min) → read the report and one journal | 03_ |
| 30 min | Break it | the two deliberate failures in `dry-run-checklist.md` | 04_ |
| 25 min | Deploy | copy to the VM, install the systemd units (paper mode), dry-run once | 04_ |
| 20 min | Problems | 10 problems | 05_ |
≈ 3.3 h.

## What the replay shows (IS 2008-09 → 2018-12, index stand-in, cash interest off in both)
| Test | Result |
|---|---|
| **Parity**: days the live pipeline's position ≠ the Day 15 engine | **0 of 2,522** |
| End equity gap vs engine | −29 bps over 10 years (integer units + fee rounding) |
| Marketable limits at 09:30 (+0.25% off the open) | 22 sent, all filled. Optimistic: index open, not ETF prints |
| **Passive** limits (−0.25%) | 33 sent, **8 unfilled**, 7 days out of sync, CAGR 6.7% → 6.3% |
| Idempotence: every day run twice | 21 orders either way |

Lesson: your live code now *is* your tested code. And on a 2-trades-a-year rule, haggling with passive limits costs more than it saves.

## Mentor's rulings
1. **Parity = 0 or no Week 4.** Any mismatch day is a bug, in one of the two.
2. **Marketable LIMIT orders only** (rulebook ±1% band, +0.5% cushion). No MARKET, no passive haggling.
3. **After any crash, ask the broker, never your memory.** Reconcile by tag, then continue or halt.
4. **Halts are cleared by a human with a written note.** Only the replay auto-clears.
5. Paper P&L in Week 4 judges plumbing, not edge (plan rule since Day 1).

Send me: replay_report.md + one traced journal day + the two "break it" outputs + `pytest -q` + 10 problems + training-log row.
Day 24 (Mon 23 Nov): first live paper session on the VM.
