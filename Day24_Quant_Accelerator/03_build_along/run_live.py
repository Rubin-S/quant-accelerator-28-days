"""
run_live.py: Day 24. One live PAPER session on the VM. Order of operations is the whole point:

  0. heartbeat /start                          (healthchecks.io notices if this never finishes)
  1. preflight.json exists, is from TODAY, ALL_OK      else: CRIT alert, exit 1, no orders
  2. KILL file?                                        → WARN alert, run reconciliation only, no orders
  3. load state (book + paper broker), RECOVER: reconcile today's broker orders and holdings (recovery.py)
  4. today's bar for NIFTYBEES + NIFTY closes for the signal (price source below)
  5. run_day()  (Day 23: decide/trade, pre-trade checks, fills, EOD limits, journal)
  6. alerts: any halt/kill/violation/mismatch → CRIT; an order or fill → WARN (you WANT to see the first ones); else INFO
  7. save state atomically, heartbeat ok (or /fail)

Price sources:
  --bars CSV        a CSV with Date,Open,High,Low,Close for NIFTYBEES (+ --signal CSV for NIFTY closes). Fine for paper:
                    run in the evening once NSE has published that day's bhavcopy (check the file exists; never assume a time) (Day 13 bhavcopy_ingest.py appends today's row).
  Kite LTP/quote needs the Connect plan (₹500/month). Personal plan → use the bhavcopy route. Paper fills = close mode.

    python run_live.py --bars data/NIFTYBEES.csv --signal data/NIFTY.csv --date 2026-11-23
"""
from __future__ import annotations
import argparse, datetime as dt, json, os, sys
import pandas as pd
from pipeline import PaperBroker, Journal, run_day, new_book, save_state
from recovery import reconcile
from alerts import Alerter, Heartbeat
from risk_engine import load_rulebook, IST

def session(date: str, bars: pd.DataFrame, signal: pd.Series | None, state_path: str, journal_path: str, rb: dict,
            alerter: Alerter, hb: Heartbeat, preflight_path: str, kill_file: str, capital: float, symbol="NIFTYBEES",
            force_target: float | None = None) -> dict:
    hb.start(); j = Journal(journal_path); today = pd.Timestamp(date)
    try:
        pf = json.load(open(preflight_path)) if os.path.exists(preflight_path) else {}
        if not pf.get("ALL_OK") or not str(pf.get("ran_at", "")).startswith(date):
            alerter.send("CRIT", f"{date}: preflight missing/failed/stale → no session"); j.log("abort", date=date, why="preflight"); hb.fail()
            return dict(status="ABORT_PREFLIGHT")
        st = json.load(open(state_path)) if os.path.exists(state_path) else dict(book=new_book(capital), broker=PaperBroker(capital).to_dict())
        book, broker = st["book"], PaperBroker.from_dict(st["broker"])
        book["kill_file"] = kill_file
        book, actions, halt = reconcile(broker.orders_today(symbol), book, symbol, broker.holdings_qty(symbol))
        for a in actions: j.log("recovery", date=date, action=a)
        if halt:
            book["halted"] = book.get("halted") or halt; alerter.send("CRIT", f"{date}: {halt}")
        if today not in bars.index:
            alerter.send("CRIT", f"{date}: no bar for {symbol} (data not published / holiday?) → no session"); hb.fail(); return dict(status="ABORT_DATA")
        if os.path.exists(kill_file): alerter.send("WARN", f"{date}: KILL file present → no orders")
        if force_target is not None:          # PAPER drill only: exercise the order path on a non-decision day
            book["pending_target"] = force_target; j.log("forced_drill", date=date, target=force_target)
            alerter.send("WARN", f"{date}: forced paper drill, target {force_target}")
        n_before = len(broker.orders)
        book = run_day(today, bars.loc[:today], book, broker, rb, j, symbol=symbol, signal_closes=signal)
        new = list(broker.orders.values())[n_before:]
        if book.get("killed"): alerter.send("CRIT", f"{date}: KILLED: {book['killed']}")
        elif book.get("halted"): alerter.send("CRIT", f"{date}: HALTED: {book['halted']}")
        for o in new: alerter.send("WARN", f"{date}: paper {o.side} {o.qty} {symbol} → {o.status} @ {o.avg_price:.2f} {o.reason}")
        alerter.send("INFO", f"{date}: session done, equity {book['equity']:.0f}, qty {book['qty']}")
        save_state(state_path, dict(book=book, broker=broker.to_dict()))
        hb.ok(); return dict(status="OK", halted=book.get("halted", ""), orders=len(new), equity=book["equity"])
    except Exception as e:
        alerter.send("CRIT", f"{date}: session crashed: {e!r}"); j.log("crash", date=date, error=repr(e)); hb.fail(); raise

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", required=True); ap.add_argument("--signal"); ap.add_argument("--date", default=dt.datetime.now(IST).date().isoformat())
    ap.add_argument("--state", default="state.json"); ap.add_argument("--journal", default="journal.jsonl")
    ap.add_argument("--force-target", type=float, help="PAPER ONLY drill: pretend today's pending target is this (0 or 1)")
    ap.add_argument("--preflight", default="preflight.json"); ap.add_argument("--kill-file", default=os.path.expanduser("~/app/KILL"))
    a = ap.parse_args()
    rb, _ = load_rulebook("rulebook.json")
    bars = pd.read_csv(a.bars, parse_dates=["Date"], index_col="Date")
    sig = pd.read_csv(a.signal, parse_dates=["Date"], index_col="Date")["Close"] if a.signal else None
    r = session(a.date, bars, sig, a.state, a.journal, rb, Alerter.from_env(), Heartbeat(os.environ.get("HC_PING_URL")),
                a.preflight, a.kill_file, rb["capital_at_risk_inr"], force_target=a.force_target)
    print(r); sys.exit(0 if r["status"] == "OK" else 1)

if __name__ == "__main__":
    main()
