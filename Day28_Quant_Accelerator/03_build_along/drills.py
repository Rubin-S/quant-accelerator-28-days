"""
drills.py: Day 27. Break the system on purpose, in a sandbox, and check it fails SAFE.

    python drills.py                 # runs every drill in a temp folder → drills_report.md

Each drill follows the chaos-engineering recipe (principlesofchaos.org):
  STEADY STATE  what "safe" means here: no order we can't explain, book == broker, a human is told
  HYPOTHESIS    what the system SHOULD do when this fault hits
  INJECT        the fault (a fake broker, a missing file, an exception at the worst moment)
  OBSERVE       orders sent, position, halt flag, alerts, journal
  VERDICT       PASS = safe AND loud.  SAFE-BUT-ACCIDENTAL = safe for the wrong reason (a finding!).  FAIL = unsafe or silent.

Nothing here touches a real broker. Kite-shaped fakes stand in for kiteconnect, so kill.py's real functions run.
The same drills must ALSO be done once by hand on the VM (04_templates/game_day_runbook.md): code drills test
logic; game days test you, your phone and your runbook.
"""
from __future__ import annotations
import builtins, copy, json, os, shutil, tempfile, dataclasses as dc
import pandas as pd
import pipeline, run_live, kill
from pipeline import PaperBroker, Journal, run_day, new_book, save_state
from recovery import reconcile
from alerts import Alerter, Heartbeat
from risk_engine import load_rulebook

HERE = os.path.dirname(os.path.abspath(__file__))
SYM = "NIFTYBEES"; CAPITAL = 20000.0
TRADE_DAY = "2018-12-04"          # demo: decision on Mon 3 Dec 2018, order on Tue 4 Dec

def load_data():
    raw = pd.read_csv(os.path.join(HERE, "../06_data/NIFTY50_daily_IS_to_2018-12-31.csv"), parse_dates=["Date"], index_col="Date")
    return raw[["Open", "High", "Low", "Close"]] / 100, raw["Close"]

# ---------------------------------------------------------------- fakes
class FlakyBroker(PaperBroker):
    """fail = None | 'before_send' (request never left) | 'after_send' (exchange got it, our response was lost)
              | 'reject' (broker says no) | 'token' (session expired on the holdings call)"""
    def __init__(self, *a, fail=None, **kw):
        super().__init__(*a, **kw); self.fail = fail; self.sent = 0
    def place(self, o, market_protection=None):
        if self.fail == "before_send": raise ConnectionError("NetworkException: OMS unreachable (502)")
        bo = super().place(o, market_protection); self.sent += 1
        if self.fail == "reject": bo.status, bo.reason = "REJECTED", "MarginException: insufficient funds (drill)"
        if self.fail == "after_send": raise ConnectionError("NetworkException: gateway timeout (504) after send")
        return bo
    def holdings_qty(self, symbol):
        if self.fail == "token": raise PermissionError("TokenException 403: session expired, re-login")
        return super().holdings_qty(symbol)

class FakeKite:
    """Just enough of kiteconnect for kill.py: orders(), cancel_order(), place_order()."""
    def __init__(self, orders): self._orders = orders; self.cancelled, self.placed = [], []
    def orders(self): return self._orders
    def cancel_order(self, variety, order_id): self.cancelled.append(order_id)
    def place_order(self, **kw): self.placed.append(kw); return "KILL0001"

# ---------------------------------------------------------------- a restartable mini-session (same steps as run_live.session)
class Ctx:
    def __init__(self, root):
        self.root = root; self.state = os.path.join(root, "state.json"); self.journal = os.path.join(root, "journal.jsonl")
        self.kill = os.path.join(root, "KILL"); self.alerts = Alerter(None, None, None, log_path=os.path.join(root, "alerts.log"))
        rb, _ = load_rulebook(os.path.join(HERE, "rulebook.json")); self.rb = copy.deepcopy(rb); self.rb["market"]["holidays"] = []
    def book(self):
        if os.path.exists(self.state): return json.load(open(self.state))["book"]
        b = new_book(CAPITAL); return b
    def alerts_text(self): return open(self.alerts.log_path).read() if os.path.exists(self.alerts.log_path) else ""
    def journal_kinds(self): return [json.loads(l)["kind"] for l in open(self.journal)] if os.path.exists(self.journal) else []

def mini_session(ctx: Ctx, date: str, bars, signal, broker):
    """Restart-safe: book from disk, broker is 'the exchange' (persists across our crashes)."""
    j = Journal(ctx.journal); today = pd.Timestamp(date)
    try:
        book = ctx.book(); book["kill_file"] = ctx.kill
        book, actions, halt = reconcile(broker.orders_today(SYM), book, SYM, broker.holdings_qty(SYM))
        for a in actions: j.log("recovery", date=date, action=a)
        if halt: book["halted"] = book.get("halted") or halt; ctx.alerts.send("CRIT", f"{date}: {halt}")
        book = run_day(today, bars.loc[:today], book, broker, ctx.rb, j, symbol=SYM, signal_closes=signal)
        if book.get("halted"): ctx.alerts.send("CRIT", f"{date}: HALTED: {book['halted']}")
        save_state(ctx.state, dict(book=book)); return "OK"
    except Exception as e:
        ctx.alerts.send("CRIT", f"{date}: session crashed: {e!r}"); j.log("crash", date=date, error=repr(e)); return "CRASH"

# ---------------------------------------------------------------- the drills
@dc.dataclass
class Result:
    name: str; hypothesis: str; observed: str; verdict: str; lesson: str = ""

DECISION_DAY = "2018-12-03"
def setup(ctx, bars, signal, broker):
    """Run the real decision day so tomorrow's order comes from the rule, not from us."""
    assert mini_session(ctx, DECISION_DAY, bars, signal, broker) == "OK" and ctx.book()["pending_target"] == 1.0

def _ok(cond_safe, cond_loud): return "PASS" if (cond_safe and cond_loud) else "FAIL"

def d01_kill_file(bars, signal, root):
    c = Ctx(root); open(c.kill, "w").write("HALT: drill\n")
    b = FlakyBroker(CAPITAL); fl = b.fail; b.fail = None; setup(c, bars, signal, b); b.fail = fl; r = mini_session(c, TRADE_DAY, bars, signal, b)
    bk = c.book(); safe = b.sent == 0 and bk["qty"] == 0; loud = "CRIT" in c.alerts_text()
    return Result("D01 KILL file on a trade day", "no order leaves; position kept; CRIT alert",
                  f"orders sent {b.sent}, halted={bk['halted'][:60]!r}", _ok(safe, loud),
                  "The file is checked inside pre_trade_check, so every order path obeys it.")

def d02_kill_cancels_only_ours(*_):
    k = FakeKite([dict(order_id="1", tradingsymbol=SYM, tag="F10261126B0", status="OPEN"),
                  dict(order_id="2", tradingsymbol=SYM, tag="", status="OPEN"),
                  dict(order_id="3", tradingsymbol=SYM, tag="F10261125B0", status="COMPLETE"),
                  dict(order_id="4", tradingsymbol="GOLDBEES", tag="F10261126B0", status="OPEN")])
    done = kill.cancel_ours(k, SYM)
    return Result("D02 kill.py halt cancels only OUR open orders", "cancel #1 only (not manual #2, not done #3, not other symbol #4)",
                  f"cancelled {done}", "PASS" if done == ["1"] else "FAIL",
                  "A kill switch that cancels other people's orders is its own incident.")

def d03_kill_flatten(*_):
    k = FakeKite([]); oid = kill.flatten(k, SYM, 70, 262.89, "KILL261126")
    p = k.placed[0] if k.placed else {}
    ok = p.get("order_type") == "LIMIT" and p.get("transaction_type") == "SELL" and p.get("quantity") == 70 and abs(p.get("price", 0) - 260.26) < 0.01 and p.get("product") == "CNC"
    none = kill.flatten(FakeKite([]), SYM, 0, 262.89, "KILL261126") is None
    return Result("D03 kill.py kill flattens with a marketable LIMIT", "SELL 70 CNC LIMIT at LTP −1% (₹260.26); qty 0 → nothing",
                  f"placed {p.get('transaction_type')} {p.get('quantity')} {p.get('order_type')} @ {p.get('price')}; qty-0 call → {'nothing' if none else 'ORDER!'}",
                  "PASS" if ok and none else "FAIL", "Never MARKET (Day 22: API market orders need market_protection).")

def d04_lost_before_send(bars, signal, root):
    c = Ctx(root); b = FlakyBroker(CAPITAL, fail="before_send"); fl = b.fail; b.fail = None; setup(c, bars, signal, b); b.fail = fl
    r1 = mini_session(c, TRADE_DAY, bars, signal, b)
    b.fail = None; r2 = mini_session(c, TRADE_DAY, bars, signal, b)          # network back, same day, restart
    bk = c.book(); safe = len(b.orders) == 1 and bk["qty"] == b.qty; loud = "crashed" in c.alerts_text()
    return Result("D04 Connection lost BEFORE the order left", "crash + CRIT; restart sends exactly one order; book = broker",
                  f"run1 {r1}, run2 {r2}; broker orders {len(b.orders)}; book {bk['qty']} vs broker {b.qty}", _ok(safe, loud),
                  "State is saved only at the end, so a crash leaves the old state: the retry is clean.")

def d05_lost_after_send(bars, signal, root):
    """The dangerous one: the exchange HAS the order, we don't know. Knight-class risk: a blind retry doubles you."""
    c = Ctx(root); b = FlakyBroker(CAPITAL, fail="after_send"); fl = b.fail; b.fail = None; setup(c, bars, signal, b); b.fail = fl
    r1 = mini_session(c, TRADE_DAY, bars, signal, b)
    b.fail = None; r2 = mini_session(c, TRADE_DAY, bars, signal, b)          # we restart before the close
    for o in b.on_bar(bars.loc[TRADE_DAY]): pass                              # the exchange fills the open order at the close
    nxt = str(bars.index[bars.index.get_loc(pd.Timestamp(TRADE_DAY)) + 1].date())
    r3 = mini_session(c, nxt, bars, signal, b)                                # next morning: recovery applies the missed fill
    bk = c.book(); n_orders = len(b.orders); halted = bk.get("halted", "")
    safe = n_orders == 1 and bk["qty"] == b.qty
    why = "duplicate order tag" in open(c.journal).read()
    verdict = "SAFE-BUT-ACCIDENTAL" if (safe and why) else _ok(safe, "crashed" in c.alerts_text())
    return Result("D05 Connection lost AFTER the order left", "restart must NOT resend while our order is OPEN; next day book = broker",
                  f"runs {r1}/{r2}/{r3}; broker orders {n_orders}; book {bk['qty']} vs broker {b.qty}; halted={halted[:50]!r}",
                  verdict,
                  "No second order went out, but only because the duplicate-tag guard fired and HALTED. run_day doesn't read "
                  "book['open_order_id'] that recovery sets. Today's bug: failing-first test, then skip sending while an order is OPEN.")

def d06_rejected(bars, signal, root):
    c = Ctx(root); b = FlakyBroker(CAPITAL, fail="reject"); fl = b.fail; b.fail = None; setup(c, bars, signal, b); b.fail = fl
    i0 = bars.index.get_loc(pd.Timestamp(TRADE_DAY)); days = [str(d.date()) for d in bars.index[i0:i0 + 4]]
    mini_session(c, days[0], bars, signal, b)
    for d in days[1:]: mini_session(c, d, bars, signal, b)
    bk = c.book(); tags = [o.tag for o in b.orders.values()]
    safe = bk["qty"] == 0 == b.qty and len(set(tags)) == len(tags) and len(tags) == 3 and "3 unfilled" in (bk.get("halted") or "")
    return Result("D06 Broker rejects the order (margin)", "book unchanged; retry next day with a NEW tag; 3 failures → HALT + CRIT",
                  f"orders {tags}; qty book {bk['qty']} / broker {b.qty}; halted={bk.get('halted','')!r}", _ok(safe, "CRIT" in c.alerts_text()),
                  "A rejection is information, not noise: read status_message, never auto-resize and resend the same day.")

def d07_no_data(bars, signal, root):
    c = Ctx(root); json.dump(dict(ALL_OK=True, ran_at=TRADE_DAY + "T09:20:00+05:30"), open(os.path.join(root, "pf.json"), "w"))
    r = run_live.session(TRADE_DAY, bars.drop(pd.Timestamp(TRADE_DAY)), signal, c.state, c.journal, c.rb, c.alerts, Heartbeat(None),
                         os.path.join(root, "pf.json"), c.kill, CAPITAL)
    return Result("D07 Today's price file missing", "ABORT_DATA, CRIT, no orders, no state change",
                  f"status {r['status']}; state written: {os.path.exists(c.state)}", _ok(r["status"] == "ABORT_DATA" and not os.path.exists(c.state), "CRIT" in c.alerts_text()))

def d08_stale_preflight(bars, signal, root):
    c = Ctx(root); json.dump(dict(ALL_OK=True, ran_at="2018-12-03T09:20:00+05:30"), open(os.path.join(root, "pf.json"), "w"))
    r = run_live.session(TRADE_DAY, bars, signal, c.state, c.journal, c.rb, c.alerts, Heartbeat(None), os.path.join(root, "pf.json"), c.kill, CAPITAL)
    return Result("D08 Yesterday's preflight (stale)", "ABORT_PREFLIGHT, CRIT", f"status {r['status']}", _ok(r["status"] == "ABORT_PREFLIGHT", "CRIT" in c.alerts_text()))

def d09_token_expired(bars, signal, root):
    c = Ctx(root); b = FlakyBroker(CAPITAL, fail="token"); fl = b.fail; b.fail = None; setup(c, bars, signal, b); b.fail = fl; r = mini_session(c, TRADE_DAY, bars, signal, b)
    return Result("D09 Session token expired (403)", "crash before any order; CRIT says re-login", f"{r}; orders {len(b.orders)}",
                  _ok(r == "CRASH" and len(b.orders) == 0, "TokenException" in c.alerts_text()),
                  "Kite: TokenException = clear the session and log in again (manual, Day 22).")

def d10_crash_while_saving(bars, signal, root):
    c = Ctx(root); b = FlakyBroker(CAPITAL); mini_session(c, "2018-12-03", bars, signal, b)
    before = open(c.state).read(); real = pipeline.json.dump
    def boom(*a, **k): raise OSError("No space left on device (drill)")
    pipeline.json.dump = boom
    try: r = mini_session(c, TRADE_DAY, bars, signal, b)
    finally: pipeline.json.dump = real
    after = open(c.state).read(); leftovers = [f for f in os.listdir(root) if f.startswith("tmp")]
    nxt = str(bars.index[bars.index.get_loc(pd.Timestamp(TRADE_DAY)) + 1].date()); mini_session(c, nxt, bars, signal, b)
    bk = c.book(); intact = before == after and bk["qty"] == b.qty and len(b.orders) == 1
    return Result("D10 Disk full while saving state", "old state.json intact (atomic write); CRIT; next run reconciles",
                  f"{r}; state unchanged: {before == after}; next day book {bk['qty']} vs broker {b.qty}, orders {len(b.orders)}; temp files left: {len(leftovers)}",
                  _ok(bool(intact), "crashed" in c.alerts_text()),
                  "The fill happened before the crash, and next day's recovery applied it from the broker's order book." + (" Finding: save_state leaves a temp file behind on failure; clean it up (failing-first test)." if leftovers else ""))

def d11_double_run(bars, signal, root):
    c = Ctx(root); b = FlakyBroker(CAPITAL); fl = b.fail; b.fail = None; setup(c, bars, signal, b); b.fail = fl
    mini_session(c, TRADE_DAY, bars, signal, b); n = len(b.orders); mini_session(c, TRADE_DAY, bars, signal, b)
    return Result("D11 Cron fires twice", "second run is a no-op", f"orders after run1 {n}, after run2 {len(b.orders)}",
                  "PASS" if len(b.orders) == n == 1 and "skip" in c.journal_kinds() else "FAIL")

def d12_manual_trade(bars, signal, root):
    c = Ctx(root); b = FlakyBroker(CAPITAL); mini_session(c, "2018-12-03", bars, signal, b)
    b.orders["M1"] = pipeline.BrokerOrder("M1", "", SYM, "BUY", 5, "LIMIT", 110.0, status="COMPLETE", filled_qty=5, avg_price=109.0); b.qty += 5
    mini_session(c, TRADE_DAY, bars, signal, b); bk = c.book()
    return Result("D12 Someone trades by hand in the Kite app", "foreign order → HALT + CRIT, nothing new sent",
                  f"halted={bk['halted'][:60]!r}; our orders sent {b.sent}", _ok("foreign order" in bk["halted"] and b.sent == 0, "CRIT" in c.alerts_text()))

DRILLS = [d01_kill_file, d02_kill_cancels_only_ours, d03_kill_flatten, d04_lost_before_send, d05_lost_after_send, d06_rejected,
          d07_no_data, d08_stale_preflight, d09_token_expired, d10_crash_while_saving, d11_double_run, d12_manual_trade]

def run_all() -> list[Result]:
    bars, signal = load_data(); out = []
    for d in DRILLS:
        root = tempfile.mkdtemp(prefix="drill_")
        try: out.append(d(bars, signal, root))
        except Exception as e: out.append(Result(d.__name__, "?", f"drill itself crashed: {e!r}", "FAIL"))
        finally: shutil.rmtree(root, ignore_errors=True)
    return out

def to_md(res: list[Result]) -> str:
    L = ["# Failure drills", "", "| Drill | Hypothesis | Observed | Verdict |", "|---|---|---|---|"]
    L += [f"| {r.name} | {r.hypothesis} | {r.observed} | **{r.verdict}** |" for r in res]
    n = {v: sum(r.verdict == v for r in res) for v in ("PASS", "SAFE-BUT-ACCIDENTAL", "FAIL")}
    L += ["", f"PASS {n['PASS']} · SAFE-BUT-ACCIDENTAL {n['SAFE-BUT-ACCIDENTAL']} · FAIL {n['FAIL']}", "", "## Lessons"]
    L += [f"- **{r.name}**: {r.lesson}" for r in res if r.lesson]
    return "\n".join(L)

if __name__ == "__main__":
    md = to_md(run_all()); open(os.path.join(HERE, "drills_report.md"), "w").write(md); print(md)
