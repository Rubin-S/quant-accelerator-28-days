"""
demo_week.py: Day 25. Builds a realistic demo of 'Week 4 so far' so you can see the review + dashboard before your own data exists.

Uses the IS index file as a stand-in for NIFTYBEES (prices scaled by 1/40 to look like an ETF) over its last 9 sessions,
runs run_live.session() each day, and plants three real-world events:
  day 3: a forced paper drill (target 1.0) → one order + fill
  day 5: preflight missing → abort + CRIT
  day 7: someone 'trades in the Kite app' (+5 units at the broker) → mismatch HALT + CRIT
Then writes review.md and dashboard.html into demo_out/. Your job tomorrow: replace this with YOUR session logs.
"""
import copy, json, os, shutil
import pandas as pd
from alerts import Alerter, Heartbeat
from risk_engine import load_rulebook
import run_live, session_review, dashboard

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "demo_out")
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
raw = pd.read_csv(os.path.join(HERE, "../06_data/NIFTY50_daily_IS_to_2018-12-31.csv"), parse_dates=["Date"], index_col="Date")
bars = (raw[["Open", "High", "Low", "Close"]] / 40).dropna(); signal = raw["Close"]
rb, _ = load_rulebook(os.path.join(HERE, "rulebook.json")); rb = copy.deepcopy(rb); rb["market"]["holidays"] = []
P = lambda f: os.path.join(OUT, f)
al = Alerter(None, None, None, log_path=P("alerts.log")); hb = Heartbeat(None)
days = bars.index[-9:]
for k, d in enumerate(days, 1):
    ds = str(d.date())
    if k != 5: json.dump(dict(ALL_OK=True, ran_at=ds + "T09:20:00+05:30", egress_ip=dict(ok=True, detail="egress = whitelisted"),
                             token=dict(ok=True, detail="valid until next 06:00"), funds=dict(ok=True, detail="cash ≥ capital")), open(P("preflight.json"), "w"))
    elif os.path.exists(P("preflight.json")): os.remove(P("preflight.json"))
    if k == 7:
        st = json.load(open(P("state.json"))); st["broker"]["qty"] += 5; json.dump(st, open(P("state.json"), "w"))
    if k == 8:   # the human writes the incident note and clears the halt, as the runbook says
        st = json.load(open(P("state.json"))); st["broker"]["qty"] -= 5; st["book"]["halted"] = ""; json.dump(st, open(P("state.json"), "w"))
        open(P("incidents.md"), "a").write(f"\n## {days[6].date()} mismatch HALT\nDrill: +5 units planted at the paper broker to mimic a manual Kite trade. Reversed, reconciled, cleared.\n"
                                          f"\n## {days[4].date()} preflight missing\nDrill: preflight.json deleted on purpose. Session aborted as designed.\n")
    r = run_live.session(ds, bars, signal, P("state.json"), P("journal.jsonl"), rb, al, hb, P("preflight.json"), P("KILL"), 20000,
                         force_target=1.0 if k == 3 else None)
    print(ds, r)
rev = session_review.review(session_review.load_jsonl(P("journal.jsonl")), json.load(open(P("state.json"))), session_review.load_jsonl(P("alerts.log")),
                            open(P("incidents.md")).read(), bars.Close)
open(P("review.md"), "w").write(session_review.to_markdown(rev))
page = dashboard.build(session_review.load_jsonl(P("journal.jsonl")), json.load(open(P("state.json"))), session_review.load_jsonl(P("alerts.log")),
                       json.load(open(P("preflight.json"))), rb, bars, False, today=days[-1].date(),
                       incidents_text=open(P("incidents.md")).read())
open(P("dashboard.html"), "w").write(page)
print(session_review.to_markdown(rev))
