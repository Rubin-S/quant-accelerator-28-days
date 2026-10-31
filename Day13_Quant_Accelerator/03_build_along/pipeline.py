# %% [markdown]
# # Day 13 build-along: RAW → CLEAN → PARQUET, with the holdout sealed
# Stages: 1 ingest + fingerprint raw · 2 normalise schema & time · 3 validate · 4 corporate actions (split + dividends,
# with evidence checks) · 5 build series you can trade (ETF total return) · 6 write Parquet + manifest, split into
# explore (≤ 2018-12-31) and a sealed holdout · 7 timezone trap demo.
# Rule: raw files are never edited. Every fix is code + a logged reason.

# %%
import warnings; warnings.filterwarnings('ignore')
import hashlib, json, os, datetime as dt, numpy as np, pandas as pd
import pyarrow as pa, pyarrow.parquet as pq
from pathlib import Path
HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path(".")
RAW, OUT = HERE.parent / "06_data" / "raw", HERE.parent / "06_data" / "clean"
OUT.mkdir(exist_ok=True)
BOUNDARY = pd.Timestamp("2019-01-01")           # pre-registered holdout start (Day 12 ruling)
LOG = []                                         # every fix lands here and in the manifest
def log(kind, msg): LOG.append({"stage": kind, "note": msg}); print(f"[{kind}] {msg}")
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

# %% [markdown]
# ## 1. Ingest + fingerprint (so you can prove which raw file produced which result)
# %%
files = {"NIFTY50": "NIFTY50_daily.csv", "NIFTYBEES": "NIFTYBEES_daily.csv", "SP500": "SP500_daily.csv"}
raw = {k: pd.read_csv(RAW / f) for k, f in files.items()}
fingerprints = {k: sha(RAW / f) for k, f in files.items()}
for k, v in raw.items(): log("ingest", f"{k}: {len(v)} rows, sha256 {fingerprints[k][:12]}…")

# %% [markdown]
# ## 2. Normalise: one schema, a session date, explicit timezone
# A daily NSE bar is a *session* (09:15–15:30 IST). Store the session date and the close timestamp in IST.
# %%
def normalise(df, tz_close):
    d = df.rename(columns=str.lower).rename(columns={"adj close": "adj_close"})
    d["session_date"] = pd.to_datetime(d["date"]).dt.normalize()
    d["close_ts"] = d["session_date"].dt.tz_localize(tz_close[0]) + pd.Timedelta(tz_close[1])
    return d.drop(columns="date").set_index("session_date").sort_index()
nifty = normalise(raw["NIFTY50"], ("Asia/Kolkata", "15:30:00"))
bees = normalise(raw["NIFTYBEES"], ("Asia/Kolkata", "15:30:00"))
spx = normalise(raw["SP500"], ("America/New_York", "16:00:00"))

# %% [markdown]
# ## 3. Validate (hard rules → drop row + log; soft rules → flag)
# %%
def validate(name, d):
    bad = d["close"].isna() | (d["close"] <= 0)
    if bad.any(): log("validate", f"{name}: drop {bad.sum()} rows with missing/non-positive close {list(d.index[bad].date)}")
    d = d[~bad]
    ohlc = (d["high"] < d[["open", "close", "low"]].max(axis=1)) | (d["low"] > d[["open", "close", "high"]].min(axis=1))
    if ohlc.any(): log("validate", f"{name}: {ohlc.sum()} rows violate low ≤ open,close ≤ high (flagged)")
    dup = d.index.duplicated()
    if dup.any(): log("validate", f"{name}: {dup.sum()} duplicate dates dropped"); d = d[~dup]
    wkend = d.index.dayofweek >= 5
    if wkend.any(): log("validate", f"{name}: {wkend.sum()} weekend dates (special sessions? check NSE circulars) {list(d.index[wkend].date)[:5]}")
    gaps = d.index.to_series().diff().dt.days
    if (gaps > 5).any(): log("validate", f"{name}: gaps > 5 calendar days at {list(gaps[gaps > 5].index.date)}")
    return d
nifty, bees, spx = validate("NIFTY50", nifty), validate("NIFTYBEES", bees), validate("SP500", spx)

# %% [markdown]
# ## 4. Corporate actions with EVIDENCE
# 4a. Ratio test: NIFTYBEES ≈ index/100 after the split (≈/10 before, in raw terms). A day where ETF/index jumps far from
#     its rolling median is a mis-adjusted or bad print.
# %%
ratio = (bees["close"] / nifty["close"]).dropna()
dev = ratio / ratio.rolling(21, center=True, min_periods=5).median() - 1
bad_ratio = dev.abs() > 0.25
for d0 in ratio.index[bad_ratio]:
    log("corp_action", f"NIFTYBEES {d0.date()}: ETF/index off by {dev[d0]:+.0%} vs neighbours → set NaN (do NOT forward-fill silently)")
bees.loc[ratio.index[bad_ratio], ["open", "high", "low", "close", "adj_close"]] = np.nan
ca = pd.read_csv(HERE.parent / "06_data" / "corporate_actions_NIFTYBEES.csv", parse_dates=["ex_date"])
log("corp_action", "Split 2019-12-19 (10:1, NSE/CML/42873): Yahoo history is already ÷10 except the 19–20 Dec rows "
    "(double-adjusted). Those are what the ratio test just caught.")

# %% [markdown]
# 4b. Dividends: Yahoo's Adj Close == Close for NIFTYBEES (no dividends applied), and vendors disagree on which dividends
#     happened. Evidence check: on a real ex-date the ETF should under-perform the index by ≈ dividend/price.
# %%
er, ir = bees["close"].pct_change(), nifty["close"].pct_change()
gap_sd = (er - ir).loc[:"2018"].std()
print(f"\nDividend evidence (typical daily ETF-index gap sd = {gap_sd:.2%}):")
for _, r in ca[ca.action == "dividend"].iterrows():
    d0 = r.ex_date
    if d0 not in bees.index or d0 >= BOUNDARY: print(f"  {d0.date()} {r.status:32s} no ETF price that day / outside explore"); continue
    seen, exp = er[d0] - ir[d0], -r.value_per_post_split_unit / bees["close"].shift(1)[d0]
    z = (seen - exp) / gap_sd
    print(f"  {d0.date()} {r.status:32s} seen {seen:+.2%} expected {exp:+.2%} (z {z:+.1f})")
log("corp_action", "Only 2012-03-09 has a clean price signature; 2013–2015 dividends are vendor-disputed. "
    "Resolve from the AMC's IDCW history before trusting the ETF total-return series.")

# %% [markdown]
# ## 5. Build the series you'd actually trade
# Total return of the ETF = price change + dividend on the ex-date. Policy here: apply only
# `price_evidence_strong`/`verified_primary` dividends; report the sensitivity of including the disputed ones.
# %%
def etf_tr(policy):
    use = ca[(ca.action == "dividend") & ca.status.isin(policy)]
    div = pd.Series(0.0, index=bees.index)
    for _, r in use.iterrows():
        if r.ex_date in div.index: div[r.ex_date] = r.value_per_post_split_unit
    return (bees["close"] + div) / bees["close"].shift(1) - 1
tr_strict = etf_tr(["price_evidence_strong", "verified_primary"])
tr_all = etf_tr(["price_evidence_strong", "verified_primary", "disputed_price_evidence_weak", "disputed_vendor_conflict"])
ann = lambda r: (1 + r.loc["2009":"2018"].fillna(0)).prod() ** (1 / 10) - 1
print(f"\nNIFTYBEES 2009–2018 CAGR: price only {ann(er):.2%} | strict dividends {ann(tr_strict):.2%} | all claimed {ann(tr_all):.2%}")
log("series", "The dividend policy moves the ETF's 10-yr CAGR; write the policy in the pre-reg/data README.")

# %% [markdown]
# ## 6. Write Parquet + manifest. Holdout goes to a separate sealed file.
# %%
def to_parquet(df, name, meta):
    t = pa.Table.from_pandas(df.reset_index())
    t = t.replace_schema_metadata({**(t.schema.metadata or {}), b"hark_meta": json.dumps(meta).encode()})
    p = OUT / f"{name}.parquet"; pq.write_table(t, p, compression="zstd"); return p, sha(p)
clean = pd.DataFrame({"nifty_close": nifty["close"], "bees_close": bees["close"],
                      "bees_ret_price": er, "bees_ret_tr_strict": tr_strict}).dropna(how="all")
meta = {"built_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "raw_sha256": fingerprints,
        "tz": "session_date = NSE session (Asia/Kolkata); close 15:30 IST", "dividend_policy": "strict",
        "holdout_boundary": str(BOUNDARY.date())}
p1, h1 = to_parquet(clean[clean.index < BOUNDARY], "explore_2018", meta)
p2, h2 = to_parquet(clean[clean.index >= BOUNDARY], "HOLDOUT_SEALED", {**meta, "sealed": True})
manifest = {"files": {p1.name: h1, p2.name: h2}, **meta, "log": LOG}
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
print(f"\nWrote {p1.name} ({(clean.index < BOUNDARY).sum()} rows) and {p2.name} (sealed). Manifest has {len(LOG)} log notes.")

def load(name="explore_2018"):
    """The ONLY way your backtests read data. The holdout needs an explicit, logged unlock (Day 20)."""
    if "HOLDOUT" in name and os.environ.get("HOLDOUT_UNLOCK") != "DAY20-PREREG-v1":
        raise PermissionError("Holdout is sealed until Day 20. Set HOLDOUT_UNLOCK=DAY20-PREREG-v1 and log it.")
    p = OUT / f"{name}.parquet"
    assert sha(p) == json.loads((OUT / "manifest.json").read_text())["files"][p.name], "file changed since manifest!"
    return pd.read_parquet(p).set_index("session_date")
print("load() →", load().index.max().date())
try: load("HOLDOUT_SEALED")
except PermissionError as e: print("load('HOLDOUT_SEALED') →", e)

# %% [markdown]
# ## 7. Timezone trap: the S&P 500 close is AFTER the next NSE open
# US close 16:00 New York = 01:30/02:30 IST the next calendar day. Joining by calendar date lets "today's" S&P
# return predict "today's" NIFTY: a look-ahead.
# %%
s = spx.loc["2018-03-06", "close_ts"]          # a Tuesday
print(f"\nS&P close {s} = {s.tz_convert('Asia/Kolkata')} IST → first usable in the NSE session of "
      f"{(s.tz_convert('Asia/Kolkata')).date()} (Wed), not {s.date()} (Tue)")
j = pd.concat([nifty["close"].pct_change().rename("nifty"), spx["close"].pct_change().rename("spx")], axis=1).loc[:"2018"].dropna()
print(f"corr(NIFTY_t, SPX_t)   same calendar date = {j.nifty.corr(j.spx):+.2f}  ← partly impossible to trade")
print(f"corr(NIFTY_t, SPX_t-1) properly lagged     = {j.nifty.corr(j.spx.shift(1)):+.2f}  ← what you could know")
