"""
is_report.py: Day 17 in-sample report generator (exploration window only: 2007-09 -> 2018-12-31).

    python is_report.py                                   # demo config (index stand-in, OECD cash)
    python is_report.py --trade ../my_data/NIFTYBEES_nse.csv --prereg ../my_prereg.md --lock ../LOCK.txt

What it does, in order:
  1. Verifies your pre-registration hash against LOCK.txt (refuses to run if the pre-reg changed).
  2. Loads data through engine.load_frame (2019+ sealed). Cash = monthly OECD rate, lagged one month (no look-ahead).
  3. Runs EVERY pre-registered variant (benchmark + primary + fixed grid), all through engine v2 with costs.
  4. Point estimates + stationary-bootstrap 90% intervals (Politis & Romano 1994) for Sharpe (excess of cash) and the
     paired overlay statistics (vol ratio, max-DD difference, CAGR give-up) vs the benchmark.
  5. Sub-periods (calendar years + 3 regimes), cost drag, exposure, turnover, longest time under water.
  6. Trial count from trial-log.csv: N, Sharpe variance across trials (the DSR inputs for Day 20), effective N.
  7. Writes IS_report.md, is_results.json, 3 charts and a reproducibility manifest (hashes of code + data).
In-sample numbers are DESCRIPTION, not evidence. The test is on Day 20.
"""
import argparse, hashlib, json, math, os, platform, sys
from datetime import datetime
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from engine import load_frame, DataFeed, Engine, Strategy, FaberMonthly, Constant, VolTargetSizer, CostModel, CashModel

HERE = os.path.dirname(os.path.abspath(__file__))
REGIMES = {"GFC crash (from eval start to 2009-03)": ("2007-09-01", "2009-03-31"),
           "Recovery & taper (2009-04 to 2013-12)": ("2009-04-01", "2013-12-31"),
           "2014 to 2018": ("2014-01-01", "2018-12-31")}

class GateUntil(Strategy):
    """Warm-up alignment: the inner strategy sees every bar (so its state builds) but holds 0 until `start`.
    Without this, a 10m filter is FLAT for its first 10 months by construction, while buy & hold is fully invested:
    in 2007-08 that hands the filter a free pass through the GFC crash. That's a warm-up artifact, not a skill."""
    def __init__(self, inner, start): self.inner, self.start = inner, start
    def on_bar(self, feed):
        w = self.inner.on_bar(feed)
        return w if feed.now >= self.start else 0.0

def common_start(df, longest):
    """First session of the month after the `longest`-th month-end: the first day EVERY variant has a real signal."""
    me = df.index.to_series().groupby([df.index.year, df.index.month]).last()
    first_signal_month = me.iloc[longest - 1] + pd.offsets.MonthBegin(1)
    return df.index[df.index >= first_signal_month][0]

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def verify_lock(prereg, lock):
    if not prereg: return "NOT CHECKED (no --prereg given): demo mode only"
    h = sha(prereg); txt = open(lock).read() if lock else ""
    if h not in txt: sys.exit(f"STOP: pre-registration hash {h[:12]}... is not in {lock}. Changed pre-reg = v2 + trial count up.")
    return f"OK: {os.path.basename(prereg)} sha256 {h[:16]}... matches LOCK"

def cash_series(path):
    m = pd.read_csv(path)
    s = pd.Series(m.cash_rate_used_pct.values / 100, index=pd.to_datetime(m.TIME_PERIOD) + pd.offsets.MonthBegin(1))
    return s.sort_index()   # month M's average becomes usable on the 1st of M+1: no look-ahead

# ------------------------------------------------------------------ statistics
def max_dd(eq):
    return float((eq / eq.cummax() - 1).min())

def longest_underwater_days(eq):
    peak = eq.cummax(); uw = eq < peak; best = cur = 0; start = None
    for d, u in uw.items():
        if u: start = start or d; cur = (d - start).days; best = max(best, cur)
        else: start = None
    return best

def stats(eq, cash_daily):
    r = eq.pct_change().dropna(); c = cash_daily.reindex(r.index).fillna(0); x = r - c
    yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    return dict(CAGR=(eq.iloc[-1] / eq.iloc[0]) ** (1 / yrs) - 1, vol=r.std() * math.sqrt(252),
                sharpe_xs=x.mean() / x.std() * math.sqrt(252), max_dd=max_dd(eq),
                calmar=((eq.iloc[-1] / eq.iloc[0]) ** (1 / yrs) - 1) / abs(max_dd(eq)),
                longest_underwater_days=longest_underwater_days(eq), years=yrs)

def lo_se(sr_ann, x):
    """IID large-sample SE of an annualised Sharpe (Lo 2002, eq. 6 scaled): sqrt((1 + SR_d^2/2) / n) * sqrt(252).
    Daily returns are fat-tailed and autocorrelated, so treat this as a floor; quote the bootstrap band."""
    n = len(x); srd = sr_ann / math.sqrt(252)
    return math.sqrt((1 + 0.5 * srd ** 2) / n) * math.sqrt(252)

def stationary_idx(n, mean_block, reps, rng):
    """Politis-Romano stationary bootstrap: geometric block lengths, wrap-around."""
    p = 1.0 / mean_block; idx = np.empty((reps, n), dtype=np.int64)
    idx[:, 0] = rng.integers(0, n, reps)
    new = rng.random((reps, n)) < p; jump = rng.integers(0, n, (reps, n))
    for t in range(1, n):
        idx[:, t] = np.where(new[:, t], jump[:, t], (idx[:, t - 1] + 1) % n)
    return idx

def boot(rets: pd.DataFrame, cash, bench, reps=2000, block=20, seed=17):
    """Resample the SAME days for all strategies (paired), recompute statistics on each pseudo-history."""
    rng = np.random.default_rng(seed); R = rets.values; C = cash.reindex(rets.index).fillna(0).values
    idx = stationary_idx(len(R), block, reps, rng); out = {k: {} for k in rets.columns}
    yrs = len(R) / 252; b = list(rets.columns).index(bench)
    sims = R[idx]                                   # reps x n x k
    xs = sims - C[idx][..., None]
    sr = xs.mean(1) / xs.std(1, ddof=1) * math.sqrt(252)
    vol = sims.std(1, ddof=1) * math.sqrt(252)
    eq = np.cumprod(1 + sims, axis=1); dd = (eq / np.maximum.accumulate(eq, axis=1) - 1).min(1)
    cagr = eq[:, -1, :] ** (1 / yrs) - 1
    for j, k in enumerate(rets.columns):
        q = lambda a: [float(np.quantile(a, 0.05)), float(np.quantile(a, 0.95))]
        out[k] = dict(sharpe_xs_90ci=q(sr[:, j]), P_sharpe_gt_0=float((sr[:, j] > 0).mean()))
        if j != b:
            out[k].update(vol_ratio_90ci=q(vol[:, j] / vol[:, b]), dd_diff_90ci=q(dd[:, j] - dd[:, b]),
                          cagr_giveup_90ci=q(cagr[:, j] - cagr[:, b]),
                          P_dd_shallower=float((dd[:, j] > dd[:, b]).mean()))
    return out

def effective_n(rets: pd.DataFrame):
    """Participation-ratio effective number of independent trials: (sum lambda)^2 / sum lambda^2."""
    if rets.shape[1] < 2: return float(rets.shape[1])
    lam = np.clip(np.linalg.eigvalsh(np.corrcoef(rets.values.T)), 0, None)
    return float(lam.sum() ** 2 / (lam ** 2).sum())

def trial_summary(path, family):
    if not os.path.exists(path): return dict(note="no trial-log.csv found")
    t = pd.read_csv(path)
    fam = t[t.family == family] if "family" in t else t
    s = pd.to_numeric(fam.get("is_sharpe_xs"), errors="coerce").dropna()
    return dict(total_trials_logged=int(len(t)), trials_in_family=int(len(fam)),
                sharpe_var_in_family=float(s.var(ddof=1)) if len(s) > 1 else None,
                note="Day 20 DSR uses N = trials_in_family (or effective N, justified) and this variance.")

# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--signal", default=os.path.join(HERE, "../06_data/NIFTY50_daily_IS_to_2018-12-31.csv"))
    ap.add_argument("--trade", default=None, help="NSE-rebuilt NIFTYBEES CSV (Date, Close). Default: index stand-in")
    ap.add_argument("--cash", default=os.path.join(HERE, "../06_data/india_cash_rate_monthly_2007_2018.csv"))
    ap.add_argument("--prereg", default=None); ap.add_argument("--lock", default=None)
    ap.add_argument("--primary", type=int, default=10); ap.add_argument("--grid", default="8,10,12")
    ap.add_argument("--trials", default=os.path.join(HERE, "../04_templates/trial-log.csv"))
    ap.add_argument("--reps", type=int, default=2000); ap.add_argument("--block", type=int, default=20)
    ap.add_argument("--out", default=os.path.join(HERE, "is_out"))
    ap.add_argument("--no-align", action="store_true", help="evaluate from the data start (shows the warm-up artifact)")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)

    lock_status = verify_lock(a.prereg, a.lock)
    df = load_frame(a.signal, a.trade or a.signal)                       # raises if any 2019+ row
    standin = a.trade is None
    cash = CashModel(cash_series(a.cash))
    cash_daily = pd.Series([cash.growth(d0, d1) - 1 for d0, d1 in zip(df.index[:-1], df.index[1:])], index=df.index[1:])

    runs = {"Buy & hold (benchmark)": lambda: Constant(1.0)}   # factories: a strategy object holds state, never reuse one
    for m in map(int, a.grid.split(",")):
        runs[f"Faber {m}m" + (" (PRIMARY)" if m == a.primary else " (grid)")] = (lambda m=m: FaberMonthly(months=m))
    grid = list(map(int, a.grid.split(",")))
    t0 = df.index[1] if a.no_align else common_start(df, max(grid))
    raw = {k: f for k, f in runs.items()}
    runs = {k: (lambda f=f: GateUntil(f(), t0)) for k, f in raw.items()}
    res, rows = {}, {}
    for name, strat in runs.items():
        r = Engine(DataFeed(df), strat(), VolTargetSizer(None), CostModel(), cash).run()
        r.equity = r.equity.loc[t0:]; r.weights = r.weights.loc[t0:]; res[name] = r
        s = stats(r.equity, cash_daily); yrs = s["years"]
        turnover = r.trades["value"].sum() / r.equity.mean() / yrs if len(r.trades) else 0.0
        gross = Engine(DataFeed(df), strat(), VolTargetSizer(None), CostModel(0, use_nse=False), cash).run(); gross.equity = gross.equity.loc[t0:]
        drag = (stats(gross.equity, cash_daily)["CAGR"] - s["CAGR"]) * 1e4
        x = r.equity.pct_change().dropna() - cash_daily.reindex(r.equity.index[1:]).fillna(0)
        rows[name] = {**s, "sharpe_se_iid": lo_se(s["sharpe_xs"], x), "exposure": float(r.weights.mean()),
                      "trades": int(len(r.trades)), "turnover_x_per_yr": turnover, "cost_drag_bps_per_yr": drag,
                      "costs_inr": float(r.total_costs), "interest_inr": float(r.total_interest)}
    bench = "Buy & hold (benchmark)"
    prk = next(k for k in raw if "PRIMARY" in k)
    unal = {k: Engine(DataFeed(df), raw[k](), VolTargetSizer(None), CostModel(), cash).run().equity for k in (bench, prk)}
    artifact = dict(dd_diff_unaligned=max_dd(unal[prk]) - max_dd(unal[bench]))
    rets = pd.DataFrame({k: v.equity.pct_change() for k, v in res.items()}).dropna()
    bs = boot(rets, cash_daily, bench, a.reps, a.block)

    sub = {}
    for k, v in res.items():
        y = v.equity.resample("YE").last(); y = pd.concat([v.equity.iloc[:1], y]); sub[k] = y.pct_change().dropna()
    yearly = pd.DataFrame(sub); yearly.index = yearly.index.year
    reg = {k: {g: float(v.equity.loc[s:e].iloc[-1] / v.equity.loc[s:e].iloc[0] - 1) for g, (s, e) in REGIMES.items()}
           for k, v in res.items()}
    trials = trial_summary(a.trials, "trend-overlay")
    neff = effective_n(rets.drop(columns=bench))

    # charts
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for k, v in res.items(): ax.plot(v.equity / v.equity.iloc[0], label=k, lw=1.6 if "PRIMARY" in k or k == bench else 0.9)
    ax.set_yscale("log"); ax.set_title(f"Growth of 1 (log), in-sample {t0:%Y-%m} to 2018-12, after costs"); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(a.out, "equity.png"), dpi=130); plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 3.5))
    for k in (bench, next(k for k in res if "PRIMARY" in k)):
        e = res[k].equity; ax.fill_between(e.index, e / e.cummax() - 1, 0, alpha=0.4, label=k)
    ax.set_title("Underwater (drawdown from peak)"); ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(os.path.join(a.out, "underwater.png"), dpi=130); plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 3.5))
    for k in (bench, next(k for k in res if "PRIMARY" in k)):
        ax.plot(rets[k].rolling(252).std() * math.sqrt(252), label=k)
    ax.set_title("Rolling 1-year volatility"); ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig(os.path.join(a.out, "rolling_vol.png"), dpi=130); plt.close(fig)

    # report
    tbl = pd.DataFrame(rows).T
    fmt = tbl.copy()
    for c in ["CAGR", "vol", "max_dd", "exposure"]: fmt[c] = (tbl[c] * 100).map("{:.1f}%".format)
    for c in ["sharpe_xs", "sharpe_se_iid", "calmar", "turnover_x_per_yr"]: fmt[c] = tbl[c].map("{:.2f}".format)
    fmt["cost_drag_bps_per_yr"] = tbl.cost_drag_bps_per_yr.map("{:.0f}".format)
    fmt["costs_inr"] = tbl.costs_inr.map("₹{:,.0f}".format); fmt["interest_inr"] = tbl.interest_inr.map("₹{:,.0f}".format)
    fmt = fmt.drop(columns=["years"])
    pr = next(k for k in res if "PRIMARY" in k); b = bs[pr]
    f = lambda ci, pct=True: (f"{ci[0]*100:+.1f} pp to {ci[1]*100:+.1f} pp" if pct else f"{ci[0]:.2f} to {ci[1]:.2f}")
    lines = [f"# In-sample report: Faber trend overlay on NIFTY 50", "",
             f"Generated {datetime.now():%Y-%m-%d %H:%M} · window {df.index[0]:%Y-%m-%d} → {df.index[-1]:%Y-%m-%d} "
             f"({len(df)} sessions) · holdout 2019-01-01+ SEALED", "",
             f"- **Evaluation starts {t0:%Y-%m-%d}**: the first session on which every variant (longest = {max(grid)}m) has a real signal. "
             f"All runs hold 0 before it. Unaligned, the primary's max-DD advantage would read {artifact['dd_diff_unaligned']*100:+.1f} pp "
             f"vs {(rows[pr]['max_dd']-rows[bench]['max_dd'])*100:+.1f} pp aligned: the gap is warm-up luck, not skill.",
             f"- Pre-registration: {lock_status}",
             f"- Trade series: {'INDEX STAND-IN (not tradable: replace with NSE-rebuilt NIFTYBEES before Gate 3)' if standin else a.trade}",
             "- Cash: OECD monthly India rates, lagged 1 month (see 06_data notes; 2007-09→2011-10 provisional)",
             "- Costs: 5 bps/side slippage + NSE statutory (nse_costs.py, rates as of 2026-10-31 applied to the past)",
             f"- Bootstrap: stationary, mean block {a.block} sessions, {a.reps} paired resamples, seed 17", "",
             "## 1. Every pre-registered run (all count as trials)", "", fmt.to_markdown(), "",
             "Interest and costs in ₹ cover the whole run, warm-up included. Sharpe is excess of the cash series. `sharpe_se_iid` is the IID large-sample SE (Lo 2002); bootstrap bands below are the ones to quote.", "",
             f"## 2. Primary vs benchmark, with 90% bootstrap bands", "",
             f"| Statistic | Point | 90% band |", "|---|---|---|",
             f"| Sharpe (xs cash), primary | {rows[pr]['sharpe_xs']:.2f} | {f(b['sharpe_xs_90ci'], False)} |",
             f"| Sharpe (xs cash), buy & hold | {rows[bench]['sharpe_xs']:.2f} | {f(bs[bench]['sharpe_xs_90ci'], False)} |",
             f"| Vol ratio (primary / B&H) | {rows[pr]['vol']/rows[bench]['vol']:.2f} | {f(b['vol_ratio_90ci'], False)} |",
             f"| Max-DD difference (primary − B&H) | {(rows[pr]['max_dd']-rows[bench]['max_dd'])*100:+.1f} pp | {f(b['dd_diff_90ci'])} |",
             f"| CAGR give-up (primary − B&H) | {(rows[pr]['CAGR']-rows[bench]['CAGR'])*100:+.1f} pp | {f(b['cagr_giveup_90ci'])} |",
             f"| P(DD shallower than B&H) | | {b['P_dd_shallower']:.0%} |", "",
             "## 3. Calendar years (total return; first year is partial)", "", (yearly * 100).round(1).to_markdown(), "",
             "## 4. Regimes (total return)", "", (pd.DataFrame(reg) * 100).round(1).to_markdown(), "",
             "## 5. Trial accounting", "",
             f"- Variants run today: {len(runs)} (1 benchmark + {len(runs)-1} pre-registered Faber lengths)",
             f"- Effective number of independent Faber trials (eigenvalue participation ratio): {neff:.2f}",
             f"- From trial-log.csv: {json.dumps(trials)}", "",
             "## 6. What this report is NOT", "",
             "- Not a test. Every number above was seen during design (Days 8 to 12). The holdout on Day 20 is the test.",
             "- Not a reason to change the primary. Grid rows are for the Day 18 stability check, not for picking a winner.",
             "", "![equity](equity.png)", "![underwater](underwater.png)", "![rolling vol](rolling_vol.png)"]
    open(os.path.join(a.out, "IS_report.md"), "w").write("\n".join(lines))
    json.dump(dict(eval_start=str(t0.date()), rows=rows, bootstrap=bs, regimes=reg, trials=trials, effective_n=neff, **artifact), 
              open(os.path.join(a.out, "is_results.json"), "w"), indent=1, default=float)
    man = dict(created=datetime.now().isoformat(timespec="seconds"), python=platform.python_version(),
               numpy=np.__version__, pandas=pd.__version__, args=vars(a),
               sha256={os.path.basename(p): sha(p) for p in [__file__, os.path.join(HERE, "engine.py"),
                       os.path.join(HERE, "nse_costs.py"), a.signal, a.cash] + ([a.trade] if a.trade else [])})
    json.dump(man, open(os.path.join(a.out, "manifest.json"), "w"), indent=1)
    print(fmt.to_string()); print("\nPrimary vs B&H bootstrap:", json.dumps(b, indent=1)); print("effective N:", round(neff, 2))
    print(f"\nWrote {a.out}/IS_report.md")

if __name__ == "__main__":
    main()
