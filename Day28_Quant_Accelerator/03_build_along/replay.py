"""
replay.py: Day 23. Drive the LIVE pipeline over 2008-09 → 2018-12, one day at a time, with the paper broker.

Test 1 PARITY (mode=close): the pipeline must hold the same position (in/out) as the Day 15 backtest engine on every
       single day. Any mismatch day = a bug in one of them. This is how you know your live code is your tested code.
Test 2 REALISM (mode=limit, orders at 09:30 with a ±limit% cushion off the open): how many orders fill on the first try,
       how many days late the position becomes, and what that does to the result.
Test 3 IDEMPOTENCE: re-running every day a second time sends zero extra orders.

    python replay.py                      # demo on the IS index stand-in
"""
import argparse, copy, json, os
import numpy as np, pandas as pd
from engine import load_frame, DataFeed, Engine, FaberMonthly, VolTargetSizer, CostModel, CashModel
from is_report import GateUntil, common_start, max_dd
from pipeline import PaperBroker, Journal, run_day, new_book
from risk_engine import load_rulebook

HERE = os.path.dirname(os.path.abspath(__file__))

def ohlc(path):
    d = pd.read_csv(path, parse_dates=["Date"], index_col="Date")[["Open", "High", "Low", "Close"]].dropna()
    return d.loc[:"2018-12-31"]

def replay(hist, t0, rb, mode, capital, out_dir, tag, limit_pct, order_time, rerun=False):
    j = Journal(os.path.join(out_dir, f"journal_{tag}.jsonl")); open(j.path, "w").close()
    broker = PaperBroker(capital, mode=mode); book = new_book(capital); held = {}
    for d in hist.index[hist.index >= t0]:
        book["halted"] = ""                                   # replay only: an EOD halt is 'reviewed' overnight (real life: you write the note)
        book = run_day(d, hist.loc[:d], book, broker, rb, j, limit_pct=limit_pct, order_time=order_time)
        if rerun: book = run_day(d, hist.loc[:d], book, broker, rb, j, limit_pct=limit_pct, order_time=order_time)
        held[d] = (book["qty"], book["cash"] + book["qty"] * hist.Close.loc[d])
    s = pd.DataFrame(held, index=["qty", "equity"]).T
    orders = [json.loads(l) for l in open(j.path) if '"kind": "order"' in l]
    unfilled = [json.loads(l) for l in open(j.path) if '"kind": "unfilled"' in l]
    return s, orders, unfilled, j.path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(HERE, "../06_data/NIFTY50_daily_IS_to_2018-12-31.csv"))
    ap.add_argument("--limit-pct", type=float, default=0.25); ap.add_argument("--out", default=os.path.join(HERE, "replay_out"))
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    hist = ohlc(a.data); df = load_frame(a.data, a.data); t0 = common_start(df, 12)
    rb, _ = load_rulebook(os.path.join(HERE, "rulebook.json")); rb = copy.deepcopy(rb)
    capital = 1_000_000                                       # index-level prices: lift the ₹ limits for the replay ONLY
    rb["orders"].update(max_order_value_inr=10 * capital, max_price_deviation_pct=1.0); rb["capital_at_risk_inr"] = capital

    # engine (Day 15) with zero cash interest so cash paths are comparable
    res = Engine(DataFeed(df), GateUntil(FaberMonthly(10), t0), VolTargetSizer(None), CostModel(), CashModel(0.0)).run()
    eng_in = (res.weights.loc[t0:] > 0.5)

    s_close, o_close, _, jp1 = replay(hist, t0, rb, "close", capital, a.out, "close", 0.5, "15:00")
    pipe_in = s_close.qty > 0
    mism = (pipe_in != eng_in.reindex(pipe_in.index)).sum()
    eq_e = res.equity.loc[t0:] / res.equity.loc[t0]; eq_p = s_close.equity / s_close.equity.iloc[0]
    gap_bps = float((eq_p.iloc[-1] / eq_e.iloc[-1] - 1) * 1e4)

    s_lim, o_lim, unf, jp2 = replay(hist, t0, rb, "limit", capital, a.out, "limit", a.limit_pct, "09:30")
    lag = int((s_lim.qty > 0).ne(pipe_in).sum())
    s_pas, o_pas, unf_p, _ = replay(hist, t0, rb, "limit", capital, a.out, "passive", -a.limit_pct, "09:30")
    lag_p = int((s_pas.qty > 0).ne(pipe_in).sum())
    s_rr, o_rr, _, _ = replay(hist, t0, rb, "close", capital, a.out, "rerun", 0.5, "15:00", rerun=True)

    def stats(eq):
        r = eq.pct_change().dropna(); yrs = len(r) / 252
        return dict(CAGR=(eq.iloc[-1] / eq.iloc[0]) ** (1 / yrs) - 1, vol=r.std() * np.sqrt(252), max_dd=max_dd(eq))
    rep = dict(start=str(t0.date()), parity_mismatch_days=int(mism), parity_days=int(len(pipe_in)), orders_close=len(o_close),
               end_equity_gap_vs_engine_bps=round(gap_bps, 1), limit_orders_sent=len(o_lim), limit_unfilled=len(unf),
               limit_first_try_fill_rate=round(1 - len(unf) / max(len(o_lim), 1), 3), limit_days_out_of_sync=lag,
               passive_orders_sent=len(o_pas), passive_unfilled=len(unf_p), passive_days_out_of_sync=lag_p,
               rerun_orders=len(o_rr), rerun_extra_orders=len(o_rr) - len(o_close),
               engine=stats(eq_e), pipeline_close=stats(eq_p), pipeline_limit=stats(s_lim.equity / s_lim.equity.iloc[0]), pipeline_passive=stats(s_pas.equity / s_pas.equity.iloc[0]))
    L = ["# Replay report: live pipeline vs backtest (IS 2008-09 → 2018-12, index stand-in)", "",
         "| Test | Result | Pass? |", "|---|---|---|",
         f"| 1 Parity: days where pipeline in/out ≠ engine | {mism} of {len(pipe_in)} | {'PASS' if mism == 0 else 'FAIL'} |",
         f"| 1 End equity gap vs engine | {gap_bps:+.1f} bps (integer units + fee rounding) | {'PASS' if abs(gap_bps) < 100 else 'CHECK'} |",
         f"| 2 Limit orders at 09:30, ±{a.limit_pct}% off the open | {len(o_lim)} sent, {len(unf)} unfilled → first-try fill rate {rep['limit_first_try_fill_rate']:.0%} | info |",
         f"| 2 Days the marketable-limit book is out of sync with the close-fill book | {lag} | info |",
         f"| 2b PASSIVE limits at 09:30, −{a.limit_pct}% (trying to save the cushion) | {len(o_pas)} sent, {len(unf_p)} unfilled, {lag_p} days out of sync | info |",
         f"| 3 Idempotence: orders when every day runs twice | {len(o_rr)} vs {len(o_close)} | {'PASS' if len(o_rr) == len(o_close) else 'FAIL'} |", "",
         "| Book | CAGR | Vol | Max DD |", "|---|---|---|---|"] + \
        [f"| {k} | {v['CAGR']:.1%} | {v['vol']:.1%} | {v['max_dd']:.1%} |" for k, v in (("Engine (Day 15)", rep["engine"]), ("Pipeline, close fills", rep["pipeline_close"]), ("Pipeline, 09:30 marketable limits", rep["pipeline_limit"]), ("Pipeline, 09:30 passive limits", rep["pipeline_passive"]))] + \
        ["", f"Journals: {os.path.basename(jp1)}, {os.path.basename(jp2)} (append-only JSONL, one line per event)."]
    open(os.path.join(a.out, "replay_report.md"), "w").write("\n".join(L)); json.dump(rep, open(os.path.join(a.out, "replay_results.json"), "w"), indent=1, default=float)
    print("\n".join(L))

if __name__ == "__main__":
    main()
