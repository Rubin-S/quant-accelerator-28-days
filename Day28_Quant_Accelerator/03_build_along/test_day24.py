import json, os, time, pandas as pd, pytest, copy
from alerts import Alerter, Heartbeat, redact
from recovery import reconcile
from kill import write_kill, cancel_ours, flatten, clear
from pipeline import PaperBroker, new_book
from risk_engine import load_rulebook, Order
import run_live

HERE = os.path.dirname(os.path.abspath(__file__))

class Rec:
    def __init__(self, fail=False): self.calls, self.fail = [], fail
    def __call__(self, url, data, headers=None):
        if self.fail: raise OSError("network down")
        self.calls.append((url, data, headers)); return 200

def test_alert_levels_dedupe_and_redaction(tmp_path):
    t = [1000.0]; post = Rec()
    a = Alerter("TOKEN123", "42", "https://ntfy.sh/xyz", log_path=str(tmp_path / "a.log"), post=post, clock=lambda: t[0])
    assert a.send("INFO", "boring") == []
    assert a.send("WARN", "late data") == ["telegram", "ntfy"]
    assert a.send("WARN", "late data") == []                        # deduped within 30 min
    t[0] += 1801; assert a.send("WARN", "late data") == ["telegram", "ntfy"]
    assert a.send("CRIT", "x") and a.send("CRIT", "x")             # CRIT is never deduped
    a.send("CRIT", "oops access_token=SECRETVALUE")
    assert all(b"SECRETVALUE" not in c[1] for c in post.calls) and "SECRETVALUE" not in open(tmp_path / "a.log").read()

def test_alert_failure_never_raises(tmp_path):
    a = Alerter("T", "1", None, log_path=str(tmp_path / "a.log"), post=Rec(fail=True))
    assert a.send("CRIT", "boom") == [] and "send failed" in open(tmp_path / "a.log").read()

def test_heartbeat_urls():
    p = Rec(); h = Heartbeat("https://hc-ping.com/uuid", post=p); h.start(); h.ok(); h.fail()
    assert [c[0] for c in p.calls] == ["https://hc-ping.com/uuid/start", "https://hc-ping.com/uuid", "https://hc-ping.com/uuid/fail"]
    assert Heartbeat(None).ok() is False

def O(oid, status, side="BUY", qty=70, px=270.0, tag="F10261201B0", sym="NIFTYBEES"):
    return dict(order_id=oid, tradingsymbol=sym, tag=tag, status=status, transaction_type=side, filled_quantity=qty if status == "COMPLETE" else 0, average_price=px)

def test_recovery_applies_missed_fill_once():
    book = new_book(20000)
    book, acts, halt = reconcile([O("1", "COMPLETE")], book, "NIFTYBEES", broker_qty=70)
    assert book["qty"] == 70 and not halt and "applied" in acts[0]
    book, acts, halt = reconcile([O("1", "COMPLETE")], book, "NIFTYBEES", broker_qty=70)   # second start: no double count
    assert book["qty"] == 70 and acts == []

def test_recovery_open_order_blocks_resend_and_foreign_halts():
    book, acts, halt = reconcile([O("2", "OPEN")], new_book(20000), "NIFTYBEES", 0)
    assert "do NOT resend" in acts[0] and "F10261201B0" in book["tags"] and not halt
    _, _, halt = reconcile([O("3", "COMPLETE", tag=None)], new_book(20000), "NIFTYBEES", 70)
    assert "foreign order" in halt
    _, _, halt = reconcile([], new_book(20000), "NIFTYBEES", 5)
    assert "mismatch" in halt

def test_kill_layers(tmp_path):
    class K:
        def __init__(self): self.cancelled, self.placed = [], []
        def orders(self): return [dict(order_id="9", tradingsymbol="NIFTYBEES", tag="F10261201B0", status="OPEN", variety="regular"),
                                  dict(order_id="8", tradingsymbol="NIFTYBEES", tag="F10261101B0", status="COMPLETE")]
        def cancel_order(self, variety, order_id): self.cancelled.append(order_id)
        def place_order(self, **kw): self.placed.append(kw); return "77"
    k = K(); assert cancel_ours(k, "NIFTYBEES") == ["9"]
    flatten(k, "NIFTYBEES", 70, 270.0, "KILL261201"); p = k.placed[0]
    assert p["order_type"] == "LIMIT" and p["transaction_type"] == "SELL" and p["price"] == 267.3
    kf = str(tmp_path / "KILL"); write_kill(kf, "test"); assert os.path.exists(kf)
    with pytest.raises(ValueError): clear(kf, "ok", str(tmp_path / "inc.md"))
    assert clear(kf, "Reviewed journal; mismatch was a manual test order, reconciled.", str(tmp_path / "inc.md")) and not os.path.exists(kf)

def bars(n=260):
    idx = pd.bdate_range("2025-11-03", periods=n); px = pd.Series([250 + 0.1 * i for i in range(n)], idx)
    return pd.DataFrame(dict(Open=px, High=px * 1.005, Low=px * 0.995, Close=px))

def setup(tmp_path, ok=True, date=None):
    b = bars(); d = date or str(b.index[-1].date())
    json.dump(dict(ALL_OK=ok, ran_at=d + "T09:20:00+05:30"), open(tmp_path / "pf.json", "w"))
    rb, _ = load_rulebook(os.path.join(HERE, "rulebook.json")); return b, d, rb

def test_session_aborts_without_fresh_preflight(tmp_path):
    b, d, rb = setup(tmp_path, ok=False); p = Rec()
    r = run_live.session(d, b, None, str(tmp_path / "s.json"), str(tmp_path / "j.jsonl"), rb, Alerter("T", "1", None, log_path=str(tmp_path / "a"), post=p),
                         Heartbeat("https://hc/x", post=p), str(tmp_path / "pf.json"), str(tmp_path / "KILL"), 20000)
    assert r["status"] == "ABORT_PREFLIGHT" and any("/fail" in c[0] for c in p.calls) and not os.path.exists(tmp_path / "s.json")

def test_session_runs_saves_state_and_is_rerunnable(tmp_path):
    b, d, rb = setup(tmp_path); p = Rec()
    args = (d, b, None, str(tmp_path / "s.json"), str(tmp_path / "j.jsonl"), rb, Alerter("T", "1", None, log_path=str(tmp_path / "a"), post=p),
            Heartbeat("https://hc/x", post=p), str(tmp_path / "pf.json"), str(tmp_path / "KILL"), 20000)
    r1 = run_live.session(*args); r2 = run_live.session(*args)
    assert r1["status"] == r2["status"] == "OK" and r2["orders"] == 0
    assert json.load(open(tmp_path / "s.json"))["book"]["last_run"] == d

def test_session_missing_bar_aborts(tmp_path):
    b, d, rb = setup(tmp_path, date="2030-01-01"); p = Rec()
    r = run_live.session("2030-01-01", b, None, str(tmp_path / "s.json"), str(tmp_path / "j.jsonl"), rb, Alerter("T", "1", None, log_path=str(tmp_path / "a"), post=p),
                         Heartbeat(None), str(tmp_path / "pf.json"), str(tmp_path / "KILL"), 20000)
    assert r["status"] == "ABORT_DATA"

def test_forced_drill_places_one_paper_order(tmp_path):
    b, d, rb = setup(tmp_path); p = Rec(); rb = copy.deepcopy(rb); rb["orders"]["max_order_value_inr"] = 1e9
    r = run_live.session(d, b, None, str(tmp_path / "s.json"), str(tmp_path / "j.jsonl"), rb, Alerter("T", "1", None, log_path=str(tmp_path / "a"), post=p),
                         Heartbeat(None), str(tmp_path / "pf.json"), str(tmp_path / "KILL"), 20000, force_target=1.0)
    st = json.load(open(tmp_path / "s.json"))
    assert r["orders"] == 1 and st["book"]["qty"] == st["broker"]["qty"] > 0
