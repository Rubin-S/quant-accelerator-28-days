# Data audit report: exploration window to 2018-12-31

| Check | Status | Evidence | Decision |
|---|---|---|---|
| A1 dates in index file but not ETF file | **PASS** | 0 dates, e.g. [] | Decide: is the ETF missing a session, or did it not trade? |
| A2 dates in ETF file but not index file | **WARN** | 17 dates ['2009-10-13', '2011-05-31', '2011-07-14', '2011-11-24'] | Special sessions (Budget Saturday, Muhurat): keep or drop, consistently |
| A3 sessions per year (ETF) | **PASS** | min 242 / max 250 | NSE normally has ≈245–250 sessions |
| B1 close-to-close outliers |robust z| > 8 | **WARN** | 2009-01-27 z=-8; 2009-05-05 z=+8; 2009-05-18 z=-16; 2010-01-25 z=+13; 2010-01-27 z=-9; 2010-02-03 z=-9; 2010-02-05 z=+68; 2010-02-08 z=-63; 2010-05-19 z=+13; 2010-05-25 z=+9; 2010-05-26 z=-12; 2010-06-04 z=+13; 2010-06-07 z=-10; 2010-06-25 z=+8; 2010-06-28 z=-11; 2010-08-05 z=+9; 2010-10-06 z=-82; 2010-10-07 z=+94; 2011-06-01 z=-10; 2012-03-09 z=-9; 2012-05-14 z=-9 | Inspect each against NSE bhavcopy (audit D) before deciding |
| B2 outliers that reverse next day (classic bad print) | **FAIL** | ['2009-05-05', '2009-05-18', '2010-01-25', '2010-02-03', '2010-02-05', '2010-05-19', '2010-05-25', '2010-06-04', '2010-06-25', '2010-06-28', '2010-08-05', '2010-10-06', '2010-10-07', '2011-06-01', '2012-05-14'] | Bad print → NaN + log; never trade on it |
| B3 ETF open gap far from index open gap (|z|>10) | **WARN** | 35 days, worst 2009-07-07 | ETF opens are first-trade prints (no pre-open auction for equity ETFs). Never assume a fill at the open. |
| B4 OHLC consistency | **WARN** | 1 rows ['2009-07-07'] |  |
| C1 longest run of unchanged closes | **PASS** | 1 days |  |
| C2 zero-volume sessions | **WARN** | 171 ['2009-06-17', '2009-08-18', '2009-08-19', '2009-08-20'] | A 'close' with no trades is a stale quote, not a price you could trade |
| D1 Yahoo vs NSE close, random sample (>0.1% off) | **FAIL** | 7/30 off; years: [2010, 2012, 2013] | Any FAIL → rebuild the ETF series from NSE bhavcopy (rebuild_from_bhavcopy.py) |
| D1 Yahoo vs NSE close, flagged dates (>0.1% off) | **FAIL** | 13/25 off; years: [2010] | Any FAIL → rebuild the ETF series from NSE bhavcopy (rebuild_from_bhavcopy.py) |
| D1b Yahoo open == close but NSE disagrees (filled/stale bars) | **WARN** | 5 dates ['2012-11-01', '2012-11-23', '2013-04-09', '2013-04-23', '2013-05-15'] | Matches the 2012–13 zero-volume cluster (audit C2) |
| D3 Yahoo ^NSEI close vs NSE index file (>0.01% off) | **PASS** | 0/19 random dates off, max diff 0.0000%; NSE file unavailable for 11 dates (pre-2012 archive gaps) | PASS → the index (your signal input) is trustworthy on this sample |
| D2 worst open-gap day, NSE's own numbers | **INFO** | 2009-07-07: NSE open 42.599000000000004 vs close 42.763 (÷10 units) | If NSE shows it too, it's a REAL first trade, not vendor error. Real but untradeable for your model. |
| E1 perturbation test: faber_leaky (bfill) | **FAIL** | signal before 2011-07-28 changed: it reads the future |  |
| E1 perturbation test: faber_ok (ffill+shift) | **PASS** | signal up to t unchanged when the future is scrambled |  |
| E2 delay test: faber_leaky | **INFO** | Sharpe (no costs, no cash) lag0 +1.26 → lag1 +1.23 → lag5 +0.95 | Delay test alone MISSES a month-long leak (lag1 barely moves). Only the perturbation test caught it. |
| E2 delay test: faber_ok | **INFO** | Sharpe (no costs, no cash) lag0 +0.53 → lag1 +0.51 → lag5 +0.56 | Delay test alone MISSES a month-long leak (lag1 barely moves). Only the perturbation test caught it. |