# Paper session 1: Mon 23 Nov 2026

## Before 09:15
- [ ] Manual Kite login done at __:__ (kite_session.py status → OK)
- [ ] preflight.json ALL_OK at __:__ (attach)
- [ ] Fire drill: 5 alerts received on phone at __:__ (screenshot) · redaction OK
- [ ] healthchecks.io check created, schedule = weekdays, grace 2 h

## Session
- Command: `python run_live.py --bars … --signal … --date 2026-11-23 [--force-target 1.0]`
- Result line: ______
- Journal lines for today (paste): ______
- Alerts received: ______ (expected: INFO only, unless forced drill → 2 WARN)
- Decision day? NO (next decision = Tue 1 Dec 2026). Forced drill used? Y/N, why

## Deliberate failures (do at least two, after the session)
- [ ] Delete preflight.json → rerun → CRIT "preflight missing" + healthchecks /fail
- [ ] `python kill.py halt "drill"` → rerun → WARN "KILL file present", no orders · then `kill.py clear --note "…"`
- [ ] Edit state.json broker qty +5 → rerun → CRIT mismatch HALT

## Grades (decision quality, not P&L)
| Item | Pass/Fail | Note |
|---|---|---|
| Followed the order of operations | | |
| Every alert was actionable | | |
| No manual trading in the Kite app | | |
| State + journal agree | | |
