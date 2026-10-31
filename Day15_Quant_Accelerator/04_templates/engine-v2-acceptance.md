# Engine v2 acceptance checklist (the Day 15 deliverable)
- [ ] `pytest -q` → 17 passed (paste output with the date)
- [ ] One test of YOUR OWN that the suite didn't have (write it, see it fail on a broken version, then pass)
- [ ] Frictionless engine == vectorised one-liner (test 5) on YOUR strategy's weights
- [ ] Your pre-registered strategy runs on the engine with the pre-registered cost/cash settings, exploration window only
- [ ] Numbers you report: CAGR, vol, **excess-of-cash** Sharpe, max DD, trades, ₹ costs, avg exposure
- [ ] Anything in the run that isn't in the pre-reg (vol targeting, band, a different cash rate) is logged as a NEW TRIAL
- [ ] Git tag `engine-v2`. Tomorrow I plant 3 bugs on a branch. Your tests are the first line of defence.
