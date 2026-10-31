"""
session_review.py: Day 25. Read the journal like an auditor, not like a hopeful owner.

    python session_review.py --journal journal.jsonl --state state.json --alerts alerts.log --out review.md

For every session date in the journal it checks the CONTRACT each session must satisfy, then lists anomalies:
  C1 every session ends with exactly one `eod` line              (missing = crash or abort; two = idempotence bug)
  C2 no `crash` lines                                            (any = a bug to fix with a failing-first test)
  C3 every `order` has a matching `fill` or `unfilled` the same day
  C4 every `pre_trade` with violations → no `order` for that tag   (a guard that logs but doesn't block is decoration)
  C5 no `mismatch`, no foreign-order halt                          (or, if present, an incident file exists)
  C6 book in state.json == broker in state.json                   (paper: both live in the state file)
  C7 every CRIT alert has an incident note in incidents.md        (CRIT without a note = ignored alarm)
  C8 orders only on decision days (+1) or a logged forced drill

It also measures the order path when there was one: implementation shortfall vs the decision-day close (bps),
fill vs limit, fees.
"""
from __future__ import annotations
import argparse, collections, json, os, re
import pandas as pd

def load_jsonl(path):
    return [json.loads(l) for l in open(path) if l.strip()] if path and os.path.exists(path) else []

def review(journal: list[dict], state: dict | None, alerts: list[dict], incidents_text: str = "", closes: pd.Series | None = None) -> dict:
    by_day = collections.defaultdict(list)
    for e in journal:
        d = str(e.get("date", ""))[:10]
        if d: by_day[d].append(e)
    sessions, anomalies, shortfalls = [], [], []
    decisions = {}
    for d in sorted(by_day):
        ev = by_day[d]; kinds = collections.Counter(e["kind"] for e in ev); prob = []
        if kinds["abort"]: prob.append(f"aborted: {[e.get('why') for e in ev if e['kind']=='abort']}")
        elif kinds["eod"] != 1: prob.append(f"C1: {kinds['eod']} eod lines (want 1)")
        if kinds["crash"]: prob.append(f"C2: crash {[e.get('error') for e in ev if e['kind']=='crash']}")
        orders = [e for e in ev if e["kind"] == "order"]; outcomes = {e["tag"] for e in ev if e["kind"] in ("fill", "unfilled")}
        for o in orders:
            if o["status"] == "OPEN" and o["tag"] not in outcomes: prob.append(f"C3: order {o['tag']} has no fill/unfilled line")
        blocked = {e["order"]["tag"] for e in ev if e["kind"] == "pre_trade" and e["violations"]}
        for o in orders:
            if o["tag"] in blocked: prob.append(f"C4: order {o['tag']} sent despite violations")
        if kinds["mismatch"]: prob.append("C5: position mismatch")
        for e in ev:
            if e["kind"] == "decision": decisions[d] = e
        drill = kinds["forced_drill"] > 0
        prev_dec = [x for x in decisions if x < d]
        if orders and not drill and not prev_dec: prob.append("C8: order with no prior decision and no forced drill")
        for f in (e for e in ev if e["kind"] == "fill"):
            ref_day = max(prev_dec) if prev_dec else None
            if drill and closes is not None:           # a drill has no decision: measure against the previous session's close
                before = closes.index[closes.index < pd.Timestamp(d)]; ref_day = str(before[-1].date()) if len(before) else None
            if closes is not None and ref_day and pd.Timestamp(ref_day) in closes.index:
                ref = float(closes.loc[pd.Timestamp(ref_day)]); sgn = 1 if f["side"] == "BUY" else -1
                shortfalls.append(dict(date=d, tag=f["tag"], side=f["side"], fill=f["avg_price"], decision_close=ref,
                                       shortfall_bps=round(sgn * (f["avg_price"] / ref - 1) * 1e4, 1), fees=round(f["fees"], 2),
                                       vs_limit_bps=round(sgn * (f["avg_price"] / f["limit_price"] - 1) * 1e4, 1)))
        eod = [e for e in ev if e["kind"] == "eod"]
        explained = d in incidents_text                  # an incident note for that date turns a breach into a documented event
        sessions.append(dict(date=d, events=len(ev), orders=len(orders), drill=drill, halted=(eod[-1]["halted"] if eod else ""),
                             equity=(eod[-1]["equity"] if eod else None), problems=[p + (" (explained in incidents.md)" if explained else "") for p in prob]))
        anomalies += [] if explained else [f"{d}: {p}" for p in prob]
    if state:
        b, k = state["book"], state["broker"]
        if b["qty"] != k["qty"] or abs(b["cash"] - k["cash"]) > 0.01: anomalies.append(f"C6: state book qty {b['qty']} cash {b['cash']:.2f} ≠ broker qty {k['qty']} cash {k['cash']:.2f}")
    crit = [a for a in alerts if a.get("level") == "CRIT"]
    def _day(a):                                         # alerts carry the SESSION date in their text; fall back to the send time
        m = re.search(r"\d{4}-\d{2}-\d{2}", a["text"]); return m.group(0) if m else a["ts"][:10]
    unexplained = [a for a in crit if _day(a) not in incidents_text]
    for a in unexplained: anomalies.append(f"C7: CRIT alert with no incident note: {a['text'][:80]}")
    return dict(sessions=sessions, anomalies=anomalies, shortfalls=shortfalls,
                alert_counts=dict(collections.Counter(a.get("level") for a in alerts)), n_crit_unexplained=len(unexplained))

def to_markdown(r: dict) -> str:
    L = ["# Session review", "", f"**Contract breaches: {len(r['anomalies'])}**" + ("  (clean)" if not r["anomalies"] else ""), ""]
    L += ["| Date | Events | Orders | Drill | Halted | Equity | Problems |", "|---|---|---|---|---|---|---|"]
    for s in r["sessions"]:
        eq = "" if s["equity"] is None else f"{s['equity']:,.0f}"
        L.append(f"| {s['date']} | {s['events']} | {s['orders']} | {'yes' if s['drill'] else ''} | {s['halted'] or ''} | {eq} | {'; '.join(s['problems'])} |")
    if r["anomalies"]: L += ["", "## Anomalies (each one → bugs.md with a failing-first test, or incidents.md)"] + [f"- {a}" for a in r["anomalies"]]
    if r["shortfalls"]:
        L += ["", "## Order path quality", "| Date | Tag | Side | Fill | Decision close | Shortfall (bps) | vs limit (bps) | Fees ₹ |", "|---|---|---|---|---|---|---|---|"]
        L += [f"| {x['date']} | {x['tag']} | {x['side']} | {x['fill']:.2f} | {x['decision_close']:.2f} | {x['shortfall_bps']:+.1f} | {x['vs_limit_bps']:+.1f} | {x['fees']:.2f} |" for x in r["shortfalls"]]
        L += ["", "Shortfall > 0 = you paid more (buy) / got less (sell) than the decision-day close. Over 1 trade it's noise; it's a number to track, not to react to."]
    L += ["", f"Alerts by level: {r['alert_counts']}"]
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--journal", default="journal.jsonl"); ap.add_argument("--state", default="state.json")
    ap.add_argument("--alerts", default="alerts.log"); ap.add_argument("--incidents", default="incidents.md")
    ap.add_argument("--bars"); ap.add_argument("--out", default="review.md")
    a = ap.parse_args()
    closes = pd.read_csv(a.bars, parse_dates=["Date"], index_col="Date")["Close"] if a.bars else None
    r = review(load_jsonl(a.journal), json.load(open(a.state)) if os.path.exists(a.state) else None, load_jsonl(a.alerts),
               open(a.incidents).read() if os.path.exists(a.incidents) else "", closes)
    open(a.out, "w").write(to_markdown(r)); print(to_markdown(r))

if __name__ == "__main__":
    main()
