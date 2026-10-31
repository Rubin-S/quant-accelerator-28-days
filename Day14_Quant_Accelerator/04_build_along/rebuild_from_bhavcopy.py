"""Rebuild NIFTYBEES daily OHLCV 2009-01-01..2018-12-31 from NSE's OFFICIAL bhavcopy (old CM format).
Run on your laptop: ~2,500 files at 1.2 s each ≈ 50 min, resumable (cached zips are reused). Output:
07_data/NIFTYBEES_nse_official_2009_2018.csv in NSE units (pre-split prices; divide by 10 for post-2019-12-19 units).
Days with no file = NSE holiday (or a fetch error, listed in the log). Re-run to retry."""
import time, zipfile, urllib.request, pandas as pd
from pathlib import Path
HERE = Path(__file__).resolve().parent; CACHE = HERE.parent / "07_data" / "bhavcopy_cache"; CACHE.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
rows, missing = [], []
for d in pd.bdate_range("2009-01-01", "2018-12-31"):
    mon = f"{d:%b}".upper(); name = f"cm{d:%d}{mon}{d:%Y}bhav.csv.zip"; f = CACHE / name
    if not f.exists():
        try:
            f.write_bytes(urllib.request.urlopen(urllib.request.Request(
                f"https://nsearchives.nseindia.com/content/historical/EQUITIES/{d:%Y}/{mon}/{name}", headers=UA), timeout=60).read())
        except Exception as e: missing.append((d.date(), str(e)[:40])); time.sleep(1.2); continue
        time.sleep(1.2)
    with zipfile.ZipFile(f) as z: b = pd.read_csv(z.open(z.namelist()[0]))
    r = b[(b.SYMBOL == "NIFTYBEES") & (b.SERIES == "EQ")]
    if not r.empty:
        r = r.iloc[0]; rows.append((d.date(), r.OPEN, r.HIGH, r.LOW, r.CLOSE, r.LAST, r.PREVCLOSE, r.TOTTRDQTY, r.TOTTRDVAL, r.ISIN))
out = pd.DataFrame(rows, columns=["session_date", "open", "high", "low", "close", "last", "prevclose", "volume", "value_inr", "isin"])
out.to_csv(HERE.parent / "07_data" / "NIFTYBEES_nse_official_2009_2018.csv", index=False)
print(f"{len(out)} sessions written; {len(missing)} weekdays with no file (holidays or errors), e.g. {missing[:5]}")
