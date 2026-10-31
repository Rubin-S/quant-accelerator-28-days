# Day 14: 10 problems
1. Why use the median absolute deviation (MAD) instead of the standard deviation to flag bad ticks?
2. A +68 robust-z jump on 2010-02-05, then −63 the next day. What's the most likely explanation, and how do you prove it?
3. 7 of 30 random dates have Yahoo's NIFTYBEES close off from NSE's by > 0.1%. Estimate the share of bad days in 2009–2018 and give a rough 95% range. Does it matter if your SIGNAL runs on the index?
4. 119 zero-volume days in 2013, with open == close. What are those rows, and what happens to a backtest that "trades" on them?
5. NSE itself records NIFTYBEES on 26 Dec 2018: prev close 1118.37, open 1188 (= day high), close 1123.82, while NIFTY was roughly flat. Bad data or real? Can your model assume it filled at the open?
6. The index archive names the same index "S&P CNX Nifty", "CNX Nifty" and "Nifty 50". What breaks if you filter on one name?
7. `faber_leaky` uses `.reindex(..., method="bfill")`. Explain in one sentence how that reads the future.
8. The delay test barely moved for the leaky version (Sharpe 1.26 → 1.23 at one day's delay). Why didn't it catch the leak, and what did?
9. Your universe is one index ETF. Is survivorship bias zero? Name one place it can still creep in.
10. Gate 2 is about process. Give two situations where you must FAIL yourself even though "the backtest looks fine".
