# Audit decision log (one row per finding; never delete rows)
| Date found | Check | Finding | Evidence (file / NSE source) | Decision (keep / NaN / rebuild / drop session) | Why | Affects pre-reg? (Y → v2) |
|---|---|---|---|---|---|---|
| 2026-11-13 | D1 | Yahoo NIFTYBEES closes off vs NSE on 7/30 random dates (2010, 2012–13) | reconciliation_sample.csv | rebuild from bhavcopy | official source exists | N (execution data, not rules) |
