# Day 7 resources: the Indian cost stack
✅ = in this ZIP. All checked 31 Oct 2026. Official sources first; broker pages second; blogs never for a number.

## 1. Official rates (folder 01)
- ✅ `RATES_SNAPSHOT_2026-10-31.md`: every charge, its rate, and its source. Start here.
- ✅ NSE circular NSE/FA/73061 (27 Feb 2026): transaction charge ₹306.99 + IPFT ₹0.01 per crore from 1 Mar 2026.
- ✅ NSE circular NSE/FA/64232 (27 Sep 2024): the uniform "true to label" charges from 1 Oct 2024.
- ✅ BSE Master Circular (Apr 2026), STT extract: the full STT table as amended by the Finance Act 2026.
- ✅ MSE circular (31 Mar 2026): STT rates from 1 Apr 2026 (a second official copy of the same table).
- ✅ SEBI FAQ on the Indian Stamp Act amendments (2021): stamp duty rates and who pays.
- ✅ NSE Capital Market Consolidated Circular (Apr 2026): trading rules, tick sizes.
- NSE "SEBI Turnover Fees, STT and Other levies" page (updated 17 Apr 2026): https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies
- SEBI "true to label" circular (Jul 2024), the reason exchange charges became uniform: https://www.sebi.gov.in/legal/circulars/jul-2024/charges-levied-by-market-infrastructure-institutions-true-to-label_84506.html

## 2. Tax (folder 02)
- ✅ HSBC Mutual Fund Tax Reckoner FY 2026-27: capital gains rates under the Income-tax Act 2025 as amended by the Finance Act 2026.
- PIB, Budget 2026 highlights (STT hike on F&O; capital gains rates unchanged): https://www.pib.gov.in/PressReleasePage.aspx?PRID=2221416

## 3. Broker pages and guides
- Zerodha charges (brokerage, DP charge, IPFT, rounding notes): https://zerodha.com/charges/
- Zerodha brokerage calculator (your fallback reference for the Gate 1 check): https://zerodha.com/brokerage-calculator/
- How to read a Zerodha contract note: https://support.zerodha.com/category/console/reports/contract-note/articles/how-to-interpret-the-contract-note
- Zerodha Varsity, *Markets and Taxation* module (how trading income is taxed, explained simply): https://zerodha.com/varsity/module/markets-and-taxation/
- Zerodha Varsity, *Clearing and Settlement*: what happens after you click buy (T+1, contract note, DP). https://zerodha.com/varsity/chapter/clearing-and-settlement-process/
- Z-Connect: the 1 Oct 2024 revision explained: https://zerodha.com/z-connect/business-updates/revision-in-exchange-transaction-charges-and-securities-transaction-tax-from-october-1-2024

## 4. Research (folder 08)
- ✅ SEBI (Jul 2024), *Analysis of Intraday Trading by Individuals in the Equity Cash Segment*: 71% lost in FY23; costs added 57% to loss-makers' losses.
- ✅ Novy-Marx & Velikov (2016), "A Taxonomy of Anomalies and Their Trading Costs", RFS (author copy).
- ✅ Frazzini, Israel & Moskowitz, "Trading Costs of Asset Pricing Anomalies" (working paper, author copy).
- Frazzini, Israel & Moskowitz (2018), "Trading Costs": SSRN abstract https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3229719

## 5. Built for you (folder 04), all tested
- `nse_costs.py`: the calculator. Rates as a dataclass with sources; `leg_costs`, `round_trip`, `breakeven_move_pct`, `after_tax_gain`.
- `test_nse_costs.py`: 7 hand-checked tests (all pass).
- `contract_note_check.py`: the Gate 1 within-20% check.
- `cost_drag_lab.py` / `.ipynb` + chart: costs and tax applied to two toy rules on real NIFTYBEES data, plus cost vs account size.

## 6. GitHub / code to read
- Zerodha's official Kite Connect Python client (you'll use it from Day 13; read how orders are placed): https://github.com/zerodha/pykiteconnect

## 7. Gate 1 (folder 07)
- ✅ `GATE_1_CHECKLIST.md`
