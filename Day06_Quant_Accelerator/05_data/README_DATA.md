# Data
Same Yahoo Finance daily files as Day 4 (downloaded 31 Oct 2026 with yfinance, auto_adjust=False): NIFTY50_daily.csv (^NSEI), NIFTYBEES_daily.csv (NIFTYBEES.NS).
Known issue: NIFTYBEES has bad prices on 2019-12-19/20 (vendor glitch, found on Day 4); the lab drops those dates. The last row (2026-10-30) has a blank Close in the raw file; the lab handles it.
Daily data can't show you the order book. Live depth comes on Day 13 (Kite).
