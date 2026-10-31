# Bugs found by today's drills (fill in like Day 25's bugs.md)
## BUG-27-1  D05: an open order makes us HALT instead of WAIT
- Contract: never send twice; an open order at the broker means wait.
- Root cause: ______  (hint: who sets book['open_order_id'], and who reads it?)
- Failing-first test: test_day27.py::test_d05_open_order_means_wait_not_halt (strict xfail → remove the marker, see it go red)
- Fix: ______   Green: ______   Replay parity (Day 23) still 0 mismatch days? ______
- Changes when/what we trade? ______ (if yes, it's a rule change: 48 h cooling-off)

## BUG-27-2  D10: save_state leaves a temp file behind when the write fails
- Failing-first test: test_day27.py::test_save_state_cleans_temp_on_failure
- Fix: ______   Green: ______
