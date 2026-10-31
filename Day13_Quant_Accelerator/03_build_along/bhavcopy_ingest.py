# %% [markdown]
# # Day 13 build-along #2: the OFFICIAL source: NSE bhavcopy, both formats
# NSE's end-of-day file changed format on 8 Jul 2024 (old CM bhavcopy discontinued; switch to "CM-UDiFF Common
# Bhavcopy Final", NSE circular 62424 dated 12 Jun 2024). Real pipelines must read BOTH and map them to one schema.
# This script pulls a few days in each format, normalises, and cross-checks against Yahoo.
# Be polite to NSE: a browser-like User-Agent, ≥1 s between requests, cache everything you download.

# %%
import io, time, zipfile, urllib.request, pandas as pd
from pathlib import Path
HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path(".")
CACHE = HERE.parent / "06_data" / "bhavcopy_cache"; CACHE.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
UDIFF_START = pd.Timestamp("2024-07-08")
def url(d):
    if d >= UDIFF_START:
        return f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{d:%Y%m%d}_F_0000.csv.zip"
    mon = f"{d:%b}".upper()
    return f"https://nsearchives.nseindia.com/content/historical/EQUITIES/{d:%Y}/{mon}/cm{d:%d}{mon}{d:%Y}bhav.csv.zip"
def get(d):
    f = CACHE / Path(url(d)).name
    if not f.exists():
        req = urllib.request.Request(url(d), headers=UA)
        f.write_bytes(urllib.request.urlopen(req, timeout=60).read()); time.sleep(1.2)
    with zipfile.ZipFile(f) as z: raw = pd.read_csv(z.open(z.namelist()[0]))
    return normalise(raw, d)
def normalise(raw, d):
    """Map both formats to: session_date, symbol, series, isin, open, high, low, close, last, volume, value_inr"""
    if "TckrSymb" in raw.columns:      # UDiFF
        m = {"TckrSymb": "symbol", "SctySrs": "series", "ISIN": "isin", "OpnPric": "open", "HghPric": "high",
             "LwPric": "low", "ClsPric": "close", "LastPric": "last", "TtlTradgVol": "volume", "TtlTrfVal": "value_inr"}
    else:                              # old CM bhavcopy
        m = {"SYMBOL": "symbol", "SERIES": "series", "ISIN": "isin", "OPEN": "open", "HIGH": "high", "LOW": "low",
             "CLOSE": "close", "LAST": "last", "TOTTRDQTY": "volume", "TOTTRDVAL": "value_inr"}
    out = raw.rename(columns=m)[list(m.values())].copy(); out.insert(0, "session_date", d)
    return out

# %%
dates = [pd.Timestamp(x) for x in ("2018-12-26", "2018-12-27", "2018-12-28", "2018-12-31", "2026-10-29")]
rows = pd.concat([get(d) for d in dates])
etf = rows[(rows.symbol == "NIFTYBEES") & (rows.series == "EQ")].set_index("session_date")
print("NSE official NIFTYBEES rows (two formats, one schema):")
print(etf[["isin", "open", "close", "last", "volume", "value_inr"]].to_string())

# %% [markdown]
# ## Cross-checks you should always run
# %%
yh = pd.read_csv(HERE.parent / "06_data" / "raw" / "NIFTYBEES_daily.csv", parse_dates=["Date"], index_col="Date")["Close"]
chk = etf.loc[:"2018", ["close"]].join(yh.rename("yahoo"))
chk["nse_div10"] = chk["close"] / 10
chk["diff_%"] = (chk["yahoo"] / chk["nse_div10"] - 1) * 100
print("\n1) Yahoo vs NSE (pre-split NSE price ÷ 10 to match Yahoo's split-adjusted history):")
print(chk.round(3).to_string())
print("\n2) close vs last: the official CLOSE is not the last trade (Day 11 PDF):")
print((etf["close"] - etf["last"]).round(2).to_string())
print("\n3) ISIN changed:", etf["isin"].unique().tolist(),
      "\n   → never join history on ISIN alone across years; keep a symbol↔ISIN map with validity dates.")
