"""
holdout_report.py: Day 20, step 2. The one look at 2019-01-01 → end of data.

    python holdout_report.py --pred ../04_templates/predictions.json --full-signal <unzipped NIFTY FULL csv> \
        --cash <unzipped cash 2007_2026 csv> [--trade <your NIFTYBEES FULL csv>]

Refuses to run unless predictions.json matches PREDICTIONS_LOCK.txt. Appends every run to OPENED.log.
The rule, grid, costs and falsifiers are exactly the pre-registered ones. Nothing here is tunable.

Method: the pre-registered rule is run once from the aligned IS start (so its state and its position on
31 Dec 2018 are real), then the equity curve is cut at the 2018-12-31 close. 2019+ is pure out-of-sample.

Outputs (holdout_out/): HOLDOUT_REPORT.md, holdout_equity.png, holdout_drawdown.png, holdout_results.json
"""
import argparse, datetime as dt, hashlib, json, math, os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import norm, skew, kurtosis
from engine import DataFeed, Engine, FaberMonthly, Constant, VolTargetSizer, CostModel, CashModel
from is_report import GateUntil, common_start, cash_series, max_dd, stationary_idx
from stress import spells

HERE = os.path.dirname(os.path.abspath(__file__))
OOS_START = pd.Timestamp("2019-01-01")
GAMMA = 0.5772156649

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

def load_full(signal_csv, trade_csv):
    s = pd.read_csv(signal_csv, parse_dates=["Date"], index_col="Date")["Close"].rename("signal_close")
    t = pd.read_csv(trade_csv, parse_dates=["Date"], index_col="Date")["Close"].rename("trade_close")
    return pd.concat([s, t], axis=1, join="inner").dropna()

def expected_max_z(n):
    return 0.0 if n <= 1 else (1 - GAMMA) * norm.ppf(1 - 1 / n) + GAMMA * norm.ppf(1 - 1 / (n * math.e))

def psr(x, sr_star_daily):
    """Bailey & Lopez de Prado (2012): P(true SR > sr_star) from a sample, adjusting for skew and kurtosis. Daily units."""
    x = np.asarray(x); sr = x.mean() / x.std(ddof=1); g3, g4 = skew(x), kurtosis(x, fisher=False)
    return float(norm.cdf((sr - sr_star_daily) * math.sqrt(len(x) - 1) / math.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr ** 2)))

def ann_sr(x): return float(x.mean() / x.std() * math.sqrt(252))

def run(df, t0, cash, months):
    strat = GateUntil(Constant(1.0) if months == 0 else FaberMonthly(months), t0)
    r = Engine(DataFeed(df), strat, VolTargetSizer(None), CostModel(), cash).run()
    return r.equity.loc[t0:], r.weights.loc[t0:]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True)
    ap.add_argument("--full-signal", required=True); ap.add_argument("--trade", default=None)
    ap.add_argument("--cash", required=True)
    ap.add_argument("--months", type=int, default=10); ap.add_argument("--longest", type=int, default=12)
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--out", default=os.path.join(HERE, "holdout_out"))
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)

    # ---- 0. integrity: predictions sealed and unchanged
    lockp = os.path.join(os.path.dirname(os.path.abspath(a.pred)), "PREDICTIONS_LOCK.txt")
    if not os.path.exists(lockp): sys.exit("STOP: no PREDICTIONS_LOCK.txt. Run seal_predictions.py first.")
    lock = dict(l.split(" ", 1) for l in open(lockp).read().strip().splitlines())
    if sha(a.pred) != lock["predictions_sha256"].strip(): sys.exit("STOP: predictions.json changed after sealing. That's the one unforgivable edit.")
    logp = os.path.join(a.out, "OPENED.log"); prior = open(logp).read().count("\n") if os.path.exists(logp) else 0
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    open(logp, "a").write(f"{now} run#{prior + 1} predictions {lock['predictions_sha256'][:16]} sealed {lock['sealed_utc']}\n")
    pred = json.load(open(a.pred)); fz = pred["falsifiers"]

    # ---- 1. run the pre-registered rule once, cut at 2018-12-31
    df = load_full(a.full_signal, a.trade or a.full_signal)
    t0 = common_start(df, a.longest)
    rates = cash_series(a.cash); cash = CashModel(rates)
    cash_d = pd.Series([cash.growth(d0, d1) - 1 for d0, d1 in zip(df.index[:-1], df.index[1:])], index=df.index[1:])
    eq_s, w_s = run(df, t0, cash, a.months); eq_b, _ = run(df, t0, cash, 0)
    cut = eq_s.index[eq_s.index < OOS_START][-1]
    def part(eq, lo, hi): e = eq.loc[lo:hi]; return e / e.iloc[0]
    IS = dict(s=part(eq_s, t0, cut), b=part(eq_b, t0, cut)); OOS = dict(s=part(eq_s, cut, None), b=part(eq_b, cut, None))

    def block(e_s, e_b, w):
        rs, rb = e_s.pct_change().dropna(), e_b.pct_change().dropna(); c = cash_d.reindex(rs.index).fillna(0)
        yrs = (e_s.index[-1] - e_s.index[0]).days / 365.25
        return dict(cagr_s=(e_s.iloc[-1]) ** (1 / yrs) - 1, cagr_b=(e_b.iloc[-1]) ** (1 / yrs) - 1,
                    vol_s=rs.std() * math.sqrt(252), vol_b=rb.std() * math.sqrt(252),
                    sharpe_xs_s=ann_sr(rs - c), sharpe_xs_b=ann_sr(rb - c), max_dd_s=max_dd(e_s), max_dd_b=max_dd(e_b),
                    vol_ratio=rs.std() / rb.std(), dd_edge_pp=(max_dd(e_s) - max_dd(e_b)) * 100,
                    round_trips=len(spells(w.reindex(rs.index).shift(1).fillna(0))), years=yrs, time_in_market=float((w.reindex(rs.index) > 0.5).mean()))
    is_m = block(IS["s"], IS["b"], w_s); oos_m = block(OOS["s"], OOS["b"], w_s)

    # ---- 2. falsifiers (pre-registered lines, no rescue)
    fals = {"vol": oos_m["vol_ratio"] <= fz["vol_ratio_max"], "dd": oos_m["dd_edge_pp"] >= fz["dd_edge_min_pp"]}

    # ---- 3. uncertainty on the OOS numbers: stationary bootstrap of paired daily returns
    rs, rb = OOS["s"].pct_change().dropna(), OOS["b"].pct_change().dropna(); c = cash_d.reindex(rs.index).fillna(0).values
    X = np.column_stack([rs.values, rb.values, c]); n = len(rs)
    idx = stationary_idx(n, 20, a.reps, np.random.default_rng(2020))
    def ddv(x): e = np.cumprod(1 + x); return float((e / np.maximum.accumulate(e) - 1).min())
    bv, bd, bsd = [], [], []
    for row in idx:
        s, b, cc = X[row, 0], X[row, 1], X[row, 2]
        bv.append(s.std() / b.std()); bd.append((ddv(s) - ddv(b)) * 100)
        bsd.append(((s - cc).mean() / (s - cc).std() - (b - cc).mean() / (b - cc).std()) * math.sqrt(252))
    q = lambda v: [round(float(np.percentile(v, p)), 3) for p in (5, 50, 95)]
    boot = dict(vol_ratio=q(bv), dd_edge_pp=q(bd), sharpe_diff=q(bsd))

    # ---- 4. PSR / DSR
    xs_oos = rs - cash_d.reindex(rs.index).fillna(0)
    diff = (rs - rb)
    r_is = IS["s"].pct_change().dropna(); xs_is = r_is - cash_d.reindex(r_is.index).fillna(0)
    N, sd = pred["dsr_n_trials"], pred["dsr_trial_sharpe_std_annual"]
    sr_star_d = sd / math.sqrt(252) * expected_max_z(N)
    dsr = dict(n_trials=N, trial_sharpe_std_annual=sd, sr_star_annual=round(sr_star_d * math.sqrt(252), 3),
               dsr_in_sample=round(psr(xs_is, sr_star_d), 3), psr_is_vs_0=round(psr(xs_is, 0.0), 3),
               psr_oos_vs_0=round(psr(xs_oos, 0.0), 3), psr_oos_beats_bh=round(psr(diff, 0.0), 3))

    # ---- 5. grade the sealed predictions
    actual = {"oos_sharpe_xs_strategy": oos_m["sharpe_xs_s"], "oos_sharpe_xs_buyhold": oos_m["sharpe_xs_b"],
              "oos_vol_ratio": oos_m["vol_ratio"], "oos_dd_edge_pp": oos_m["dd_edge_pp"],
              "oos_max_dd_strategy_pct": oos_m["max_dd_s"] * 100, "oos_n_round_trips": oos_m["round_trips"]}
    grades = []
    for k, v in actual.items():
        p = pred[k]; grades.append(dict(metric=k, predicted=p["point"], lo90=p["lo90"], hi90=p["hi90"], actual=round(v, 3),
                                        error=round(v - p["point"], 3), inside_90=bool(p["lo90"] <= v <= p["hi90"])))
    hits = sum(g["inside_90"] for g in grades)
    outcomes = {"p_vol_falsifier_passes": fals["vol"], "p_dd_falsifier_passes": fals["dd"],
                "p_strategy_sharpe_beats_buyhold": oos_m["sharpe_xs_s"] > oos_m["sharpe_xs_b"]}
    brier = {k: round((pred[k] - float(o)) ** 2, 3) for k, o in outcomes.items()}

    # ---- 6. yearly + charts
    ys = (1 + rs).groupby(rs.index.year).prod() - 1; yb = (1 + rb).groupby(rb.index.year).prod() - 1
    yearly = pd.DataFrame({"strategy %": ys * 100, "buy & hold %": yb * 100, "difference pp": (ys - yb) * 100}).round(1)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(eq_s / eq_s.iloc[0], label=f"Faber {a.months}m"); ax.plot(eq_b / eq_b.iloc[0], label="Buy & hold")
    ax.axvline(OOS_START, color="red", ls="--", lw=1); ax.text(OOS_START, ax.get_ylim()[1] * 0.9, " holdout →", color="red", fontsize=8)
    ax.set_yscale("log"); ax.legend(); ax.set_title("In-sample (left of red) and the one-time holdout look (right)")
    fig.tight_layout(); fig.savefig(os.path.join(a.out, "holdout_equity.png"), dpi=130); plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 3))
    for nm, e in [(f"Faber {a.months}m", OOS["s"]), ("Buy & hold", OOS["b"])]: ax.fill_between(e.index, (e / e.cummax() - 1) * 100, 0, alpha=0.4, label=nm)
    ax.legend(); ax.set_title("Holdout drawdowns (%)"); fig.tight_layout(); fig.savefig(os.path.join(a.out, "holdout_drawdown.png"), dpi=130); plt.close(fig)

    # ---- 7. report
    def row(m, k, pct=False): return f"{m[k]*100:.1f}%" if pct else f"{m[k]:.2f}"
    cmp = pd.DataFrame({"In-sample": is_m, "Holdout": oos_m}).T
    view = pd.DataFrame({
        "Period": [f"{t0:%Y-%m-%d} → {cut:%Y-%m-%d}", f"{cut:%Y-%m-%d} → {OOS['s'].index[-1]:%Y-%m-%d}"],
        "CAGR strat / B&H": [f"{m['cagr_s']*100:.1f}% / {m['cagr_b']*100:.1f}%" for m in (is_m, oos_m)],
        "Vol strat / B&H": [f"{m['vol_s']*100:.1f}% / {m['vol_b']*100:.1f}%" for m in (is_m, oos_m)],
        "Sharpe xs strat / B&H": [f"{m['sharpe_xs_s']:.2f} / {m['sharpe_xs_b']:.2f}" for m in (is_m, oos_m)],
        "Max DD strat / B&H": [f"{m['max_dd_s']*100:.1f}% / {m['max_dd_b']*100:.1f}%" for m in (is_m, oos_m)],
        "Vol ratio": [f"{m['vol_ratio']:.2f}" for m in (is_m, oos_m)], "DD edge": [f"{m['dd_edge_pp']:+.1f} pp" for m in (is_m, oos_m)],
        "Round trips": [m["round_trips"] for m in (is_m, oos_m)]}, index=["In-sample", "Holdout"])
    decay = oos_m["sharpe_xs_s"] / is_m["sharpe_xs_s"] if is_m["sharpe_xs_s"] else float("nan")
    L = [f"# Holdout report: Faber {a.months}m overlay (pre-registered)", "",
         f"Run #{prior + 1} of the holdout ({'FIRST LOOK' if prior == 0 else 'RE-RUN: numbers are identical by construction; any rule change is a new strategy'}) · "
         f"predictions sealed {lock['sealed_utc']} · pre-reg sha {lock['prereg_sha256'][:16]}", "",
         "## 1. In-sample vs holdout", "", view.to_markdown(), "",
         f"Sharpe (xs cash) holdout ÷ in-sample: {decay:.2f} (published anomalies keep ~50% OOS: Falck et al.; McLean-Pontiff: −26% OOS)", "",
         "## 2. Pre-registered falsifiers (no rescue, no re-reading)", "",
         f"- Vol ratio ≤ {fz['vol_ratio_max']}: actual {oos_m['vol_ratio']:.2f} → **{'SURVIVES' if fals['vol'] else 'FALSIFIED'}** (bootstrap 5/50/95%: {boot['vol_ratio']})",
         f"- DD edge ≥ {fz['dd_edge_min_pp']} pp: actual {oos_m['dd_edge_pp']:+.1f} → **{'SURVIVES' if fals['dd'] else 'FALSIFIED'}** (bootstrap: {boot['dd_edge_pp']})",
         f"- Sharpe difference vs B&H (no claim made): {oos_m['sharpe_xs_s'] - oos_m['sharpe_xs_b']:+.2f} (bootstrap: {boot['sharpe_diff']})", "",
         "## 3. Probabilistic and Deflated Sharpe", "",
         f"- DSR (in-sample, N = {N}, trial Sharpe std {sd} → SR* = {dsr['sr_star_annual']} annual): **{dsr['dsr_in_sample']}** (need > 0.95 to call the IS Sharpe real)",
         f"- PSR in-sample vs 0: {dsr['psr_is_vs_0']} · PSR holdout vs 0: {dsr['psr_oos_vs_0']} · PSR holdout that it beats B&H: {dsr['psr_oos_beats_bh']}", "",
         "## 4. Your sealed predictions, graded", "", pd.DataFrame(grades).to_markdown(index=False), "",
         f"Inside your 90% intervals: {hits}/{len(grades)} (well calibrated ≈ 5 or 6 of 6; fewer = overconfident)", "",
         f"Brier scores (0 = perfect, 0.25 = coin-flip guessing): {json.dumps(brier)}", "",
         "## 5. Holdout by calendar year", "", yearly.to_markdown(), "", "![](holdout_equity.png)", "", "![](holdout_drawdown.png)", "",
         "## 6. What happens now", "", "- A falsified claim is dead. Don't re-cut dates, swap lookbacks, or 'adjust for COVID'.",
         "- A surviving claim is *not yet refuted*. It isn't proven. It goes into the Day 21 rulebook with this report attached.",
         "- The holdout is now spent. Any new idea needs NEW untouched data (paper trading, Week 4) before it can claim anything."]
    open(os.path.join(a.out, "HOLDOUT_REPORT.md"), "w").write("\n".join(L))
    json.dump(dict(run=prior + 1, in_sample=is_m, holdout=oos_m, falsifiers=fals, bootstrap=boot, dsr=dsr, grades=grades,
                   calibration_hits=hits, brier=brier, yearly=yearly.to_dict(orient="index")),
              open(os.path.join(a.out, "holdout_results.json"), "w"), indent=1, default=float)
    print(view.to_string()); print("falsifiers", fals, "boot", boot); print("dsr", dsr); print(pd.DataFrame(grades).to_string()); print("brier", brier); print(yearly.to_string())

if __name__ == "__main__":
    main()
