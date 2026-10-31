# DAY 27: Thu 26 Nov 2026: PAPER SESSION 3 + FAILURE DRILLS
## "If you haven't tried it, assume it's broken." (Google SRE, ch. 17)

| Time | Block | What | Files |
|---|---|---|---|
| 07:30–08:30 | **Game day** on the VM, G1–G8, before the market | 04_templates/game_day_runbook.md |
| 08:30–09:20 | Pre-market | login → preflight → dashboard all green again | Day 22–25 tools |
| 30 min | Read | Principles of Chaos + Krishnan "Weathering the Unexpected" | RESOURCES.md |
| 20 min | Code drills | `python drills.py` → drills_report.md | 03_ |
| 60 min | Fix | BUG-27-1 and BUG-27-2: failing-first (remove xfail → red) → fix → green → replay parity → drills 12/12 | 03_, 04_ |
| evening | **Session 3** | run_live → session_review → dashboard → live_vs_backtest (sessions 1–3) | 03_ |
| 20 min | Problems | 10 problems | 05_ |
≈ 3.5 h of deep work + the session.

## Code drill results today (before your fixes)
11 PASS · **1 SAFE-BUT-ACCIDENTAL** (D05: lost connection after the order left. No double order, but only because the duplicate-tag guard HALTED) · 0 FAIL. D10 also left a temp file after a failed save. Both are now failing-first tests for you.
After the fix (checked, sealed in solutions): 12/12 PASS.

## Mentor's rulings
1. **Drills run on paper only.** Never inject a fault into a live account.
2. **One fault at a time; undo it before the next.** Two faults at once teach you nothing.
3. **Safe for the wrong reason is a bug.** Log it, test it, fix it.
4. **After any 5xx or timeout on an order: ask the broker by tag, never resend.**
5. **The Console kill switch is a tabletop drill this week** (12-hour lock).
6. These two fixes don't change when or what you trade, so they're bug fixes, not rule changes. Prove it: replay parity still shows 0 mismatch days.

Send me: drills_report.md (12/12), both bug entries with red and green output, the game-day sheet with phone times, the session-3 review and diff, 10 problems, and a training-log row.
Day 28 (Fri 27 Nov): paper session 4 + go/no-go memo (graduation).
