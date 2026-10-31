# %% [markdown]
# # Day 12 build-along: DESIGN THE TEST, THEN LOCK IT
# Three jobs:
# 1. **Power:** can the 2019+ holdout ever show t > 3 for your idea? (Usually no. Know it before you look.)
# 2. **Falsifier sizing:** block-bootstrap the 2008–2018 exploration data to see what a *true* strategy would
#    show in a holdout of the same length. Set kill thresholds that a real effect passes ~90% of the time.
# 3. **Lock:** SHA-256 hash your pre-registration so nobody (including you) can edit it after the fact.
# Uses exploration data only. It never reads anything after 2018-12-31.

# %%
import hashlib, datetime as dt, sys, numpy as np, pandas as pd
from math import erf, sqrt
from pathlib import Path
from nse_costs import round_trip
HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path(".")
DATA = HERE.parent / "07_data"
END, START, CASH = "2018-12-31", "2008-07-01", 0.06
COST = round_trip(1e5, 1e5, "delivery", "etf_equity")["total"] / 1e5 + 2 * 0.0005
HOLDOUT_YEARS = 7.8          # 2019-01 to ~2026-10: the locked sample you'll touch ONCE (Day 20)
Phi = lambda x: 0.5 * (1 + erf(x / sqrt(2)))

# %% [markdown]
# ## 4. LOCK: hash the pre-registration
# `python prereg_designer.py lock ../05_templates/preregistration-template.md`
# writes `<file>.LOCK.txt` with the SHA-256 and UTC time. Then commit + tag + push to GitHub (public timestamp).
# Any later edit changes the hash, and the edit is visible.
# %%
def lock(path):
    p = Path(path); h = hashlib.sha256(p.read_bytes()).hexdigest()
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    out = p.with_suffix(p.suffix + ".LOCK.txt")
    out.write_text(f"file: {p.name}\nsha256: {h}\nlocked_at: {stamp}\n")
    print(f"LOCKED {p.name}\n sha256 {h}\n at {stamp}\n -> git add . && git commit -m 'prereg lock {h[:12]}' "
          f"&& git tag prereg-v1 && git push --tags")
def verify(path):
    p = Path(path); rec = dict(l.split(": ", 1) for l in p.with_suffix(p.suffix + ".LOCK.txt").read_text().splitlines())
    ok = hashlib.sha256(p.read_bytes()).hexdigest() == rec["sha256"]
    print("VERIFIED: unchanged since", rec["locked_at"]) if ok else print("TAMPERED: file differs from the lock!")
if len(sys.argv) == 3 and sys.argv[1] in ("lock", "verify"):
    (lock if sys.argv[1] == "lock" else verify)(sys.argv[2]); sys.exit(0)

# %% [markdown]
# ## 1. Power: P(t > bar) if the true Sharpe is S and you have T years.  t ≈ S·√T + noise(1)
# %%
print("1) POWER: chance a TRUE strategy clears the bar in the holdout")
print(f"{'true SR':>8} | {'years':>5} | P(t>2) | P(t>3) | years needed for E[t]=3")
for S in (0.2, 0.3, 0.5, 0.8):
    for T in (HOLDOUT_YEARS, 18.5):
        m = S * sqrt(T)
        print(f"{S:8.1f} | {T:5.1f} | {1-Phi(2-m):5.0%}  | {1-Phi(3-m):5.0%}  | {(3/S)**2:6.0f}")
print("-> A t>3 bar on 7.8 years of holdout needs Sharpe ≈ 1.1 just for a coin flip. Plan around that.\n")

# %% [markdown]
# ## 2. Rebuild the Day 11 candidates on exploration data (daily, 1-day lag, costs, 6% cash)
# %%
px = pd.read_csv(DATA / "NIFTY50_daily.csv", parse_dates=["Date"], index_col="Date").loc[:END, "Close"].dropna()
mc = px.resample("ME").last()
def strat(n_months):
    sig = (mc > mc.rolling(n_months).mean()).astype(int)
    pos = sig.reindex(px.index, method="ffill").shift(2).fillna(0)        # known at close, trade next day
    cash_d = (1 + CASH) ** (1 / 245) - 1
    r = pos * px.pct_change() + (1 - pos) * cash_d - pos.diff().abs().fillna(0) * COST / 2
    return r.loc[START:]
bh = px.pct_change().loc[START:]
def sharpe(r): return (r.mean() * 245 - CASH) / (r.std() * sqrt(245))

print("2) FIXED GRID (decided by the literature, not by this table): SMA months {8, 10, 12}")
for n in (8, 10, 12):
    r = strat(n); print(f"   SMA {n:2d}m: Sharpe (excess of 6% cash) {sharpe(r):+.2f}   vol {r.std()*sqrt(245):.1%}")
print(f"   Buy & hold: Sharpe {sharpe(bh):+.2f}   vol {bh.std()*sqrt(245):.1%}")
print("   You'll pick the parameter BEFORE reading this (10m, Faber 2007). The grid is for a stability check only.\n")

# %% [markdown]
# ## 3. Falsifier sizing: stationary block bootstrap of 12-month blocks, holdout-length windows
# Question: "if the world in 2019+ looks like 2008–2018, what would the overlay show?"
# The thresholds you write tomorrow should be ones a true effect usually passes. Otherwise you're setting it up to fail
# (too strict) or to always pass (too loose).
# %%
rng = np.random.default_rng(11)
S, B = strat(10).values, bh.values
n, L, H = len(S), 245, int(HOLDOUT_YEARS * 245)
def mdd(x): w = np.cumprod(1 + x); return (w / np.maximum.accumulate(w) - 1).min()
rows = []
for _ in range(2000):
    idx = []
    while len(idx) < H:
        s0 = rng.integers(0, n - L); idx.extend(range(s0, s0 + L))
    idx = np.array(idx[:H]); s, b = S[idx], B[idx]
    rows.append(dict(vol_ratio=s.std() / b.std(), dd_s=mdd(s), dd_b=mdd(b),
                     cagr_gap=(np.prod(1 + s) ** (245 / H) - np.prod(1 + b) ** (245 / H)),
                     t_excess=(s - b).mean() / (s - b).std() * sqrt(H)))
bs = pd.DataFrame(rows)
q = bs.quantile([0.10, 0.50, 0.90]).T
q.columns = ["10th pct", "median", "90th pct"]
print("3) WHAT A TRUE FABER OVERLAY LOOKS LIKE OVER 7.8 YEARS (bootstrap of 2008–2018)")
print(q.round(3).to_string())
print(f"\n   P(overlay maxDD shallower than buy & hold) = {(bs.dd_s > bs.dd_b).mean():.0%}")
print(f"   P(t of return difference > 3)            = {(bs.t_excess > 3).mean():.1%}   <- why return-alpha is the wrong test")
print("   -> A testable overlay hypothesis is about RISK: vol ratio and drawdown, plus a cap on the return give-up.\n"
      "   -> Example falsifier a true overlay passes ~80% of the time: KILL if vol ratio > its 90th pct (worse side)\n"
      "      OR CAGR gap < its 10th pct. Write your own numbers in the pre-reg; don't copy mine.\n")

