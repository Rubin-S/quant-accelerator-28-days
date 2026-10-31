# DATA README: <dataset name> (one per clean dataset; lives next to the Parquet files)
| Field | Value |
|---|---|
| Built (UTC) / by | |
| Raw sources + download date + SHA-256 | |
| Instruments + exchange symbol + ISIN | NIFTYBEES (INF204KB14I2) … |
| Calendar | NSE sessions; session_date in Asia/Kolkata; close 15:30 IST |
| Price field used for signals | official close? (CAS/VWAP, Day 11 PDF) |
| Price field used for fills | next-session open / limit price model |
| Corporate actions applied | split 2019-12-19 10:1 (NSE/CML/42873); dividends: policy = |
| Disputed items + how resolved | |
| Rows dropped / set NaN (with reasons) | from manifest.json log |
| Holdout boundary + seal | 2019-01-01; HOLDOUT_SEALED.parquet sha256 … |
| Known limitations | |
| Re-build command | python pipeline.py |
