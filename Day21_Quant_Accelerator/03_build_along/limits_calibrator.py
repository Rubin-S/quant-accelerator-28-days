"""
limits_calibrator.py: Day 21. Are your loss limits SIGNALS or NOISE?

A limit that fires every year while the strategy is working as backtested gets ignored ("oh, it always does that"),
and then it's decoration. A limit that can never fire is decoration too. This tool resamples the strategy's own
IN-SAMPLE daily returns (stationary bootstrap, 20-day blocks) into thousands of 1-year paths and reports how often
each candidate limit would fire WHILE NOTHING IS WRONG. Pick limits that rarely false-fire but still bind.

    python limits_calibrator.py            # uses the IS data in ../06_data
    python limits_calibrator.py --trade <your NIFTYBEES IS csv>
"""
import argparse, json, math, os
import numpy as np, pandas as pd
from engine import load_frame, DataFeed, Engine, FaberMonthly, VolTargetSizer, CostModel, CashModel
from is_report import GateUntil, common_start, cash_series, max_dd, stationary_idx
from risk_engine import kelly_report, triple_penance, load_rulebook

HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--signal", default=os.path.join(HERE, "../06_data/NIFTY50_daily_IS_to_2018-12-31.csv"))
    ap.add_argument("--trade", default=None)
    ap.add_argument("--cash", default=os.path.join(HERE, "../06_data/india_cash_rate_monthly_2007_2018.csv"))
    ap.add_argument("--rulebook", default=os.path.join(HERE, "rulebook.json"))
    ap.add_argument("--sharpe-lo90", type=float, default=-0.32, help="lower 90%% bound of IS Sharpe from your Day 17 report")
    ap.add_argument("--reps", type=int, default=4000)
    ap.add_argument("--out", default=os.path.join(HERE, "limits_out"))
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    rb, rb_hash = load_rulebook(a.rulebook)

    df = load_frame(a.signal, a.trade or a.signal); t0 = common_start(df, 12)
    cash = CashModel(cash_series(a.cash))
    res = Engine(DataFeed(df), GateUntil(FaberMonthly(10), t0), VolTargetSizer(None), CostModel(), cash).run()
    eq = res.equity.loc[t0:]; r = eq.pct_change().dropna().values
    bt_dd = max_dd(eq); vol = r.std() * math.sqrt(252)
    cd = pd.Series([cash.growth(d0, d1) - 1 for d0, d1 in zip(df.index[:-1], df.index[1:])], index=df.index[1:]).reindex(eq.index[1:]).fillna(0).values
    sr = (r - cd).mean() / (r - cd).std() * math.sqrt(252)

    # one-year paths (252 sessions) resampled from the strategy's own history
    idx = stationary_idx(len(r), 20, a.reps, np.random.default_rng(21))[:, :252]
    P = r[idx]                                                        # reps x 252
    worst_day = P.min(1)
    month = P[:, :252 - 252 % 21].reshape(a.reps, -1, 21)
    worst_month = (np.prod(1 + month, axis=2) - 1).min(1)
    eqp = np.cumprod(1 + P, axis=1); dd = (eqp / np.maximum.accumulate(eqp, axis=1) - 1).min(1)

    rows = []
    for L in (3, 4, 5, 6, 8):    rows.append(("daily loss halt", f"{L}%", float((worst_day <= -L / 100).mean())))
    for L in (8, 10, 12, 15, 20): rows.append(("monthly loss halt", f"{L}%", float((worst_month <= -L / 100).mean())))
    for m in (1.0, 1.25, 1.5, 2.0):
        lvl = m * abs(bt_dd); rows.append(("kill drawdown", f"{m}× backtest = {lvl:.0%}", float((dd <= -lvl).mean())))
    tbl = pd.DataFrame(rows, columns=["limit", "level", "P(fires within 1 year | strategy working as backtested)"])
    c = tbl.columns[2]; tbl[c] = [f"{x:.1%}" for x in tbl[c]]

    L_ = rb["loss_limits"]
    yours = dict(daily=float((worst_day <= -L_["daily_loss_halt_pct"] / 100).mean()),
                 monthly=float((worst_month <= -L_["monthly_loss_halt_pct"] / 100).mean()),
                 kill=float((dd <= -L_["kill_drawdown_multiple_of_backtest"] * abs(bt_dd)).mean()))
    kr = kelly_report(sr, a.sharpe_lo90, vol, rb["sizing"]["kelly_fraction_for_report"])
    tp = triple_penance(sr, vol)
    cap = rb["capital_at_risk_inr"]
    loss_at_kill = cap * L_["kill_drawdown_multiple_of_backtest"] * abs(bt_dd)

    L = ["# Limits calibration (in-sample, strategy working as backtested)", "",
         f"Rulebook {rb['version']} sha256 {rb_hash[:16]} · IS Sharpe xs cash {sr:.2f} · vol {vol:.1%} · backtest max DD {bt_dd:.1%} · {a.reps} one-year resampled paths", "",
         "## False-alarm rates of candidate limits", "", tbl.to_markdown(index=False), "",
         f"**Your rulebook's limits:** daily {L_['daily_loss_halt_pct']}% → {yours['daily']:.1%}/yr · monthly {L_['monthly_loss_halt_pct']}% → {yours['monthly']:.1%}/yr · "
         f"kill at {L_['kill_drawdown_multiple_of_backtest']}× backtest DD → {yours['kill']:.1%}/yr", "",
         f"Caveat: a bootstrap can't invent a day worse than the worst in history (strategy's worst day here: {r.min():.1%}). A 0.0% at levels beyond that means 'never seen', not 'impossible'.", "",
         "Rule of thumb: HALT limits may false-fire ~5–15% of years (a halt costs a review, not money). The KILL limit should false-fire well under 5% a year.", "",
         "## Kelly (diagnostic, not the sizing rule)", "",
         f"Full Kelly at the point Sharpe: {kr['full_kelly_point']:.2f}× · half Kelly {kr['frac_kelly_point']:.2f}× · at the lower 90% Sharpe: {kr['full_kelly_lower']:.2f}×", "",
         kr["verdict"], "",
         "## Triple penance (Bailey & López de Prado 2015)", "",
         (f"At SR {sr:.2f} and vol {vol:.1%}: 95%-quantile worst loss ≈ {tp['max_quantile_loss']:.0%}, reached after ≈ {tp['years_to_max_loss']:.0f} years; "
          f"recovery can take ≈ {tp['max_years_under_water']:.0f} years under water." if "note" not in tp else tp["note"]),
         "That's why the retirement rule here is drawdown- and plumbing-based, not time-based: at a low Sharpe, time under water says almost nothing.", "",
         "## What the kill limit means in rupees", "",
         f"Capital at risk ₹{cap:,} → the kill limit fires after about **₹{loss_at_kill:,.0f}** of drawdown. Can you lose that and still follow the rules? If not, lower the capital, not the limit."]
    open(os.path.join(a.out, "limits_report.md"), "w").write("\n".join(L))
    json.dump(dict(sr=sr, vol=vol, backtest_max_dd=bt_dd, yours=yours, kelly=kr, triple_penance=tp, rulebook_sha=rb_hash),
              open(os.path.join(a.out, "limits_results.json"), "w"), indent=1, default=float)
    print("\n".join(L))

if __name__ == "__main__":
    main()
