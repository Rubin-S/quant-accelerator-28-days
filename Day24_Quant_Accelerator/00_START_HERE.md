# DAY 24: Mon 23 Nov 2026: PAPER SESSION 1
## Kill switch · crash recovery · phone alerts · dead man's switch

Today the system meets real days. It will mostly do nothing, and doing nothing correctly is the test.

| Time | Block | What | Files |
|---|---|---|---|
| 08:30–09:15 | Pre-market | Manual Kite login → `preflight.py` → `fire_drill.py` (5 alerts on your phone) | 03_ |
| 20 min | Read | Kite Orders (statuses, today-only book) + Zerodha kill switch page | RESOURCES |
| 30 min | Set up | Telegram bot or ntfy topic + healthchecks.io check (free, 20 checks) | RESOURCES |
| 30 min | Study | `recovery.py` + `kill.py`; map each to a Knight failure | 03_ |
| evening | **Session 1** | append today's NIFTYBEES + NIFTY bhavcopy rows → `python run_live.py …` → read journal + alerts | 03_, 04_ |
| 30 min | Break it | 2 of the 3 deliberate failures in session-1-log.md | 04_ |
| 20 min | Problems | 10 problems | 05_ |
≈ 3.5 h, split around the market.

## The honest calendar
NSE is shut **Tue 24 Nov** (Guru Nanak Jayanti). Paper sessions run Mon 23, Wed 25, Thu 26, Fri 27 Nov. **None is a decision day.** The next is **Tue 1 Dec**. So Week 4 tests the plumbing, not the strategy. You may run **one** `--force-target` drill to push a paper order through end to end, and label it a drill.

## Mentor's rulings
1. **Three stop layers:** KILL file (seconds) → `kill.py` cancel/flatten (seconds) → Zerodha Console kill switch (manual, 12-hour lock). Use them in that order.
2. **Every restart starts with recovery.** Broker truth first; never resend while an order is open.
3. **A foreign order halts the system.** Including yours from the Kite app. Week 4 has no manual trades.
4. **Alerts must be rare and actionable.** If you mute a channel, that's an incident.
5. **The heartbeat lives outside the VM.** Silence is a signal.

Send me: session-1-log.md (with phone screenshots) + journal lines + `pytest -q` (22 pass) + 10 problems + training-log row.
Day 25 (Tue 24 Nov, market shut): review session 1, fix bugs, build the monitoring dashboard.
