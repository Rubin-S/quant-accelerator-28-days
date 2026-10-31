# Data notes (Day 17)
- `NIFTY50_daily_IS_to_2018-12-31.csv`: the Day 14 audited NIFTY 50 file, physically cut at 2018-12-31. The holdout isn't in this ZIP at all.
- `india_cash_rate_monthly_2007_2018.csv`: built 31 Oct 2026 from the OECD SDMX API (dataflow DF_FINMARK, India, monthly, % p.a.):
  - `ir3m_interbank_pct` = IR3TIB (3-month interbank). Available from **2011-11** only.
  - `oecd_irstci_pct` = IRSTCI (call money/interbank). It reads a flat **6.00 from 2007-01 to 2012-01**, which isn't how the traded call rate behaved (it spiked in late 2008). Treat that stretch as **PROVISIONAL**.
  - `cash_rate_used_pct` = IR3TIB where it exists, else IRSTCI. `is_report.py` lags it one month (month M's average is used from the 1st of M+1).
- **Before Day 20**, replace it with RBI DBIE 91-day T-bill (primary-auction implicit yields, weekly) from https://data.rbi.org.in. Log the swap in your audit-decision log. It's a cash-leg change, not a strategy change, but write it down anyway.
- Trade series: still the INDEX stand-in. Pass `--trade` your NSE-rebuilt NIFTYBEES (Day 14 `rebuild_from_bhavcopy.py`).
