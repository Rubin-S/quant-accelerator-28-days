# Day 26 resources: live vs backtest (checked 1 Nov 2026)

## Papers (01_papers)
- **Frazzini, Israel & Moskowitz (2018), "Trading Costs"** (AQR/Yale working paper, 88 pp; free author copy). 1.7 trillion dollars of live execution data across 21 developed markets over 19 years: actual costs were an order of magnitude smaller than earlier studies suggested. Read the intro, the implementation-shortfall definition, and the size and time-of-day results. The lesson for you: measure your own fills, don't guess. SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3229719
- Perold (1988), implementation shortfall: cited in the Day 25 kit.

## The instrument you actually trade (02_reference)
- **Nippon India ETF Nifty 50 BeES, product note (Sep 2026, official PDF)**: benchmark is the **Nifty 50 TRI**; 1 unit ≈ 1/100 of the index; NAV is published daily on AMFI by 11 pm. Performance to 30 Sep 2026: 1 year −7.11% vs Nifty 50 TRI −7.09%; 5 years 6.33% vs 6.37% CAGR. https://mf.nipponindiaim.com/FundsAndPerformance/ProductNotes/NipponIndia-ETF-Nifty-50-BeES-Sep-2026.pdf
- Fund page (NAV, tracking error, monthly disclosures): https://etf.nipponindiaim.com/Funds/details/14
- NSE, "Tracking error" explainer: https://www.nseindia.com/static/products-services/indices-tracking-error

**Why this matters today:** your signal and backtest use the NIFTY 50 *price* index, but NIFTYBEES tracks the *total-return* index and trades at a small premium or discount to its NAV. So D5's "ETF vs index" line will drift **positive** over long holds (the dividend yield was 1.22% on 30 Sep 2026, per the same note) and wobble day to day with the premium. The Day 13 ruling (benchmark = NIFTY 50 TRI) is why.

## From earlier kits
- Cost model `nse_costs.py` (Day 7), ETF round trip ≈ 13.9 bps incl. 5 bps a side for spread (Day 10), "never model fills at the ETF open" (Day 14), parity (Day 23), contracts and shortfall (Day 25).

## Build-along (03_build_along), 36 tests pass
- `live_vs_backtest.py`: five diffs in order: **D1 signal** (live decision vs recomputed on final data), **D2 position** (daily in/out vs backtest, drills labelled), **D3 fills** (slippage vs the 5 bps assumption), **D4 costs** (fees vs model), **D5 return attribution** (live = backtest(index) + timing/sizing + ETF-vs-index + slippage + fees + residual). Plus an honest slippage verdict with the number of fills needed.
- `demo_paper_weeks.py`: 25 paper sessions over a REAL decision day (3 Dec 2018) with a simulated ETF premium → `demo_out/diff_report.md`.
- Carried: the full Day 25 stack (pipeline, risk, recovery, alerts, kill, run_live, review, dashboard) + `engine.py`.
