"""
stress.py: Day 19. Try to break the pre-registered Faber overlay BEFORE the holdout does. Data <= 2018-12-31 only.

    python stress.py                                   # demo on the index stand-in
    python stress.py --trade ../my_data/NIFTYBEES_nse.csv --vol-ratio-max 0.85 --dd-edge-min 5
    (pass YOUR pre-registered falsifier thresholds; the defaults are placeholders)

Stresses (each one is a question a sceptic would ask):
  S1 costs ×2, ×3            "your 5 bps slippage is a guess"
  S2 delay +1, +2, +5 bars   "you won't fill on the close you decided on"
  S3 timing luck             "why the FIRST session of the month? try days 1..15"   (Hoffstein et al. 2019/2020)
  S4 drop best N trades      "how much rests on a few lucky round trips?"
  S5 drop best N days        "how much rests on a few days?"
  S6 cash rate −1 pp         "your 2007–2011 cash series is provisional"
  S7 random-timing null      "is the vol cut TIMING, or just being in cash ~30% of the time?"
  S8 stationary bootstrap    "how wide is the noise band on each claim?"
Outputs (stress_out/): stress_report.md, stress_table.csv, timing_luck.png, random_timing.png, bootstrap.png, stress_results.json
"""
import argparse, json, math, os
from dataclasses import dataclass
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from engine import load_frame, DataFeed, Engine, Strategy, FaberMonthly, Constant, VolTargetSizer, CostModel, CashModel
from is_report import GateUntil, common_start, cash_series, max_dd, stationary_idx

HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ stress building blocks
@dataclass
class ScaledCost(CostModel):
    mult: float = 1.0
    def fill_price(self, px, side):
        k = self.slippage_bps * self.mult / 1e4
        return px * (1 + k) if side == "buy" else px * (1 - k)
    def fees(self, value, side):
        return super().fees(value, side) * self.mult

class Delay(Strategy):
    """Return the target decided k bars EARLIER. k=0 = unchanged. The engine already fills at t+1 close; Delay(k)
    makes that t+1+k. On a monthly rule, Delay(k) is the same as deciding on the (k+1)-th session of the month."""
    def __init__(self, inner, k): self.inner, self.k, self.buf = inner, k, []
    def on_bar(self, feed):
        self.buf.append(self.inner.on_bar(feed))
        return self.buf[-1 - self.k] if len(self.buf) > self.k else 0.0

def run(df, t0, cash, months=10, delay=0, cost_mult=1.0):
    inner = Constant(1.0) if months == 0 else FaberMonthly(months)
    strat = GateUntil(Delay(inner, delay), t0)
    r = Engine(DataFeed(df), strat, VolTargetSizer(None), ScaledCost(mult=cost_mult), cash).run()
    eq = r.equity.loc[t0:]
    return eq, r.weights.loc[t0:]

def stats(eq, cash_d, bench_eq):
    r, rb = eq.pct_change().dropna(), bench_eq.pct_change().dropna()
    c = cash_d.reindex(r.index).fillna(0)
    xs, xb = r - c, rb - c
    yrs = len(r) / 252
    return dict(CAGR=(eq.iloc[-1] / eq.iloc[0]) ** (1 / yrs) - 1, vol=r.std() * math.sqrt(252),
                sharpe_xs=xs.mean() / xs.std() * math.sqrt(252), max_dd=max_dd(eq),
                vol_ratio=r.std() / rb.std(), dd_edge_pp=(max_dd(eq) - max_dd(bench_eq)) * 100,
                sharpe_diff=xs.mean() / xs.std() * math.sqrt(252) - xb.mean() / xb.std() * math.sqrt(252))

def spells(w, thresh=0.5):
    """In-market spells (round trips): list of (start, end) dates where held weight > thresh."""
    on = (w > thresh).astype(int); edges = on.diff().fillna(on.iloc[0])
    starts = list(on.index[edges == 1]); ends = list(on.index[edges == -1])
    if len(ends) < len(starts): ends.append(on.index[-1] + pd.Timedelta(days=1))
    return [(s, e) for s, e in zip(starts, ends)]

def drop_best(r, cash_d, units, n):
    """Replace the n best units (spells or days) with the cash return: as if you had missed them."""
    r = r.copy(); c = cash_d.reindex(r.index).fillna(0)
    if units == "days":
        for d in r.nlargest(n).index: r.loc[d] = c.loc[d]
        return r
    perf = sorted(units, key=lambda se: -(1 + r.loc[se[0]:se[1] - pd.Timedelta(days=1)]).prod())
    for s, e in perf[:n]:
        m = (r.index >= s) & (r.index < e); r[m] = c[m]
    return r

# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--signal", default=os.path.join(HERE, "../06_data/NIFTY50_daily_IS_to_2018-12-31.csv"))
    ap.add_argument("--trade", default=None)
    ap.add_argument("--cash", default=os.path.join(HERE, "../06_data/india_cash_rate_monthly_2007_2018.csv"))
    ap.add_argument("--months", type=int, default=10); ap.add_argument("--longest", type=int, default=12)
    ap.add_argument("--vol-ratio-max", type=float, default=0.85, help="PLACEHOLDER: use your pre-registered value")
    ap.add_argument("--dd-edge-min", type=float, default=5.0, help="PLACEHOLDER (pp): use your pre-registered value")
    ap.add_argument("--reps", type=int, default=1000)
    ap.add_argument("--out", default=os.path.join(HERE, "stress_out"))
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)

    df = load_frame(a.signal, a.trade or a.signal)
    t0 = common_start(df, a.longest)                       # same aligned start as Day 17 (2008-09-01 on the demo)
    rates = cash_series(a.cash); cash = CashModel(rates)
    cash_d = pd.Series([cash.growth(d0, d1) - 1 for d0, d1 in zip(df.index[:-1], df.index[1:])], index=df.index[1:])
    bh, _ = run(df, t0, cash, months=0)
    base, wb = run(df, t0, cash, a.months)

    rows = {"Base (pre-registered)": stats(base, cash_d, bh)}
    for m in (2, 3):
        e, _ = run(df, t0, cash, a.months, cost_mult=m); bhm, _ = run(df, t0, cash, 0, cost_mult=m)
        rows[f"S1 costs ×{m}"] = stats(e, cash_d, bhm)
    for k in (1, 2, 5):
        e, _ = run(df, t0, cash, a.months, delay=k); rows[f"S2 delay +{k} bar"] = stats(e, cash_d, bh)

    # S3 timing luck: decision on session 1..15 of the month
    tl = {}
    for k in range(0, 15):
        e, _ = run(df, t0, cash, a.months, delay=k); tl[k + 1] = stats(e, cash_d, bh)
    tl = pd.DataFrame(tl).T
    rows["S3 timing luck: worst day"] = tl.loc[tl.dd_edge_pp.idxmin()].to_dict()

    # S4/S5 drop best trades / days
    rb = base.pct_change().dropna(); sp = spells(wb.reindex(rb.index).shift(1).fillna(0))
    def eq_of(r): return (1 + r).cumprod() * base.iloc[0]
    for n in (1, 3, 5, 10):
        if n <= len(sp): rows[f"S4 drop best {n} of {len(sp)} trades"] = stats(eq_of(drop_best(rb, cash_d, sp, n)), cash_d, bh)
    for n in (5, 10):
        rows[f"S5 drop best {n} days"] = stats(eq_of(drop_best(rb, cash_d, "days", n)), cash_d, bh)

    # S6 cash −1 pp (both strategies earn the lower rate; Sharpe is measured over the lower cash too)
    cash_lo = CashModel(rates - 0.01)
    cash_d_lo = pd.Series([cash_lo.growth(d0, d1) - 1 for d0, d1 in zip(df.index[:-1], df.index[1:])], index=df.index[1:])
    e, _ = run(df, t0, cash_lo, a.months); bl, _ = run(df, t0, cash_lo, 0)
    rows["S6 cash rate −1 pp"] = stats(e, cash_d_lo, bl)

    tbl = pd.DataFrame(rows).T
    tbl["vol_falsifier"] = np.where(tbl.vol_ratio <= a.vol_ratio_max, "survives", "FAILS")
    tbl["dd_falsifier"] = np.where(tbl.dd_edge_pp >= a.dd_edge_min, "survives", "FAILS")
    ret_only = tbl.index.str.startswith(("S4", "S5"))      # replacing trades with cash LOWERS vol/DD by construction:
    tbl.loc[ret_only, ["vol_falsifier", "dd_falsifier"]] = "n/a (return stress)"   # these rows test the RETURN claim only

    # S7 random-timing null: circularly shift the REAL weight path by a random offset. Same time in market,
    # same number of trades, same spell lengths; only the TIMING is random. Where does the real strategy rank?
    rbh = bh.pct_change().dropna(); w = wb.reindex(rbh.index).shift(1).fillna(0).values
    c = cash_d.reindex(rbh.index).fillna(0).values; R = rbh.values; n = len(R)
    rng = np.random.default_rng(19); sims = []
    turn_cost = 0.00139 / 2                       # per unit of |Δw|, ~13.9 bps round trip (Day 10)
    def path(wv):
        dw = np.abs(np.diff(wv, prepend=0.0))
        r = wv * R + (1 - wv) * c - dw * turn_cost
        return r
    real = path(w)
    for _ in range(a.reps):
        sims.append(path(np.roll(w, rng.integers(60, n - 60))))
    sims = np.array(sims)
    def vr(x): return x.std() / R.std()
    def dd(x): e = np.cumprod(1 + x); return float((e / np.maximum.accumulate(e) - 1).min())
    real_vr, real_dd = vr(real), dd(real)
    sim_vr = np.array([vr(s) for s in sims]); sim_dd = np.array([dd(s) for s in sims])
    rt = dict(time_in_market=float(w.mean()), real_vol_ratio=float(real_vr), sim_vol_ratio_median=float(np.median(sim_vr)),
              p_vol=float((sim_vr <= real_vr).mean()), real_max_dd=real_dd, sim_dd_median=float(np.median(sim_dd)),
              p_dd=float((sim_dd >= real_dd).mean()))

    # S8 stationary bootstrap of paired daily returns: noise band on each claim
    X = np.column_stack([real, R, c]); idx = stationary_idx(n, 20, a.reps, np.random.default_rng(1919))
    bvr, bdd, bsd = [], [], []
    for row in idx:
        s, b, cc = X[row, 0], X[row, 1], X[row, 2]
        bvr.append(s.std() / b.std()); bdd.append((dd(s) - dd(b)) * 100)
        xs, xb = s - cc, b - cc; bsd.append((xs.mean() / xs.std() - xb.mean() / xb.std()) * math.sqrt(252))
    q = lambda v: [float(np.percentile(v, 5)), float(np.percentile(v, 50)), float(np.percentile(v, 95))]
    bs = dict(vol_ratio=q(bvr), dd_edge_pp=q(bdd), sharpe_diff=q(bsd),
              p_vol_falsifier=float((np.array(bvr) <= a.vol_ratio_max).mean()),
              p_dd_falsifier=float((np.array(bdd) >= a.dd_edge_min).mean()))

    # ---- charts
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.2))
    for ax, col in zip(axs, ["vol_ratio", "dd_edge_pp", "sharpe_diff"]):
        ax.bar(tl.index, tl[col]); ax.set_title(f"{col} by decision session of month", fontsize=8); ax.set_xticks(tl.index)
        ax.tick_params(labelsize=7)
    axs[0].axhline(a.vol_ratio_max, color="red", lw=0.8); axs[1].axhline(a.dd_edge_min, color="red", lw=0.8)
    fig.suptitle("S3 timing luck: same rule, decided on session 1..15 of each month (red = falsifier line)", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(a.out, "timing_luck.png"), dpi=130); plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(10, 3.2))
    axs[0].hist(sim_vr, 40); axs[0].axvline(real_vr, color="red"); axs[0].set_title("Vol ratio: random timing vs real (red)", fontsize=9)
    axs[1].hist(np.array(sim_dd) * 100, 40); axs[1].axvline(real_dd * 100, color="red"); axs[1].set_title("Max DD %: random timing vs real (red)", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(a.out, "random_timing.png"), dpi=130); plt.close(fig)

    fig, axs = plt.subplots(1, 3, figsize=(12, 3.2))
    for ax, (nm, v, line) in zip(axs, [("vol ratio", bvr, a.vol_ratio_max), ("DD edge pp", bdd, a.dd_edge_min), ("Sharpe diff", bsd, 0)]):
        ax.hist(v, 40); ax.axvline(line, color="red", lw=0.8); ax.set_title(f"Bootstrap: {nm}", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(a.out, "bootstrap.png"), dpi=130); plt.close(fig)

    # ---- report
    f = tbl.copy()
    for col in ["CAGR", "vol", "max_dd"]: f[col] = (tbl[col] * 100).map("{:.1f}%".format)
    for col in ["sharpe_xs", "vol_ratio", "sharpe_diff"]: f[col] = tbl[col].map("{:.2f}".format)
    f["dd_edge_pp"] = tbl.dd_edge_pp.map("{:+.1f}".format)
    tlf = tl[["vol_ratio", "dd_edge_pp", "sharpe_diff"]].round(2); tlf.index.name = "session"
    L = ["# Stress report: Faber overlay (exploration window)", "",
         f"Window {t0:%Y-%m-%d} → 2018-12-31 · rule {a.months}m · falsifier lines: vol ratio ≤ {a.vol_ratio_max}, DD edge ≥ {a.dd_edge_min} pp "
         "(PLACEHOLDERS unless you passed your pre-registered values)", "",
         "## Scenario table", "", f.to_markdown(), "",
         "## S3 Timing luck (decision session 1–15)", "", "![](timing_luck.png)", "", tlf.to_markdown(), "",
         f"Range: DD edge {tl.dd_edge_pp.min():+.1f} to {tl.dd_edge_pp.max():+.1f} pp · vol ratio {tl.vol_ratio.min():.2f} to {tl.vol_ratio.max():.2f}", "",
         "## S7 Random-timing null (circular shifts of the real weight path)", "", "![](random_timing.png)", "",
         f"Time in market {rt['time_in_market']:.0%}. Real vol ratio {rt['real_vol_ratio']:.2f} vs random-timing median {rt['sim_vol_ratio_median']:.2f} "
         f"(share of random paths at least as low: {rt['p_vol']:.2f}). Real max DD {rt['real_max_dd']:.1%} vs random median {rt['sim_dd_median']:.1%} "
         f"(share at least as shallow: {rt['p_dd']:.2f}).", "",
         "## S8 Stationary bootstrap (mean block 20 days)", "", "![](bootstrap.png)", "",
         f"5/50/95%: vol ratio {np.round(bs['vol_ratio'], 2).tolist()} · DD edge pp {np.round(bs['dd_edge_pp'], 1).tolist()} · Sharpe diff {np.round(bs['sharpe_diff'], 2).tolist()}",
         f"Share of resamples where the falsifier is met: vol {bs['p_vol_falsifier']:.0%} · DD {bs['p_dd_falsifier']:.0%}", "",
         "## Trial accounting", "", "Stress runs are NOT new strategy trials (no rule changed, nothing is selectable). Log them as 'stress' rows, counted_in_dsr = no."]
    open(os.path.join(a.out, "stress_report.md"), "w").write("\n".join(L))
    tbl.to_csv(os.path.join(a.out, "stress_table.csv"))
    json.dump(dict(t0=str(t0.date()), table=tbl.drop(columns=["vol_falsifier", "dd_falsifier"]).round(4).to_dict(orient="index"),
                   timing_luck=tl.round(4).to_dict(orient="index"), random_timing=rt, bootstrap=bs, n_trades=len(sp)),
              open(os.path.join(a.out, "stress_results.json"), "w"), indent=1, default=float)
    print(f.to_string()); print(tlf.to_string()); print("random timing", rt); print("bootstrap", bs)

if __name__ == "__main__":
    main()
