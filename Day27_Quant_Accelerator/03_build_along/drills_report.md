# Failure drills

| Drill | Hypothesis | Observed | Verdict |
|---|---|---|---|
| D01 KILL file on a trade day | no order leaves; position kept; CRIT alert | orders sent 0, halted='pre-trade violation KILL SWITCH FILE present (/tmp/drill_yic' | **PASS** |
| D02 kill.py halt cancels only OUR open orders | cancel #1 only (not manual #2, not done #3, not other symbol #4) | cancelled ['1'] | **PASS** |
| D03 kill.py kill flattens with a marketable LIMIT | SELL 70 CNC LIMIT at LTP −1% (₹260.26); qty 0 → nothing | placed SELL 70 LIMIT @ 260.26; qty-0 call → nothing | **PASS** |
| D04 Connection lost BEFORE the order left | crash + CRIT; restart sends exactly one order; book = broker | run1 CRASH, run2 OK; broker orders 1; book 182 vs broker 182 | **PASS** |
| D05 Connection lost AFTER the order left | restart must NOT resend while our order is OPEN; next day book = broker | runs CRASH/OK/OK; broker orders 1; book 182 vs broker 182; halted='pre-trade violation duplicate order tag F10181204B' | **SAFE-BUT-ACCIDENTAL** |
| D06 Broker rejects the order (margin) | book unchanged; retry next day with a NEW tag; 3 failures → HALT + CRIT | orders ['F10181204B0', 'F10181205B1', 'F10181206B2']; qty book 0 / broker 0; halted='3 unfilled attempts by 2018-12-06' | **PASS** |
| D07 Today's price file missing | ABORT_DATA, CRIT, no orders, no state change | status ABORT_DATA; state written: False | **PASS** |
| D08 Yesterday's preflight (stale) | ABORT_PREFLIGHT, CRIT | status ABORT_PREFLIGHT | **PASS** |
| D09 Session token expired (403) | crash before any order; CRIT says re-login | CRASH; orders 0 | **PASS** |
| D10 Disk full while saving state | old state.json intact (atomic write); CRIT; next run reconciles | CRASH; state unchanged: True; next day book 182 vs broker 182, orders 1; temp files left: 1 | **PASS** |
| D11 Cron fires twice | second run is a no-op | orders after run1 1, after run2 1 | **PASS** |
| D12 Someone trades by hand in the Kite app | foreign order → HALT + CRIT, nothing new sent | halted="foreign order M1 on NIFTYBEES (tag='')"; our orders sent 0 | **PASS** |

PASS 11 · SAFE-BUT-ACCIDENTAL 1 · FAIL 0

## Lessons
- **D01 KILL file on a trade day**: The file is checked inside pre_trade_check, so every order path obeys it.
- **D02 kill.py halt cancels only OUR open orders**: A kill switch that cancels other people's orders is its own incident.
- **D03 kill.py kill flattens with a marketable LIMIT**: Never MARKET (Day 22: API market orders need market_protection).
- **D04 Connection lost BEFORE the order left**: State is saved only at the end, so a crash leaves the old state: the retry is clean.
- **D05 Connection lost AFTER the order left**: No second order went out, but only because the duplicate-tag guard fired and HALTED. run_day doesn't read book['open_order_id'] that recovery sets. Today's bug: failing-first test, then skip sending while an order is OPEN.
- **D06 Broker rejects the order (margin)**: A rejection is information, not noise: read status_message, never auto-resize and resend the same day.
- **D09 Session token expired (403)**: Kite: TokenException = clear the session and log in again (manual, Day 22).
- **D10 Disk full while saving state**: The fill happened before the crash, and next day's recovery applied it from the broker's order book. Finding: save_state leaves a temp file behind on failure; clean it up (failing-first test).