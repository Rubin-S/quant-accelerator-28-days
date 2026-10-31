# %% [markdown]
# # Day 14 build-along: DATA AUDIT + LOOK-AHEAD TESTS → audit_report.md (Gate 2 evidence)
# Exploration window only (≤ 2018-12-31). Five audits, each ends PASS / WARN / FAIL with evidence:
#  A completeness & calendar · B bad ticks (robust z on ETF-minus-index) · C stale prices / zero volume
#  D cross-source reconciliation vs NSE's official bhavcopy · E look-ahead tests on strategy CODE
# Philosophy: an audit doesn't "clean". It produces findings, and each finding gets a decision you write down.

# %%
import warnings; warnings.filterwarnings("ignore")
import io, time, random, zipfile, urllib.request, numpy as np, pandas as pd
from pathlib import Path
HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path(".")
DATA = HERE.parent / "07_data"; CACHE = DATA / "bhavcopy_cache"; CACHE.mkdir(exist_ok=True)
END = "2018-12-31"
rd = lambda f: pd.read_csv(DATA / "raw" / f, parse_dates=["Date"], index_col="Date").loc[:END]
idx, etf = rd("NIFTY50_daily.csv"), rd("NIFTYBEES_daily.csv")
R = []                                                  # report rows
def rep(check, status, evidence, decision=""): R.append((check, status, evidence, decision)); print(f"[{status}] {check}: {evidence}")

# %% [markdown]
# ## A. Completeness & calendar
# %%
only_idx, only_etf = idx.index.difference(etf.loc["2009":].index), etf.index.difference(idx.index)
only_idx = only_idx[only_idx >= etf.index.min()]
rep("A1 dates in index file but not ETF file", "WARN" if len(only_idx) else "PASS",
    f"{len(only_idx)} dates, e.g. {[d.date().isoformat() for d in only_idx[:4]]}", "Decide: is the ETF missing a session, or did it not trade?")
rep("A2 dates in ETF file but not index file", "WARN" if len(only_etf) else "PASS",
    f"{len(only_etf)} dates {[d.date().isoformat() for d in only_etf[:4]]}", "Special sessions (Budget Saturday, Muhurat): keep or drop, consistently")
per_year = etf.groupby(etf.index.year).size()
rep("A3 sessions per year (ETF)", "PASS" if per_year.loc[2009:2018].between(240, 252).all() else "WARN",
    f"min {per_year.loc[2009:2018].min()} / max {per_year.loc[2009:2018].max()}", "NSE normally has ≈245–250 sessions")

# %% [markdown]
# ## B. Bad ticks: robust z-score of ETF return minus index return (MAD, not std: outliers inflate std)
# %%
resid = (etf["Close"].pct_change() - idx["Close"].pct_change()).dropna()
mad = (resid - resid.median()).abs().median() * 1.4826
z = (resid - resid.median()) / mad
hits = z[z.abs() > 8]
rep("B1 close-to-close outliers |robust z| > 8", "WARN" if len(hits) else "PASS",
    "; ".join(f"{d.date()} z={v:+.0f}" for d, v in hits.items()) or "none", "Inspect each against NSE bhavcopy (audit D) before deciding")
reversal = hits[[(d in z.index) and (z.shift(-1).get(d, 0) * hits[d] < -16) for d in hits.index]]
rep("B2 outliers that reverse next day (classic bad print)", "FAIL" if len(reversal) else "PASS",
    f"{[d.date().isoformat() for d in reversal.index]}", "Bad print → NaN + log; never trade on it")
gap = (etf["Open"] / etf["Close"].shift(1) - 1) - (idx["Open"] / idx["Close"].shift(1) - 1)
gz = ((gap - gap.median()) / ((gap - gap.median()).abs().median() * 1.4826)).dropna()
odd_open = gz[gz.abs() > 10]
rep("B3 ETF open gap far from index open gap (|z|>10)", "WARN" if len(odd_open) else "PASS",
    f"{len(odd_open)} days, worst {odd_open.abs().idxmax().date() if len(odd_open) else '-'}",
    "ETF opens are first-trade prints (no pre-open auction for equity ETFs). Never assume a fill at the open.")
ohlc = etf[(etf["High"] < etf[["Open", "Close"]].max(axis=1)) | (etf["Low"] > etf[["Open", "Close"]].min(axis=1))]
rep("B4 OHLC consistency", "WARN" if len(ohlc) else "PASS", f"{len(ohlc)} rows {[d.date().isoformat() for d in ohlc.index[:3]]}")

# %% [markdown]
# ## C. Stale prices & zero volume
# %%
same = (etf["Close"].diff() == 0)
runs = same.groupby((~same).cumsum()).sum(); longest = int(runs.max())
rep("C1 longest run of unchanged closes", "WARN" if longest >= 3 else "PASS", f"{longest} days")
zv = etf[etf["Volume"] == 0]
rep("C2 zero-volume sessions", "WARN" if len(zv) else "PASS", f"{len(zv)} {[d.date().isoformat() for d in zv.index[:4]]}",
    "A 'close' with no trades is a stale quote, not a price you could trade")

# %% [markdown]
# ## D. Reconcile against NSE's official bhavcopy (random sample + every flagged date)
# Old CM bhavcopy format (pre-July 2024). Pre-split prices are ×10 vs Yahoo's adjusted history.
# %%
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
def bhav(d):
    mon = f"{d:%b}".upper(); name = f"cm{d:%d}{mon}{d:%Y}bhav.csv.zip"; f = CACHE / name
    if not f.exists():
        try:
            f.write_bytes(urllib.request.urlopen(urllib.request.Request(
                f"https://nsearchives.nseindia.com/content/historical/EQUITIES/{d:%Y}/{mon}/{name}", headers=UA), timeout=60).read())
            time.sleep(1.2)
        except Exception as e: return None
    with zipfile.ZipFile(f) as z: b = pd.read_csv(z.open(z.namelist()[0]))
    row = b[(b.SYMBOL == "NIFTYBEES") & (b.SERIES == "EQ")]
    return None if row.empty else row.iloc[0]
random.seed(13)
sample_random = random.sample(list(etf.loc["2009":].index), 30)
sample = sorted(set(sample_random) | set(hits.index) | set(odd_open.index[:5]))
rows = []
for d in sample:
    b = bhav(d)
    if b is None: rows.append((d, np.nan, np.nan, np.nan, np.nan)); continue
    rows.append((d, etf.at[d, "Close"], b.CLOSE / 10, etf.at[d, "Open"], b.OPEN / 10))
rec = pd.DataFrame(rows, columns=["date", "yahoo_close", "nse_close", "yahoo_open", "nse_open"]).set_index("date")
rec["close_diff_%"] = (rec.yahoo_close / rec.nse_close - 1) * 100

for label, part in [("random sample", rec.loc[rec.index.isin(sample_random)]), ("flagged dates", rec.loc[~rec.index.isin(sample_random)])]:
    bad = part[part["close_diff_%"].abs() > 0.1]
    rep(f"D1 Yahoo vs NSE close, {label} (>0.1% off)", "FAIL" if len(bad) else "PASS",
        f"{len(bad)}/{part.nse_close.notna().sum()} off; years: {sorted(set(bad.index.year))}",
        "Any FAIL → rebuild the ETF series from NSE bhavcopy (rebuild_from_bhavcopy.py)")
stale = rec[(rec.yahoo_open == rec.yahoo_close) & (rec.nse_open != rec.nse_close)]
rep("D1b Yahoo open == close but NSE disagrees (filled/stale bars)", "WARN" if len(stale) else "PASS",
    f"{len(stale)} dates {[d.date().isoformat() for d in stale.index]}", "Matches the 2012–13 zero-volume cluster (audit C2)")
rec.round(4).to_csv(HERE / "reconciliation_sample.csv")

# The same index has had three names in NSE files: another trap for naive joins
NIFTY_NAMES = {"NIFTY 50", "CNX NIFTY", "S&P CNX NIFTY"}
# D3: the INDEX itself (your Day 12 signal runs on NIFTY 50) vs NSE's index close file
def ind(d):
    f = CACHE / f"ind_close_all_{d:%d%m%Y}.csv"
    if not f.exists():
        try:
            f.write_bytes(urllib.request.urlopen(urllib.request.Request(
                f"https://nsearchives.nseindia.com/content/indices/{f.name}", headers=UA), timeout=60).read()); time.sleep(1.2)
        except Exception: return None
    b = pd.read_csv(f); r = b[b["Index Name"].str.strip().str.upper().isin(NIFTY_NAMES)]
    return None if r.empty else float(r["Closing Index Value"].iloc[0])
ic = pd.Series({d: ind(d) for d in sample_random}, dtype=float)
idiff = (idx["Close"].reindex(ic.index) / ic - 1).abs() * 100
rep("D3 Yahoo ^NSEI close vs NSE index file (>0.01% off)", "FAIL" if (idiff > 0.01).any() else "PASS",
    f"{int((idiff > 0.01).sum())}/{ic.notna().sum()} random dates off, max diff {idiff.max():.4f}%; NSE file unavailable for {int(ic.isna().sum())} dates (pre-2012 archive gaps)",
    "PASS → the index (your signal input) is trustworthy on this sample")

if len(odd_open):
    d = odd_open.abs().idxmax()
    rep("D2 worst open-gap day, NSE's own numbers", "INFO", f"{d.date()}: NSE open {rec.at[d,'nse_open'] if d in rec.index else 'n/a'} vs close {rec.at[d,'nse_close'] if d in rec.index else 'n/a'} (÷10 units)",
        "If NSE shows it too, it's a REAL first trade, not vendor error. Real but untradeable for your model.")

# %% [markdown]
# ## E. Look-ahead tests on CODE (the bug is usually in your code, not the data)
# Test 1, future-perturbation: replace every price after date t with noise. A legal signal at dates ≤ t must not change.
# Test 2, delay test: execute one more bar later. A real daily/monthly edge degrades a little; a leak collapses.
# %%
px = idx["Close"]
def faber_leaky(p):          # classic bug: month-end signal from the month-end close, traded AT that close
    m = p.resample("ME").last(); s = (m > m.rolling(10).mean()).astype(float)
    return s.reindex(p.index, method="bfill")          # bfill pulls month-end info into earlier days!
def faber_ok(p):
    m = p.resample("ME").last(); s = (m > m.rolling(10).mean()).astype(float)
    return s.reindex(p.index, method="ffill").shift(1)  # known after the month-end close → act next session
def perturbation_test(fn, p, trials=5):
    base = fn(p); rng = np.random.default_rng(0)
    for t in rng.choice(p.index[300:-50], trials, replace=False):
        q = p.copy(); q[q.index > t] = q[q.index > t].values * rng.uniform(0.5, 1.5, (q.index > t).sum())
        if not base.loc[:t].fillna(-1).equals(fn(q).loc[:t].fillna(-1)): return False, t
    return True, None
for name, fn in [("faber_leaky (bfill)", faber_leaky), ("faber_ok (ffill+shift)", faber_ok)]:
    ok, t = perturbation_test(fn, px)
    rep(f"E1 perturbation test: {name}", "PASS" if ok else "FAIL",
        "signal up to t unchanged when the future is scrambled" if ok else f"signal before {pd.Timestamp(t).date()} changed: it reads the future")
ret = px.pct_change()
def sharpe(sig, lag): r = (sig.shift(lag) * ret).dropna(); return r.mean() / r.std() * np.sqrt(245)
for name, fn in [("faber_leaky", faber_leaky), ("faber_ok", faber_ok)]:
    s = fn(px); rep(f"E2 delay test: {name}", "INFO", f"Sharpe (no costs, no cash) lag0 {sharpe(s,0):+.2f} → lag1 {sharpe(s,1):+.2f} → lag5 {sharpe(s,5):+.2f}",
                    "Delay test alone MISSES a month-long leak (lag1 barely moves). Only the perturbation test caught it.")

# %% [markdown]
# ## Write the report
# %%
md = ["# Data audit report: exploration window to " + END, "", "| Check | Status | Evidence | Decision |", "|---|---|---|---|"]
md += [f"| {c} | **{s}** | {e} | {d} |" for c, s, e, d in R]
(HERE / "audit_report.md").write_text("\n".join(md)); print("\nwrote audit_report.md and reconciliation_sample.csv")
