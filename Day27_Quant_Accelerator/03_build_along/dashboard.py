"""
dashboard.py: Day 25. One static HTML file you can read in 10 seconds. No server, no JS libraries, no internet.

    python dashboard.py --journal journal.jsonl --state state.json --alerts alerts.log --preflight preflight.json \
                        --bars NIFTYBEES.csv --out dashboard.html
    # view it safely: on the VM  `python -m http.server 8080 --bind 127.0.0.1`, on the laptop  `ssh -L 8080:127.0.0.1:8080 trader@<ip>`
    # then open http://127.0.0.1:8080/dashboard.html (no public port, same idea as the Day 22 login tunnel)

Panels, top to bottom, in the order you should look:
  1. STATUS banner: KILLED / HALTED / KILL FILE / STALE / OK, decided by fixed rules (the first match wins)
  2. Risk headroom: daily loss, monthly loss and drawdown, each as % of its limit (the rulebook numbers)
  3. Golden signals: latency (session minutes), traffic (orders), errors (crash/abort/violation/mismatch), saturation (token, disk)
  4. Position + equity vs buy-and-hold since the first session (inline SVG)
  5. Preflight checks today
  6. Alerts (7 days) and the last 25 journal events
Design rule: nothing on this page is a button. It shows; humans act through kill.py and the runbook.
"""
from __future__ import annotations
import argparse, collections, datetime as dt, html, json, os, shutil
import pandas as pd
from session_review import load_jsonl, review
from risk_engine import load_rulebook, IST

def status(state: dict | None, kill_file_exists: bool, last_eod: str | None, today: dt.date) -> tuple[str, str]:
    b = (state or {}).get("book", {})
    if b.get("killed"): return "KILLED", f"retired: {b['killed']}"
    if b.get("halted"): return "HALTED", b["halted"]
    if kill_file_exists: return "KILL FILE", "KILL file present: no orders until cleared with a note"
    if last_eod is None: return "NO DATA", "no session has completed yet"
    lag = (pd.Timestamp(today) - pd.Timestamp(last_eod)).days
    if lag > 4: return "STALE", f"last completed session {last_eod} ({lag} days ago)"   # > a long weekend + a holiday
    return "OK", f"last completed session {last_eod}"

def headroom(state: dict | None, rb: dict, backtest_max_dd: float) -> list[tuple[str, float, float]]:
    """(name, used fraction of the limit, limit) for daily loss, monthly loss and drawdown → kill."""
    if not state: return []
    b = state["book"]; eq = b.get("equity", b["cash"])
    lim = rb["loss_limits"]
    daily = max(0.0, 1 - eq / b["day_start"]) if b.get("day_start") else 0.0
    month = max(0.0, 1 - eq / b["month_start"]) if b.get("month_start") else 0.0
    dd = max(0.0, 1 - eq / b["peak"]) if b.get("peak") else 0.0
    kill_dd = abs(backtest_max_dd) * lim["kill_drawdown_multiple_of_backtest"]
    return [("Daily loss", daily / (lim["daily_loss_halt_pct"] / 100), lim["daily_loss_halt_pct"] / 100),
            ("Monthly loss", month / (lim["monthly_loss_halt_pct"] / 100), lim["monthly_loss_halt_pct"] / 100),
            ("Drawdown → KILL", dd / kill_dd, kill_dd)]

def svg_lines(series: dict[str, pd.Series], w=640, h=180) -> str:
    allv = pd.concat(series.values()); lo, hi = float(allv.min()), float(allv.max()); hi = hi if hi > lo else lo + 1
    idx = sorted(set().union(*[s.index for s in series.values()])); n = max(len(idx) - 1, 1); pos = {d: i for i, d in enumerate(idx)}
    colors = ["#111", "#999"]; out = [f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" role="img">']
    for (name, s), c in zip(series.items(), colors):
        pts = " ".join(f"{pos[d] / n * (w - 10) + 5:.1f},{h - 5 - (v - lo) / (hi - lo) * (h - 20):.1f}" for d, v in s.items())
        out.append(f'<polyline fill="none" stroke="{c}" stroke-width="2" points="{pts}"><title>{html.escape(name)}</title></polyline>')
    out.append(f'<text x="5" y="12" font-size="11">{hi:.3f}</text><text x="5" y="{h - 8}" font-size="11">{lo:.3f}</text></svg>')
    return "".join(out)

def build(journal, state, alerts, preflight, rb, bars: pd.DataFrame | None, kill_file_exists=False, today=None,
          backtest_max_dd=-0.256, disk_path="/", incidents_text: str = "") -> str:
    today = today or dt.datetime.now(IST).date()
    r = review(journal, state, alerts, incidents_text, bars.Close if bars is not None else None)
    eods = [e for e in journal if e["kind"] == "eod"]; last_eod = str(eods[-1]["date"])[:10] if eods else None
    st, why = status(state, kill_file_exists, last_eod, today)
    color = {"OK": "#1b7f3b", "STALE": "#b26a00", "NO DATA": "#b26a00", "KILL FILE": "#b26a00"}.get(st, "#b00020")
    E = html.escape; H = []
    H.append(f'<div class="banner" style="background:{color}"><b>{E(st)}</b> · {E(why)}</div>')
    # headroom
    H.append("<h2>Risk headroom</h2><table>")
    for name, used, limit in headroom(state, rb, backtest_max_dd):
        pct = min(used, 1.0) * 100; c = "#1b7f3b" if used < 0.5 else ("#b26a00" if used < 0.8 else "#b00020")
        H.append(f'<tr><td>{E(name)}</td><td class="bar"><div style="width:{pct:.0f}%;background:{c}"></div></td><td>{used:.0%} of {limit:.1%}</td></tr>')
    H.append("</table>")
    # golden signals
    by_day = collections.defaultdict(list)
    for e in journal: by_day[str(e.get("date", ""))[:10]].append(e)
    last = by_day.get(last_eod, []) if last_eod else []
    def _t(e): return dt.datetime.fromisoformat(e["ts"])
    lat = (max(map(_t, last)) - min(map(_t, last))).total_seconds() / 60 if len(last) > 1 else 0.0
    errs = sum(1 for e in journal if e["kind"] in ("crash", "abort", "mismatch") or (e["kind"] == "pre_trade" and e["violations"]))
    tok = "n/a"
    if os.path.exists(os.path.expanduser("~/.kite/token.json")):
        try: tok = json.load(open(os.path.expanduser("~/.kite/token.json")))["expires_at"]
        except Exception: tok = "unreadable"
    disk = shutil.disk_usage(disk_path); disk_pct = disk.used / disk.total
    H.append("<h2>Golden signals</h2><table>"
             f"<tr><td>Latency</td><td>last session took {lat:.1f} min</td></tr>"
             f"<tr><td>Traffic</td><td>{sum(s['orders'] for s in r['sessions'])} orders in {len(r['sessions'])} sessions (expect ~0–1)</td></tr>"
             f"<tr><td>Errors</td><td>{errs} (crash/abort/mismatch/violation) · contract breaches {len(r['anomalies'])}</td></tr>"
             f"<tr><td>Saturation</td><td>disk {disk_pct:.0%} used · token expires {E(str(tok))}</td></tr></table>")
    # equity vs buy & hold
    if state and eods and bars is not None:
        eq = pd.Series({pd.Timestamp(str(e["date"])[:10]): e["equity"] for e in eods}).sort_index()
        bh = bars.Close.reindex(eq.index).ffill()
        b = state["book"]
        H.append(f"<h2>Position and equity</h2><p>Qty {b['qty']} · cash ₹{b['cash']:,.0f} · equity ₹{eq.iloc[-1]:,.0f} "
                 f"({eq.iloc[-1] / eq.iloc[0] - 1:+.2%} since {eq.index[0].date()}) · B&H {bh.iloc[-1] / bh.iloc[0] - 1:+.2%}</p>")
        H.append(svg_lines({"strategy (black)": eq / eq.iloc[0], "buy & hold (grey)": bh / bh.iloc[0]}))
        H.append("<p class='small'>Paper P&L judges plumbing, not edge. A week is noise: do not react to this line.</p>")
    # preflight
    if preflight:
        H.append(f"<h2>Preflight ({E(str(preflight.get('ran_at', '?')))})</h2><table>")
        for k, v in preflight.items():
            if isinstance(v, dict): H.append(f"<tr><td>{'✅' if v['ok'] else '❌'} {E(k)}</td><td>{E(str(v['detail']))}</td></tr>")
        H.append("</table>")
    # alerts + journal tail
    cut = (pd.Timestamp(today) - pd.Timedelta(days=7)).date().isoformat()
    recent = [a for a in alerts if a["ts"][:10] >= cut]
    H.append(f"<h2>Alerts, last 7 days</h2><p>{dict(collections.Counter(a['level'] for a in recent)) or 'none'}</p><table>")
    for a in recent[-10:]: H.append(f"<tr><td>{E(a['ts'])}</td><td>{E(a['level'])}</td><td>{E(a['text'])}</td></tr>")
    H.append("</table><h2>Journal, last 25 events</h2><table>")
    for e in journal[-25:]:
        extra = {k: v for k, v in e.items() if k not in ("ts", "kind", "date")}
        H.append(f"<tr><td>{E(str(e.get('date', ''))[:10])}</td><td>{E(e['kind'])}</td><td class='small'>{E(json.dumps(extra, default=str)[:160])}</td></tr>")
    H.append("</table>")
    if r["anomalies"]: H.insert(1, "<h2>Contract breaches</h2><ul>" + "".join(f"<li>{E(a)}</li>" for a in r["anomalies"]) + "</ul>")
    css = ("body{font:14px system-ui,sans-serif;max-width:760px;margin:20px auto;padding:0 12px;color:#111}"
           ".banner{color:#fff;padding:14px;border-radius:8px;font-size:18px}h2{font-size:15px;margin:22px 0 6px}"
           "table{border-collapse:collapse;width:100%}td{border-bottom:1px solid #eee;padding:4px 6px;vertical-align:top}"
           ".bar{width:45%}.bar div{height:12px;border-radius:3px}.small{font-size:11px;color:#555}")
    gen = dt.datetime.now(IST).isoformat(timespec="minutes")
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>trader: {E(st)}</title><style>{css}</style></head>"
            f"<body><p class='small'>Generated {gen} · read-only</p>{''.join(H)}</body></html>")

def main():
    ap = argparse.ArgumentParser()
    for k, d in (("journal", "journal.jsonl"), ("state", "state.json"), ("alerts", "alerts.log"), ("preflight", "preflight.json"), ("out", "dashboard.html")):
        ap.add_argument("--" + k, default=d)
    ap.add_argument("--incidents", default="incidents.md")
    ap.add_argument("--bars"); ap.add_argument("--kill-file", default=os.path.expanduser("~/app/KILL"))
    a = ap.parse_args(); rb, _ = load_rulebook("rulebook.json")
    bars = pd.read_csv(a.bars, parse_dates=["Date"], index_col="Date") if a.bars else None
    page = build(load_jsonl(a.journal), json.load(open(a.state)) if os.path.exists(a.state) else None, load_jsonl(a.alerts),
                 json.load(open(a.preflight)) if os.path.exists(a.preflight) else None, rb, bars, os.path.exists(a.kill_file),
                 incidents_text=open(a.incidents).read() if os.path.exists(a.incidents) else "")
    open(a.out, "w").write(page); print("wrote", a.out)

if __name__ == "__main__":
    main()
