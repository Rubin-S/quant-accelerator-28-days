# Day 13 resources (checked 31 Oct 2026). ✅ = in this ZIP

## Data quality and structure (01_data_quality)
- ✅ Wickham (2014), "Tidy Data," Journal of Statistical Software 59(10) (author copy).
- Ince & Porter (2006), "Individual Equity Return Data from Thomson Datastream: Handle with Care!" J. Fin. Research 29(4): the classic on vendor data errors. SSRN blocked our download: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=486523

## NSE / index primary sources (02_nse_sources)
- ✅ NSE circular NSE/CML/42873 (11 Dec 2019): NIFTYBEES face value ₹10 → ₹1, effective 19 Dec 2019.
- ✅ NSE circular MSD61773: discontinuation of old trade/bhavcopy files. Related: circular 62424 (12 Jun 2024) set the old CM bhavcopy's end for 8 Jul 2024 (named on https://www.nseindia.com/all-reports).
- ✅ NSE "UDiFF Standards for Generation and Implementation" v1.0 (the new file-naming and field standard).
- ✅ NIFTY Equity Indices methodology (NSE Indices). Includes the Total Return Index method. Concept page: https://www.niftyindices.com/resources/index-concepts/total-return-index
- NSE ETF master list (symbol, ISIN, listing date, face value): ✅ `06_data/nse_etf_list.csv`, from https://nsearchives.nseindia.com/content/equities/eq_etfseclist.csv
- NSE holidays: https://www.nseindia.com/resources/exchange-communication-holidays
- Official TRI history: https://www.niftyindices.com/reports/historical-data ("Total returns Index Values")

## Tools and docs
- jugaad-data (NSE/RBI/AMFI data, incl. TRI via niftyindices): https://github.com/jugaad-py/jugaad-data
- niftyindices TRI endpoint notes (quirks: User-Agent stall, double JSON): https://github.com/satwikbasu/indian-market-data-endpoints/blob/main/endpoints/niftyindices-tri-api.md
- Kite Connect historical candles (you'll use these from Day 22): https://kite.trade/docs/connect/v3/historical/
- pandas time series & time zones: https://pandas.pydata.org/docs/user_guide/timeseries.html
- pandas I/O (Parquet section): https://pandas.pydata.org/docs/user_guide/io.html
- Apache Parquet concepts (row groups, column chunks, pages): https://parquet.apache.org/docs/concepts/

## Videos
- Data Mozart, "Parquet File Format: Explained to a 5 Year Old!": https://www.youtube.com/watch?v=5NA57Pfpdr4
- Learn Data with Mark, "An introduction to Apache Parquet" (pyarrow hands-on): https://www.youtube.com/watch?v=KLFadWdomyI

## Build-alongs (03_build_along), tested here unless noted
- `pipeline.py` / `.ipynb`: ingest + SHA-256, normalise (session date, IST close), validate, corporate actions with evidence, ETF total return, Parquet + manifest, sealed holdout `load()`, timezone trap.
- `bhavcopy_ingest.py` / `.ipynb`: official NSE bhavcopy in the old and UDiFF formats → one schema; cross-check vs Yahoo; close vs last; ISIN change. Cached files included so it runs offline.
- `fetch_nifty_tri.py`: niftyindices TRI downloader. **Not testable from our server (blocked)**; run it on your laptop.
- Reuse: Day 7 `nse_costs.py` (unchanged).

## Data (06_data)
- raw/: NIFTY50, NIFTYBEES, SP500 daily (Yahoo, downloaded 31 Oct 2026, left raw on purpose).
- corporate_actions_NIFTYBEES.csv: split + dividends with **status and source per row** (vendor conflicts marked).
- bhavcopy_cache/: 5 NSE bhavcopy files (4 in Dec 2018, old format; 1 in Oct 2026, UDiFF format, used for the format demo only).
