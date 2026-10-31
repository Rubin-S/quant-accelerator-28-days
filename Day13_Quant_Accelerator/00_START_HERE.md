# DAY 13: Thu 12 Nov 2026: DATA PIPELINE
## Garbage in, confident garbage out. Today you build the pipe your strategy will drink from for the rest of the course.

Deliverable: a **clean dataset** (Parquet + manifest + data README) that your Day 15 engine reads through one `load()`
function, with the 2019+ holdout physically sealed. Tomorrow (Day 14, Gate 2) you audit it.

| Time | Block | What | Files |
|---|---|---|---|
| 20 min | Drill | Zetamac + "10:1 split, pre-split close 1136.75 → adjusted?" × 5 | |
| 30 min | Read | Wickham, *Tidy Data* (secs 1–3: one row per observation, one column per variable) | 01_ |
| 25 min | Read | NSE sources: the split circular (1 page), the bhavcopy-format circular, UDiFF guide pp. 1–6, and the TRI section of the NIFTY methodology (search "Total Returns") | 02_ |
| 15 min | Watch | Data Mozart, "Parquet File Format: Explained to a 5 Year Old!" | |
| 50 min | Run | `pipeline.py`: predict each stage's findings first, then run | 03_ |
| 30 min | Run | `bhavcopy_ingest.py`: official NSE data, both formats, cross-checked against Yahoo | 03_ |
| 30 min | Own it | Run `fetch_nifty_tri.py` on your laptop (or download TRI by hand); add TRI + a cash-leg series to the pipeline | 03_ |
| 20 min | Write | `data-README-template.md` for your dataset | 04_ |
| 20 min | Problems | 10 problems | 05_ |
≈ 4.0 h.

## What the pipeline found in the data you've been using since Day 4
1. **NIFTYBEES split 10:1 on 19 Dec 2019** (NSE circular NSE/CML/42873). Yahoo adjusted the history but **double-adjusted 19–20 Dec**
   (these are the "bad ticks" from Day 4). The ratio test catches them; we set them to NaN, not a guess.
2. **No dividends in Yahoo's Adj Close.** Vendors disagree: Trendlyne lists 2003–2012, while Investing.com and StockEvents add 2013–2015.
   The price-gap test clearly confirms only **9 Mar 2012** (seen −1.80% vs expected −1.87%). Over 2009–2018 the ETF's CAGR
   is 14.04% price-only, 14.25% with the confirmed dividend and 14.75% with all claimed ones. **Resolve this from the AMC's IDCW
   record** (Nippon India MF site) and write the policy down.
3. **Official NSE close ≠ Yahoo?** For Dec 2018 they match exactly once you divide the pre-split NSE price by 10. Good.
   But the official close ≠ last trade (up to ₹2 on a ₹1,124 unit), as on Day 11.
4. **The ISIN changed** (INF732E01011 in 2018 → INF204KB14I2 now). Don't key history on ISIN alone.
5. **Calendar is data:** Budget-Saturday and Muhurat sessions appear (2015-02-28, 2020-11-14, 2025-02-01), and the
   6-day gap to 2014-10-07 is real holidays. Yahoo's NIFTY and NIFTYBEES files don't even agree on these sessions.
6. **Timezones:** the S&P close (16:00 New York) lands at 01:30/02:30 IST the next day. Joining by calendar date shows a
   correlation of +0.30, but the tradable, lagged version is +0.22.
7. **Holdout sealed:** `load("HOLDOUT_SEALED")` raises an error unless you set the Day 20 unlock string, and every file is
   checked against its SHA-256 in `manifest.json`.

## Mentor's rulings
- **Raw files are read-only.** Every fix is code + a log line + a reason.
- **Signals and fills from the official NSE file** (bhavcopy, later Kite). Yahoo is a cross-check only.
- **Upgrade the benchmark now:** NIFTY 50 TRI (with dividends) and a real cash leg (LIQUIDBEES or the overnight rate) replace
  "price index + 6%". If your Day 12 pre-reg says otherwise, file a v2 *before* any holdout look and log it in the trial log.
- **Network etiquette:** browser-like User-Agent, ≥1 s between requests, cache everything. Getting blocked is a pipeline failure.

Send me: manifest.json, your data README, the TRI/cash series you added, the 10 problems, and your training-log row.
Teaser for Day 14: NSE shows a 26 Dec 2018 NIFTYBEES **open of 1188 vs close 1123.82** (−5.4% intraday on a flat-ish day). Bad print or real?
