"""
live_vs_backtest.py: Day 26. Did the live (paper) system do what the backtest says it would have done, on the same days?

    python live_vs_backtest.py --journal journal.jsonl --bars NIFTYBEES.csv --signal NIFTY.csv --out diff_report.md

Five diffs, in the order you must check them (a later diff means nothing if an earlier one fails):
  D1 SIGNAL     each live decision vs the rule recomputed on today's FINAL data (revised data or a code drift shows here)
  D2 POSITION   each day: live in/out vs the backtest's in/out (same rule, same t+1 timing)
  D3 FILLS      each fill vs the backtest's assumed fill (that day's close ± 5 bps): slippage vs assumption, in bps
  D4 COSTS      fees charged vs nse_costs model on the same trade value
  D5 RETURN     live return − backtest return, split into: timing/position, ETF-vs-index tracking, slippage, fees, residual

Then a verdict on "slippage within assumption" that is honest about sample size: mean, a t-interval, and how many
fills you'd need before the test could tell 5 bps from 15 bps.
"""
from __future__ import annotations
import argparse, json, math, os
import numpy as np, pandas as pd
from pipeline import faber_signal, is_decision_day
from nse_costs import leg_costs

ASSUMED_SLIP_BPS = 5.0
TOLERANCE_BPS = 5.0          # graduation: mean excess over the assumption must be ≤ 5 bps (i.e. ≤ 10 bps total slippage)

def load_journal(path):
    return [json.loads(l) for l in open(path) if l.strip()]

def backtest_positions(sessions: pd.DatetimeIndex, signal: pd.Series, months=10, start_in: bool | None = None) -> pd.Series:
    """In/out the backtest would hold at each session's close: decide on the first session of a month from closes to the
    previous session, hold from the NEXT session's close (Day 15 timing). start_in = position before the window."""
    held, pending, cur = {}, None, bool(start_in)
    for k, d in enumerate(sessions):
        if pending is not None: cur, pending = pending, None
        prev = sessions[k - 1] if k > 0 else signal.index[signal.index < d][-1]
        if is_decision_day(d, prev):
            s = faber_signal(signal.loc[:prev], months)
            if s is not None: pending = bool(s)
        held[d] = cur
    return pd.Series(held)

def diff(journal: list[dict], bars: pd.DataFrame, signal: pd.Series, months=10, instrument="etf_equity") -> dict:
    eods = {pd.Timestamp(str(e["date"])[:10]): e for e in journal if e["kind"] == "eod"}
    sessions = pd.DatetimeIndex(sorted(eods))
    live_in = pd.Series({d: eods[d]["qty"] > 0 for d in sessions})
    first = sessions[0]
    traded_day1 = any(e["kind"] == "fill" and pd.Timestamp(str(e["date"])[:10]) == first for e in journal)
    start_in = (not live_in.iloc[0]) if traded_day1 else bool(live_in.iloc[0])     # position held BEFORE the window
    bt_in = backtest_positions(sessions, signal, months, start_in=start_in)
    # D1 signal
    d1 = []
    for e in (x for x in journal if x["kind"] == "decision"):
        d = pd.Timestamp(str(e["date"])[:10]); prev = signal.index[signal.index < d][-1]
        recomputed = faber_signal(signal.loc[:prev], months)
        d1.append(dict(date=str(d.date()), live=e["signal"], recomputed=recomputed, match=(e["signal"] == recomputed)))
    # D2 position
    drills = {pd.Timestamp(str(e["date"])[:10]) for e in journal if e["kind"] == "forced_drill"}
    mism = [str(d.date()) for d in sessions if live_in[d] != bt_in[d]]
    explained_by_drill = [m for m in mism if any(pd.Timestamp(m) >= x for x in drills)]
    # D3 + D4 fills and costs
    d3 = []
    for f in (x for x in journal if x["kind"] == "fill"):
        d = pd.Timestamp(str(f["date"])[:10]); buy = f["side"] == "BUY"; close = float(bars.Close.loc[d])
        assumed = close * (1 + ASSUMED_SLIP_BPS / 1e4 if buy else 1 - ASSUMED_SLIP_BPS / 1e4)
        sgn = 1 if buy else -1
        model_fee = leg_costs(f["filled_qty"] * f["avg_price"], "buy" if buy else "sell", "delivery", instrument)["total"]
        d3.append(dict(date=str(d.date()), tag=f["tag"], side=f["side"], qty=f["filled_qty"], fill=f["avg_price"], close=close,
                       slip_vs_close_bps=sgn * (f["avg_price"] / close - 1) * 1e4,
                       excess_vs_assumption_bps=sgn * (f["avg_price"] / assumed - 1) * 1e4,
                       fee=f["fees"], model_fee=model_fee, fee_diff=f["fees"] - model_fee, drill=d in drills))
    # D5 return attribution over the window (per ₹ of starting equity)
    eq = pd.Series({d: eods[d]["equity"] for d in sessions})
    etf_r = bars.Close.reindex(sessions).pct_change().fillna(0.0)
    idx_r = signal.reindex(sessions).pct_change().fillna(0.0)
    expo = pd.Series({d: eods[d]["qty"] * float(bars.Close.loc[d]) / eods[d]["equity"] for d in sessions})   # actual weight held
    w_live = expo.shift(1).fillna(0.0 if start_in is False else expo.iloc[0]); w_bt = bt_in.shift(1).fillna(bt_in.iloc[0]).astype(float)
    live_ret = eq.iloc[-1] / eq.iloc[0] - 1
    bt_ret = float((1 + w_bt * idx_r).prod() - 1)                                 # the backtest trades the INDEX, frictionless here
    timing = float((1 + w_live * idx_r).prod() - 1) - bt_ret                         # in/out on different days + holding < 100% (cash drag)
    tracking = float((1 + w_live * etf_r).prod() - 1) - float((1 + w_live * idx_r).prod() - 1)   # ETF price vs index on held days
    e0 = eq.iloc[0]
    slip = -sum(x["qty"] * x["close"] * x["slip_vs_close_bps"] / 1e4 for x in d3) / e0
    fees = -sum(x["fee"] for x in d3) / e0
    resid = live_ret - (bt_ret + timing + tracking + slip + fees)
    att = dict(live=live_ret, backtest_index=bt_ret, timing_and_sizing=timing, etf_vs_index=tracking, slippage=slip, fees=fees, residual=resid)
    # verdict on slippage (non-drill AND drill fills both count as fills; label them)
    xs = np.array([x["excess_vs_assumption_bps"] for x in d3]); n = len(xs)
    if n >= 2:
        m, s = xs.mean(), xs.std(ddof=1); half = 2.0 * s / math.sqrt(n)   # ~95% (t≈2 for moderate n; wider for tiny n)
        n_needed = math.ceil((2.0 * max(s, 1.0) / TOLERANCE_BPS) ** 2)  # fills until the ~95% half-width shrinks to the tolerance
        verdict = "WITHIN" if m + half <= TOLERANCE_BPS else ("OUTSIDE" if m - half > TOLERANCE_BPS else "UNDECIDED")
    elif n == 1:
        m, s, half, n_needed, verdict = xs[0], float("nan"), float("nan"), None, "UNDECIDED (1 fill)"
    else:
        m = s = half = float("nan"); n_needed, verdict = None, "NO FILLS"
    return dict(sessions=len(sessions), d1=d1, d2_mismatch_days=mism, d2_explained_by_drill=explained_by_drill, d3=d3, d5=att,
                slip=dict(n=n, mean=m, sd=s, half_width=half, n_needed=n_needed, verdict=verdict))

def to_md(r: dict) -> str:
    L = ["# Live vs backtest", "", f"Sessions compared: {r['sessions']}", "", "## D1 Signal"]
    if r["d1"]:
        L += ["| Decision day | Live | Recomputed on final data | Match |", "|---|---|---|---|"]
        L += [f"| {x['date']} | {x['live']} | {x['recomputed']} | {'✅' if x['match'] else '❌ INVESTIGATE (data revision or code drift)'} |" for x in r["d1"]]
    else: L.append("No decision day in the window (expected for 23–27 Nov 2026; the next is Tue 1 Dec).")
    unexpl = [m for m in r["d2_mismatch_days"] if m not in r["d2_explained_by_drill"]]
    L += ["", "## D2 Position", f"Days live ≠ backtest: {len(r['d2_mismatch_days'])} · explained by a labelled drill: {len(r['d2_explained_by_drill'])} · **unexplained: {len(unexpl)}**"]
    if unexpl: L.append("Unexplained days: " + ", ".join(unexpl))
    L += ["", "## D3 Fills and D4 costs"]
    if r["d3"]:
        L += ["| Date | Side | Qty | Fill | Close | Slip vs close (bps) | Excess over 5 bps assumption | Fee ₹ | Model fee ₹ | Drill |", "|---|---|---|---|---|---|---|---|---|---|"]
        L += [f"| {x['date']} | {x['side']} | {x['qty']} | {x['fill']:.2f} | {x['close']:.2f} | {x['slip_vs_close_bps']:+.1f} | {x['excess_vs_assumption_bps']:+.1f} | {x['fee']:.2f} | {x['model_fee']:.2f} | {'yes' if x['drill'] else ''} |" for x in r["d3"]]
    else: L.append("No fills.")
    s = r["slip"]
    L += ["", f"**Slippage verdict (graduation test: mean excess over the 5 bps assumption ≤ 5 bps, upper 95% bound): {s['verdict']}**  n = {s['n']}"
          + (f", mean excess {s['mean']:+.1f} bps ± {s['half_width']:.1f}" if s["n"] >= 2 else "")
          + (f"; fills needed to decide ≈ {s['n_needed']}" if s.get("n_needed") else "")]
    a = r["d5"]
    L += ["", "## D5 Return attribution (fractions of starting equity)", "| Piece | Value |", "|---|---|"]
    L += [f"| {k} | {v:+.3%} |" for k, v in a.items()]
    L += ["", "Read it as: live = backtest(index) + timing + ETF-vs-index + slippage + fees + residual. A residual bigger than a few bps means the books don't add up: find it before Day 28."]
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--journal", default="journal.jsonl"); ap.add_argument("--bars", required=True); ap.add_argument("--signal", required=True)
    ap.add_argument("--out", default="diff_report.md")
    a = ap.parse_args()
    bars = pd.read_csv(a.bars, parse_dates=["Date"], index_col="Date"); sig = pd.read_csv(a.signal, parse_dates=["Date"], index_col="Date")["Close"]
    md = to_md(diff(load_journal(a.journal), bars, sig)); open(a.out, "w").write(md); print(md)

if __name__ == "__main__":
    main()
