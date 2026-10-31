"""
walk_forward.py: Day 18. Walk-forward selection + parameter-stability heat maps. Exploration window only (<= 2018-12-31).

    python walk_forward.py                       # pre-registered grid 8/10/12 + the 6..14m neighbourhood diagnostic
    python walk_forward.py --no-neighbourhood    # grid only (fewer trials)
    python walk_forward.py --trade ../my_data/NIFTYBEES_nse.csv

The question: "If I had RE-PICKED the best Faber length every January using only the past, would I have beaten
just sticking with the pre-registered 10m?" If not, the choice of parameter carries no information: good.
That means the result doesn't hinge on a lucky pick.

Outputs (wf_out/): stability_report.md, heatmap_year_x_param.png, heatmap_neighbourhood.png, wf_equity.png, wf_results.json
"""
import argparse, json, math, os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from engine import load_frame, DataFeed, Engine, FaberMonthly, Constant, VolTargetSizer, CostModel, CashModel
from is_report import GateUntil, common_start, cash_series, max_dd

HERE = os.path.dirname(os.path.abspath(__file__))
SWITCH_COST = 0.00139   # Day 10 ETF round trip ~13.9 bps; charged on |w_new - w_old| when a WF switch changes exposure

def run_variant(df, months, t0, cash):
    strat = GateUntil(Constant(1.0), t0) if months == 0 else GateUntil(FaberMonthly(months), t0)
    r = Engine(DataFeed(df), strat, VolTargetSizer(None), CostModel(), cash).run()
    return r.equity.loc[t0:], r.weights.loc[t0:]

def sharpe_xs(r, c):
    x = r - c.reindex(r.index).fillna(0)
    return float(x.mean() / x.std() * math.sqrt(252)) if x.std() > 0 else 0.0

def walk_forward(rets, wts, cash_d, grid, scheme, min_train_years=3, roll_years=5):
    """Each January: pick argmax Sharpe(xs cash) on the training window, hold that variant all year.
    expanding = all history so far; rolling = last `roll_years`. Ties -> pre-registered order (primary first)."""
    years = sorted(set(rets.index.year)); first = years[0]
    out, picks = [], {}
    for y in years:
        if y - first < min_train_years: continue
        lo = pd.Timestamp(f"{first if scheme == 'expanding' else max(first, y - roll_years)}-01-01")
        tr = rets.loc[lo:pd.Timestamp(f"{y-1}-12-31")]
        scores = {m: sharpe_xs(tr[m], cash_d) for m in grid}
        best = max(grid, key=lambda m: scores[m]); picks[y] = (best, scores)
        te = rets.loc[str(y), best].copy()
        prev = picks.get(y - 1, (None,))[0]
        if prev is not None and prev != best:          # switching variants can change exposure on 1 Jan
            dw = abs(wts.loc[str(y), best].iloc[0] - wts.loc[str(y), prev].iloc[0])
            te.iloc[0] -= dw * SWITCH_COST
        out.append(te)
    return pd.concat(out), picks

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--signal", default=os.path.join(HERE, "../06_data/NIFTY50_daily_IS_to_2018-12-31.csv"))
    ap.add_argument("--trade", default=None)
    ap.add_argument("--cash", default=os.path.join(HERE, "../06_data/india_cash_rate_monthly_2007_2018.csv"))
    ap.add_argument("--grid", default="8,10,12"); ap.add_argument("--primary", type=int, default=10)
    ap.add_argument("--no-neighbourhood", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "wf_out"))
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)

    df = load_frame(a.signal, a.trade or a.signal)
    grid = list(map(int, a.grid.split(",")))
    hood = [] if a.no_neighbourhood else [m for m in range(6, 15) if m not in grid]
    t0 = common_start(df, max(grid + hood))                     # every variant (incl. 14m) starts on the same day
    cash = CashModel(cash_series(a.cash))
    cash_d = pd.Series([cash.growth(d0, d1) - 1 for d0, d1 in zip(df.index[:-1], df.index[1:])], index=df.index[1:])

    eqs, wts = {}, {}
    for m in [0] + sorted(grid + hood):
        eqs[m], wts[m] = run_variant(df, m, t0, cash)
    rets = pd.DataFrame({m: e.pct_change() for m, e in eqs.items()}).dropna()
    W = pd.DataFrame(wts).reindex(rets.index)

    # ---- 1. walk-forward selection over the PRE-REGISTERED grid only
    wf = {}
    for scheme in ("expanding", "rolling"):
        r, picks = walk_forward(rets, W, cash_d, grid, scheme); wf[scheme] = (r, picks)
    test_idx = wf["expanding"][0].index
    def summ(r):
        eq = (1 + r).cumprod(); yrs = len(r) / 252
        return dict(CAGR=eq.iloc[-1] ** (1 / yrs) - 1, vol=r.std() * math.sqrt(252), sharpe_xs=sharpe_xs(r, cash_d), max_dd=max_dd(eq))
    rows = {"WF expanding (re-pick each Jan)": summ(wf["expanding"][0]),
            "WF rolling 5y (re-pick each Jan)": summ(wf["rolling"][0]),
            f"Fixed {a.primary}m (pre-registered)": summ(rets.loc[test_idx, a.primary]),
            "Buy & hold": summ(rets.loc[test_idx, 0])}
    for m in grid:
        if m != a.primary: rows[f"Fixed {m}m (hindsight check)"] = summ(rets.loc[test_idx, m])
    # Walk-forward efficiency (Pardo): annualised OOS return of the picked variant / its annualised IS return when picked
    wfe = {}
    for scheme, (r, picks) in wf.items():
        oos, ins = [], []
        for y, (m, _) in picks.items():
            first = rets.index.year.min()
            lo = pd.Timestamp(f"{first if scheme == 'expanding' else max(first, y - 5)}-01-01")
            ins.append(rets.loc[lo:pd.Timestamp(f"{y-1}-12-31"), m].mean() * 252); oos.append(rets.loc[str(y), m].mean() * 252)
        wfe[scheme] = float(np.mean(oos) / np.mean(ins)) if np.mean(ins) != 0 else float("nan")

    # ---- 2. heat map: year x parameter, excess return over buy & hold (pp)
    yearly = (1 + rets).groupby(rets.index.year).prod() - 1
    rel = (yearly[sorted(grid + hood)].sub(yearly[0], axis=0)) * 100
    rank = yearly[grid].rank(axis=1, ascending=False)
    fig, ax = plt.subplots(figsize=(1.0 + 0.7 * rel.shape[1], 0.45 * rel.shape[0] + 1.5))
    v = np.nanmax(np.abs(rel.values)); im = ax.imshow(rel.values, cmap="RdYlGn", vmin=-v, vmax=v, aspect="auto")
    ax.set_xticks(range(rel.shape[1])); ax.set_xticklabels([f"{m}m" + ("*" if m in grid else "") for m in rel.columns])
    ax.set_yticks(range(rel.shape[0])); ax.set_yticklabels(rel.index)
    for i in range(rel.shape[0]):
        for j in range(rel.shape[1]):
            ax.text(j, i, f"{rel.values[i, j]:+.0f}", ha="center", va="center", fontsize=7)
    ax.set_title("Year × lookback: return minus buy & hold (pp). * = pre-registered grid", fontsize=9)
    fig.colorbar(im, ax=ax, shrink=0.7); fig.tight_layout(); fig.savefig(os.path.join(a.out, "heatmap_year_x_param.png"), dpi=130); plt.close(fig)

    # ---- 3. neighbourhood plateau: lookback x sub-period Sharpe (diagnostic, every cell is a trial)
    periods = {"2008-09..2011": (t0, "2011-12-31"), "2012..2015": ("2012-01-01", "2015-12-31"), "2016..2018": ("2016-01-01", "2018-12-31"),
               "Full": (t0, "2018-12-31")}
    cols = sorted(grid + hood)
    hm = pd.DataFrame({p: {m: sharpe_xs(rets.loc[s:e, m], cash_d) for m in cols} for p, (s, e) in periods.items()}).T
    fig, ax = plt.subplots(figsize=(1.0 + 0.7 * len(cols), 3.2))
    im = ax.imshow(hm.values, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(cols))); ax.set_xticklabels([f"{m}m" + ("*" if m in grid else "") for m in cols])
    ax.set_yticks(range(len(hm))); ax.set_yticklabels(hm.index)
    for i in range(hm.shape[0]):
        for j in range(hm.shape[1]):
            ax.text(j, i, f"{hm.values[i, j]:.2f}", ha="center", va="center", fontsize=7)
    ax.set_title("Sharpe (xs cash) by lookback and sub-period: plateau or spike?", fontsize=9)
    fig.colorbar(im, ax=ax, shrink=0.8); fig.tight_layout(); fig.savefig(os.path.join(a.out, "heatmap_neighbourhood.png"), dpi=130); plt.close(fig)
    full = hm.loc["Full"]; prim = full[a.primary]
    plateau = dict(primary_sharpe=float(prim), neighbours_mean=float(full.drop(a.primary).mean()),
                   neighbours_min=float(full.drop(a.primary).min()), neighbours_max=float(full.drop(a.primary).max()),
                   primary_rank=int(full.rank(ascending=False)[a.primary]), n_cols=len(cols),
                   share_beating_bh=float((full > sharpe_xs(rets[0], cash_d)).mean()))

    # ---- 4. SPA test (Hansen 2005) via arch: does the BEST of the grid beat buy & hold, allowing for the search?
    spa_res = None
    try:
        from arch.bootstrap import SPA
        xs = rets.sub(cash_d.reindex(rets.index).fillna(0), axis=0)
        spa = SPA(-xs[0].values, -xs[grid].values, block_size=20, reps=2000, seed=18)   # losses = negative returns
        spa.compute(); spa_res = {k: float(v) for k, v in spa.pvalues.items()}
    except Exception as e:
        spa_res = {"error": str(e)}

    # ---- 5. start-date stability: slide the evaluation start month by month; does the pre-registered claim survive?
    starts = [d for d in pd.date_range(common_start(df, max(grid)), "2009-12-31", freq="MS")]
    sd = {}
    for st in starts:
        s0 = df.index[df.index >= st][0]
        ep, _ = run_variant(df, a.primary, s0, cash); eb, _ = run_variant(df, 0, s0, cash)
        rp, rb = ep.pct_change().dropna(), eb.pct_change().dropna()
        sd[f"{s0:%Y-%m}"] = dict(vol_ratio=float(rp.std() / rb.std()), dd_diff_pp=(max_dd(ep) - max_dd(eb)) * 100,
                                 sharpe_diff=sharpe_xs(rp, cash_d) - sharpe_xs(rb, cash_d))
    sdf = pd.DataFrame(sd).T
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.2))
    for ax, c in zip(axs, ["vol_ratio", "dd_diff_pp", "sharpe_diff"]):
        ax.plot(range(len(sdf)), sdf[c], marker="o", ms=3); ax.set_title(c, fontsize=9)
        ax.set_xticks(range(0, len(sdf), 3)); ax.set_xticklabels(sdf.index[::3], rotation=45, fontsize=7)
        ax.axhline(1 if c == "vol_ratio" else 0, color="grey", lw=0.8)
    fig.suptitle(f"Start-date stability: Faber {a.primary}m vs buy & hold, evaluation start slid month by month", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(a.out, "start_date_stability.png"), dpi=130); plt.close(fig)

    # ---- equity chart
    fig, ax = plt.subplots(figsize=(10, 4))
    for name, r in [("WF expanding", wf["expanding"][0]), ("WF rolling 5y", wf["rolling"][0]),
                    (f"Fixed {a.primary}m", rets.loc[test_idx, a.primary]), ("Buy & hold", rets.loc[test_idx, 0])]:
        ax.plot((1 + r).cumprod(), label=name)
    ax.set_yscale("log"); ax.legend(fontsize=8); ax.set_title("Walk-forward test years only (after costs)")
    fig.tight_layout(); fig.savefig(os.path.join(a.out, "wf_equity.png"), dpi=130); plt.close(fig)

    # ---- report
    tbl = pd.DataFrame(rows).T
    f = tbl.copy()
    for c in ["CAGR", "vol", "max_dd"]: f[c] = (tbl[c] * 100).map("{:.1f}%".format)
    f["sharpe_xs"] = tbl.sharpe_xs.map("{:.2f}".format)
    picks_tbl = pd.DataFrame({s: {y: f"{m}m" for y, (m, _) in p.items()} for s, (_, p) in wf.items()})
    n_trials = len(grid) + len(hood) + 2   # variants + 2 WF schemes
    L = ["# Stability report: Faber trend overlay (exploration window)", "",
         f"Window {t0:%Y-%m-%d} → 2018-12-31 (common start for lookbacks up to {max(grid + hood)}m) · test years for WF: "
         f"{test_idx[0]:%Y} to {test_idx[-1]:%Y} · switch cost {SWITCH_COST*1e4:.1f} bps × |Δw|", "",
         "## 1. Walk-forward: re-picking the best length every January vs sticking with the pre-registered one", "",
         f.to_markdown(), "", "Picks each January:", "", picks_tbl.to_markdown(), "",
         f"Walk-forward efficiency (OOS annual return ÷ IS annual return of the pick): expanding {wfe['expanding']:.2f}, rolling {wfe['rolling']:.2f}", "",
         "## 2. Heat map: year × lookback (return minus buy & hold, pp)", "", "![](heatmap_year_x_param.png)", "",
         "Rank of each pre-registered length per year (1 = best):", "", rank.astype(int).to_markdown(), "",
         "## 3. Neighbourhood plateau (Sharpe xs cash; DIAGNOSTIC: every cell is a trial)", "", "![](heatmap_neighbourhood.png)", "",
         hm.round(2).to_markdown(), "", f"Plateau summary: {json.dumps({k: round(v, 3) if isinstance(v, float) else v for k, v in plateau.items()})}", "",
         "## 4. Hansen SPA: does the best grid member beat buy & hold after allowing for the search?", "",
         f"p-values (lower, consistent, upper): {json.dumps({k: round(v, 3) for k, v in spa_res.items()}) if 'error' not in spa_res else spa_res}", "",
         "## 5. Start-date stability (same strategy, evaluation start slid month by month)", "",
         "![](start_date_stability.png)", "", sdf.round(2).to_markdown(), "",
         f"Vol ratio range {sdf.vol_ratio.min():.2f} to {sdf.vol_ratio.max():.2f} · DD difference range {sdf.dd_diff_pp.min():+.1f} to {sdf.dd_diff_pp.max():+.1f} pp · "
         f"Sharpe difference range {sdf.sharpe_diff.min():+.2f} to {sdf.sharpe_diff.max():+.2f}", "",
         "## 6. Trial accounting", "", f"- Variants run today: {len(grid)} grid + {len(hood)} neighbourhood + 2 WF schemes = **{n_trials}**. Add them to trial-log.csv.",
         "- None of these may replace the pre-registered primary. Day 18 asks whether the result depends on the pick, not which pick is best.", "",
         "![](wf_equity.png)"]
    open(os.path.join(a.out, "stability_report.md"), "w").write("\n".join(L))
    json.dump(dict(t0=str(t0.date()), rows=rows, wfe=wfe, picks={s: {int(y): m for y, (m, _) in p.items()} for s, (_, p) in wf.items()},
                   neighbourhood=hm.round(4).to_dict(), plateau=plateau, spa=spa_res, n_trials=n_trials, start_dates=sdf.round(4).to_dict()),
              open(os.path.join(a.out, "wf_results.json"), "w"), indent=1, default=float)
    print(f.to_string()); print(picks_tbl.to_string()); print("WFE", wfe); print(hm.round(2).to_string()); print("plateau", plateau); print("SPA", spa_res); print(sdf.round(2).to_string())

if __name__ == "__main__":
    main()
