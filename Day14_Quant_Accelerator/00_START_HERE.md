# DAY 14: Fri 13 Nov 2026: DATA AUDIT · GATE 2
## Yesterday you built the pipe. Today you try to prove it leaks.

| Time | Block | What | Files |
|---|---|---|---|
| 20 min | Drill | Zetamac + "30 samples, 7 bad: give the 95% range" × 3 | |
| 35 min | Read | Brownlees & Gallo (2006), secs 1–3: data errors and the moving-window filter. Skim ECB WP 948 for how to choose filter parameters. | 01_ |
| 35 min | Read | Brown, Goetzmann, Ibbotson & Ross (1992), intro + sec 1 (survivorship). Deutsche Bank's *Seven Sins*: survivorship, look-ahead, data mining. | 02_ |
| 15 min | Read | NSE rules that explain "weird" prints: pre-open FAQ, ETF price-band circular (equity ETFs: no pre-open book, ±10% band flexing to ±20%) | 03_ |
| 60 min | Run | `audit.py`: predict each check's verdict first, then run. Read `audit_report.md`. | 04_ |
| 25 min | Run | `rebuild_from_bhavcopy.py` on your laptop (~50 min unattended, resumable) | 04_ |
| 30 min | Own it | Run the perturbation test on YOUR signal function from the pre-reg | 04_ |
| 20 min | Write | Audit decision log + Gate 2 checklist | 05_ |
| 20 min | Problems | 10 problems | 06_ |
≈ 4.0 h (plus the unattended rebuild).

## What the audit found (2009–2018, exploration window only)
- **Your signal input is clean.** Yahoo's NIFTY 50 matched NSE's own index file on all 19 random dates with an NSE file. Watch out: NSE named the index "S&P CNX Nifty", then "CNX Nifty", then "Nifty 50".
- **Your execution series is not.** Yahoo's NIFTYBEES close was off from NSE's bhavcopy by > 0.1% on **7 of 30 random dates**
  (2010, 2012–13). Worst: 2010-02-05 (+14%) and 2010-10-06 (−15%), each a one-day spike that reverses.
- **Fake bars:** 171 zero-volume days, 119 of them in 2013, often with open == close where NSE shows real trading. Vendor filler.
- **Real but untradeable:** NSE's own 26 Dec 2018 record has an open of 1188 (= day high) after a 1118.37 previous close, on a flat NIFTY day.
  Equity ETFs have no pre-open auction, so the "open" is just the first trade. **Never model fills at the open.**
- **Look-ahead in code:** the classic month-end bug (`bfill`) inflates the Faber filter's Sharpe from +0.53 to +1.26. The perturbation
  test catches it. The one-day delay test does NOT (1.26 → 1.23), because the leak reaches up to a month ahead.
- **Day 13 teaser answered:** it's real (NSE records it), and it's exactly why you use limit orders.

## Mentor's rulings for Gate 2
- Data roles are audited separately: **signal** (index: PASS), **execution** (ETF: rebuild from NSE), **benchmark** (TRI, from Day 13).
- Every WARN/FAIL gets a row in the decision log. "Ignored" is a decision too, and it has to be written down.
- Your own signal function must pass the perturbation test before Day 15 starts.
- Gate 2 is graded on process. Passing it with a bad data decision is worse than failing it honestly.

Send me: audit_report.md, the decision log, the Gate 2 checklist (with the verify output and the prereg-v1 tag URL), perturbation-test output for your signal, the 10 problems, and your training-log row.
