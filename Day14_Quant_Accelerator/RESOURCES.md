# Day 14 resources (checked 31 Oct 2026). ✅ = in this ZIP

## Data-cleaning papers (01_cleaning_papers)
- ✅ Brownlees & Gallo (2006), "Financial Econometric Analysis at Ultra-High Frequency: Data Handling Concerns" (Univ. Florence working-paper version of CSDA 51(4)). The standard bad-tick filter.
- ✅ ECB Working Paper 948 (2008), "Clustering Techniques Applied to Outlier Detection of Financial Market Series Using a Moving Window Filtering Algorithm": outlier filtering for daily data, and how to set the parameters.

## Bias papers (02_bias_papers)
- ✅ Brown, Goetzmann, Ibbotson & Ross (1992), "Survivorship Bias in Performance Studies," RFS 5(4).
- ✅ Luo et al. (2014), Deutsche Bank Markets Research, "Seven Sins of Quantitative Investing": survivorship, look-ahead, storytelling, data mining, signal decay, outliers, asymmetric patterns.
- Carhart, Carpenter, Lynch & Musto, "Mutual Fund Survivorship" (bias ≈ 1%/yr for samples > 15 years): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1300796

## NSE / SEBI rules (03_nse_rules)
- ✅ NSE FAQ, pre-open session in the CM segment (Oct 2026).
- ✅ NSE/CMTR/76101 (1 Sep 2026): ETF trading parameters from 7 Sep 2026 (base price = last-30-min VWAP; equity ETF band ±10% flexing to ±20%; book types).
- ✅ SEBI 2013 circular: pre-open call auction extended to non-illiquid scrips.
- Index close archive pattern (tested): `https://nsearchives.nseindia.com/content/indices/ind_close_all_DDMMYYYY.csv` (available from late 2012 in our tests)
- Equity bhavcopy archive pattern (tested): `https://nsearchives.nseindia.com/content/historical/EQUITIES/YYYY/MON/cmDDMONYYYYbhav.csv.zip`

## Free articles
- "Lookahead bias in pandas: 8 ways a backtest sees the future" (uses the same change-the-future test): https://nothingbutalpha.app/learn/lookahead-bias-pandas
- The Quant Stack, "Why is my backtest wrong?!" (resample label/closed trap): https://www.algos.org/p/why-is-my-backtest-wrong
- Systematic Long Short, "A Practical Guide To Cleaning High Frequency Data": https://www.systematiclongshort.com/p/a-practical-guide-to-cleaning-high

## Code
- lookahead-lint (static check for shift(-N) and similar): https://github.com/bmouler/lookahead-lint
- jugaad-data (NSE archives; also has an NSE holiday helper): https://github.com/jugaad-py/jugaad-data

## Build-alongs (04_build_along), tested here unless noted
- `audit.py` / `.ipynb`: audits A–E → `audit_report.md` + `reconciliation_sample.csv` (NSE files cached, so it runs offline).
- `rebuild_from_bhavcopy.py`: the full 2009–2018 official NIFTYBEES series. **Run on your laptop (~50 min)**; not run here.

## Templates (05_templates)
- gate2-checklist.md · audit-decision-log.md · EXAMPLE_audit_report_generated.md (what today's run produced)

## Reused, not duplicated
- Day 13 `pipeline.py` (manifest, sealed holdout) · Day 12 `prereg_designer.py` (verify) · Day 11 scoresheet · Day 4 data-audit checklist
