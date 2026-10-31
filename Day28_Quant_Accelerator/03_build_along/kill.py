"""
kill.py: Day 24. The big red button, three layers deep.

  python kill.py halt "reason"     Layer 1: write the KILL file (risk_engine refuses every order while it exists),
                                   cancel our OPEN orders, CRIT alert. Position is KEPT (Day 21 ruling: HALT ≠ liquidate).
  python kill.py kill "reason"     Layer 2: halt + sell the whole position with a marketable LIMIT (−1% off LTP, the
                                   rulebook band). Only for the KILL conditions in the rulebook (1.5× backtest DD, broken plumbing).
  python kill.py status
  python kill.py clear --note "…"  Only a human, only with a written note (≥ 20 chars) appended to incidents.md.

  Layer 3 (manual, outside your code): Zerodha Console → Kill switch disables a segment; re-enabling is possible only
  after 12 hours, and Zerodha asks you to have no open orders or positions first. So it's a lock for the door, not a
  fire extinguisher: use layers 1–2 first. (support.zerodha.com/…/what-is-the-kill-switch)
"""
from __future__ import annotations
import datetime as dt, os, sys

def write_kill(path: str, reason: str):
    with open(path, "w") as f: f.write(f"{dt.datetime.now().isoformat(timespec='seconds')} {reason}\n")

def cancel_ours(kite, symbol: str, prefix: str = "F10") -> list[str]:
    done = []
    for o in kite.orders():
        if o["tradingsymbol"] == symbol and (o.get("tag") or "").startswith(prefix) and o["status"] not in ("COMPLETE", "REJECTED", "CANCELLED"):
            kite.cancel_order(variety=o.get("variety", "regular"), order_id=o["order_id"]); done.append(o["order_id"])
    return done

def flatten(kite, symbol: str, qty: int, ltp: float, tag: str) -> str | None:
    if qty <= 0: return None
    return kite.place_order(variety="regular", exchange="NSE", tradingsymbol=symbol, transaction_type="SELL", quantity=qty,
                            product="CNC", order_type="LIMIT", price=round(ltp * 0.99, 2), validity="DAY", tag=tag)

def clear(path: str, note: str, incidents: str = "incidents.md") -> bool:
    if len(note.strip()) < 20: raise ValueError("write a real note (≥ 20 chars): what happened, why it's safe now")
    with open(incidents, "a") as f: f.write(f"\n## {dt.datetime.now().isoformat(timespec='minutes')} CLEARED\n{note.strip()}\n")
    if os.path.exists(path): os.remove(path)
    return True

def main():
    kill_file = os.environ.get("KILL_FILE", os.path.expanduser("~/app/KILL"))
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        print(open(kill_file).read() if os.path.exists(kill_file) else "no KILL file: trading allowed if preflight passes"); return
    if cmd == "clear":
        clear(kill_file, sys.argv[sys.argv.index("--note") + 1]); print("cleared"); return
    reason = sys.argv[2] if len(sys.argv) > 2 else "manual"
    write_kill(kill_file, f"{cmd.upper()}: {reason}")
    from alerts import Alerter; a = Alerter.from_env()
    try:
        from kiteconnect import KiteConnect; from kite_session import load_token
        k = KiteConnect(api_key=os.environ["KITE_API_KEY"]); k.set_access_token(load_token()["access_token"])
        c = cancel_ours(k, "NIFTYBEES"); msg = f"{cmd.upper()} {reason}: cancelled {c}"
        if cmd == "kill":
            q = sum(h["quantity"] + h.get("t1_quantity", 0) for h in k.holdings() if h["tradingsymbol"] == "NIFTYBEES")
            ltp = k.ltp(["NSE:NIFTYBEES"])["NSE:NIFTYBEES"]["last_price"]            # needs the Connect plan
            msg += f", flatten order {flatten(k, 'NIFTYBEES', q, ltp, 'KILL' + dt.date.today().strftime('%y%m%d'))}"
    except Exception as e:
        msg = f"{cmd.upper()} {reason}: KILL file written, broker step FAILED ({e!r}). Use Kite app now."
    a.send("CRIT", msg); print(msg)

if __name__ == "__main__":
    main()
