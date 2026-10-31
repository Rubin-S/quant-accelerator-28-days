# Day 23 deliverable: "pipeline passing dry run"
- [ ] `pytest -q` → all green (count: ___)
- [ ] `python replay.py --data <your NIFTYBEES-aligned OHLC>` → Parity mismatch days = 0, idempotence PASS (paste the table)
- [ ] Journal spot check: pick one decision day and trace decision → pre_trade → order → fill → eod in the JSONL (paste the 5 lines)
- [ ] Break it on purpose: set max_order_value_inr = 10 → zero orders, pre_trade violations logged, halt set (paste)
- [ ] Break it on purpose: give the paper broker 5 extra units → mismatch halt on the next run (paste)
- [ ] On the VM: one live `run_day` in PAPER mode on Mon 23 Nov at 15:00 IST with real LTP (Day 24 uses this)
