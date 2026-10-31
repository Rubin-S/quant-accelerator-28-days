# Data in this folder
Downloaded 31 Oct 2026 from Yahoo Finance with yfinance (auto_adjust=False). Daily bars. Columns: Open, High, Low, Close, Adj Close, Volume.

| File | Yahoo symbol | What it is | From |
|---|---|---|---|
| NIFTY50_daily.csv | ^NSEI | NIFTY 50 **price** index (no dividends) | 17 Sep 2007 |
| NIFTYBANK_daily.csv | ^NSEBANK | NIFTY Bank price index | 17 Sep 2007 |
| NIFTYBEES_daily.csv | NIFTYBEES.NS | Nippon India ETF Nifty BeES: tradeable | 2 Jan 2009 |
| GOLDBEES_daily.csv | GOLDBEES.NS | Nippon India ETF Gold BeES | 2 Jan 2009 |
| INDIAVIX_daily.csv | ^INDIAVIX | India VIX (implied vol, %) | 3 Mar 2008 |
| SP500_daily.csv | ^GSPC | S&P 500 (US time zone!) | 3 Jan 2007 |

**Left raw on purpose.** Known issues: NIFTYBEES and GOLDBEES show wrong prices on 19–20 Dec 2019; the last row of each ETF has an empty Close. Finding these is part of the lab.
Free data is fine for learning. In Week 4 you'll switch to Kite Connect data and audit it again. Official index history (including the Total Return Index): https://www.niftyindices.com/reports/historical-data
