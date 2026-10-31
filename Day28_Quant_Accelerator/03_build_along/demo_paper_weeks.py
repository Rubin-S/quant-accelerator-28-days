"""
demo_paper_weeks.py: Day 26 demo. 25 paper sessions (2018-11-26 → 2018-12-31) that INCLUDE a real decision day
(Mon 3 Dec 2018), so the live-vs-backtest diff has something to bite on.

The 'ETF' is NIFTY/100 with a small random premium/discount to its 'NAV' each day (sd 0.15%), so D5 shows what
ETF-vs-index tracking looks like. Paper fills are close ± 5 bps by construction, so D3 slippage ≈ 0 here:
in paper, D3 tests your CODE; only real fills test the MARKET.
"""
import copy, json, os, shutil
import numpy as np, pandas as pd
from alerts import Alerter, Heartbeat
from risk_engine import load_rulebook
import run_live, live_vs_backtest as lvb

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "demo_out")
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT); P = lambda f: os.path.join(OUT, f)
raw = pd.read_csv(os.path.join(HERE, "../06_data/NIFTY50_daily_IS_to_2018-12-31.csv"), parse_dates=["Date"], index_col="Date")
signal = raw["Close"]
rng = np.random.default_rng(26)
prem = pd.Series(rng.normal(0, 0.0015, len(raw)), raw.index)
bars = raw[["Open", "High", "Low", "Close"]].div(100).mul(1 + prem, axis=0)
bars.to_csv(P("demo_ETF_bars.csv")); signal.to_frame("Close").to_csv(P("demo_NIFTY_signal.csv"))
rb, _ = load_rulebook(os.path.join(HERE, "rulebook.json")); rb = copy.deepcopy(rb); rb["market"]["holidays"] = []
al = Alerter(None, None, None, log_path=P("alerts.log"))
for d in bars.loc["2018-11-26":"2018-12-31"].index:
    ds = str(d.date())
    json.dump(dict(ALL_OK=True, ran_at=ds + "T09:20:00+05:30"), open(P("preflight.json"), "w"))
    r = run_live.session(ds, bars, signal, P("state.json"), P("journal.jsonl"), rb, al, Heartbeat(None), P("preflight.json"), P("KILL"), 20000)
    if r.get("orders"): print(ds, r)
res = lvb.diff(lvb.load_journal(P("journal.jsonl")), bars, signal)
md = lvb.to_md(res); open(P("diff_report.md"), "w").write(md); print(md)
