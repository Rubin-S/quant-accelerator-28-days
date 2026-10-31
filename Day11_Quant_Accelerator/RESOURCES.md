# Day 11 resources (checked 31 Oct 2026)
✅ = in this ZIP. Organised by checklist point.

## P1 Economic reason (01_payer_and_myths)
- ✅ Moskowitz, Ooi & Pedersen (2012), "Time Series Momentum," JFE (author copy). Slides: http://docs.lhpedersen.com/TSMOM_Slides.pdf
- ✅ Hurst, Ooi & Pedersen (2017), "A Century of Evidence on Trend-Following Investing," JPM (AQR copy). Positive in every decade since 1880; did well in 8 of 10 worst 60/40 crises.
- ✅ Asness, Frazzini, Israel & Moskowitz (2014), "Fact, Fiction and Momentum Investing," JPM (AQR copy).

## P2–P3 Costs and capacity (02_costs_capacity)
- ✅ Frazzini, Israel & Moskowitz, "Trading Costs of Asset Pricing Anomalies" (Oct 2015 draft): real fund trading data; costs are much lower than earlier estimates; capacity is finite.
- Liquidity check (facts, allowed): NSE ETF page https://www.nseindia.com/market-data/exchange-traded-funds-etf

## P4 Hidden beta, India (03_hidden_beta_india + 09_data)
- ✅ Agarwalla, Jacob & Varma (IIMA WP 2013-09-05), "Four Factor Model in Indian Equities Market."
- ✅ IIMA factor data, Dec 2025 release, survivorship-adjusted, daily + monthly (in %; MF = market minus RF). Library: https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/ (please cite the paper if you use it)
- Video: Alpha Architect (Wes Gray), "How to Calculate Fama French 3 Factor Alpha": https://www.youtube.com/watch?v=mrfWCUKX1Qw
- Video: Algovibes, "Fama French Regression in Python": https://www.youtube.com/watch?v=pLyatGMTqzY

## P5–P6 Sample size and bad regimes (04_sample_regimes)
- ✅ Daniel & Moskowitz, "Momentum Crashes" (2015 draft of JFE 2016).
- Re-read: Lo (2002) Sharpe ratio statistics (Day 2), Bailey & López de Prado MinTRL (Day 5).

## P8 Executable (05_executable_nse)
- ✅ NSE "Historical Data Dissemination of Capital Market Segment" (defines Close vs LTP; close uses rules such as averaging the last 30 minutes).
- NSE Closing Auction Session page: https://www.nse.in/static/products-services/closing-auction-session (CAS reference price = VWAP 3:00–3:15 pm, ±3% band)
- NSE index FAQ (NIFTY close = last-half-hour weighted average of constituents): https://www.nseindia.com/static/products-services/indices-faqs

## Listening
- Lasse Pedersen on Trend Following Radio (Ep. 373): https://www.youtube.com/watch?v=FapcJm91oHg

## Build-along (06_build_along), tested
- `checklist_scorer.py` / `.ipynb`: P2–P6 and P8 numbers on exploration data; reuses Day 7 `nse_costs.py`.

## Templates (07_templates)
- `8-point-checklist-scoresheet.md`, including the honest note on point 5 (confirm vs discovery mode).
