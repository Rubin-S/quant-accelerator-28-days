# Data notes (Day 20)
- `NIFTY50_daily_IS_to_2018-12-31.csv`: unchanged exploration file.
- `india_cash_rate_monthly_2007_2018.csv`: unchanged (2007–2012-01 still PROVISIONAL; did you swap in RBI DBIE 91-day T-bills as Day 17 asked? If yes, use yours and say so in the report).
- `SEALED_holdout_2019_2026.zip` (password printed by `seal_predictions.py` after your predictions pass validation):
  - `NIFTY50_daily_FULL_2007-09-17_to_2026-10-30.csv`: the audited IS file + Yahoo ^NSEI rows from 2019-01-01 to 2026-10-30 (pulled 2026-10-31, same source as the Day 4/14 file). Index stand-in, not tradable.
  - `india_cash_rate_monthly_2007_2026.csv`: the Day 17 series + OECD IR3TIB (3-month interbank, % p.a.) for 2019-01 to 2026-09, fetched from the OECD SDMX API on 2026-11-01. Lagged one month by the scripts.
- For the real verdict, pass `--trade` your NSE-bhavcopy NIFTYBEES series covering 2007–2026 (Day 14 rebuild + split-adjusted for the 10:1 split ex 2019-12-19). The index run is only a cross-check.
