"""The live path gets the same scrutiny as the backtest. Small synthetic markets, exact expectations."""
import copy, json, os, pandas as pd, pytest
from pipeline import is_decision_day, faber_signal, order_tag, PaperBroker, KiteBroker, Journal, run_day, new_book, save_state
from risk_engine import Order, load_rulebook

HERE = os.path.dirname(os.path.abspath(__file__))
RB0, _ = load_rulebook(os.path.join(HERE, "rulebook.json"))

def rb_big():
    rb = copy.deepcopy(RB0); rb["orders"]["max_order_value_inr"] = 1e9; return rb

def market(n_months=14, up=True, start="2025-01-01"):
    idx = pd.bdate_range(start, periods=21 * n_months)
    px = pd.Series([100 + (i if up else -i) * 0.2 for i in range(len(idx))], idx)
    return pd.DataFrame(dict(Open=px, High=px * 1.01, Low=px * 0.99, Close=px))

def test_decision_day():
    assert is_decision_day(pd.Timestamp("2026-12-01"), pd.Timestamp("2026-11-30"))
    assert not is_decision_day(pd.Timestamp("2026-12-02"), pd.Timestamp("2026-12-01"))
    assert not is_decision_day(pd.Timestamp("2026-12-01"), None)

def test_faber_signal_needs_history_and_ignores_today():
    m = market(14)
    assert faber_signal(m.Close, 10) == 1 and faber_signal(market(14, up=False).Close, 10) == 0
    short = m.Close.loc[:m.index[21 * 5]]
    assert faber_signal(short, 10) is None

def test_order_tag_short_and_unique():
    t = order_tag(pd.Timestamp("2026-12-01"), "BUY"); assert len(t) <= 20 and t != order_tag(pd.Timestamp("2026-12-01"), "BUY", 1)

def test_paper_broker_rejections():
    b = PaperBroker(10_000)
    assert b.place(Order("NIFTYBEES", "BUY", 10, "MARKET", 100, "T1")).status == "REJECTED"            # no market_protection
    assert b.place(Order("NIFTYBEES", "SELL", 1, "LIMIT", 100, "T2")).status == "REJECTED"              # nothing held
    assert b.place(Order("NIFTYBEES", "BUY", 1, "LIMIT", 100, "X" * 21)).status == "REJECTED"           # tag > 20
    assert b.place(Order("NIFTYBEES", "BUY", 1000, "LIMIT", 100, "T3")).status == "REJECTED"            # funds

def test_limit_mode_fill_rules():
    bar = pd.Series(dict(Open=100.0, High=101.0, Low=99.5, Close=100.5))
    b = PaperBroker(1e6, mode="limit"); b.place(Order("NIFTYBEES", "BUY", 10, "LIMIT", 99.0, "P1"))
    assert b.on_bar(bar)[0].status == "CANCELLED"                       # low 99.5 never reached 99.0
    b.place(Order("NIFTYBEES", "BUY", 10, "LIMIT", 100.2, "P2")); f = b.on_bar(bar)[0]
    assert f.status == "COMPLETE" and f.avg_price == 100.0 and b.qty == 10   # better of open and limit

def test_close_mode_respects_limit():
    bar = pd.Series(dict(Open=100.0, High=103.0, Low=99.0, Close=102.0))
    b = PaperBroker(1e6, mode="close"); b.place(Order("NIFTYBEES", "BUY", 1, "LIMIT", 101.0, "C1"))
    assert b.on_bar(bar)[0].status == "CANCELLED"                       # close + slippage above the limit

def run_all(m, rb, broker=None, rerun=False, tmp="/tmp/j.jsonl"):
    open(tmp, "w").close(); j = Journal(tmp); b = broker or PaperBroker(1e6); book = new_book(1e6)
    for d in m.index[230:]:
        book["halted"] = ""
        book = run_day(d, m.loc[:d], book, b, rb, j)
        if rerun: book = run_day(d, m.loc[:d], book, b, rb, j)
    return book, b, [json.loads(l) for l in open(tmp)]

def test_uptrend_buys_once_and_book_matches_broker(tmp_path):
    book, b, log = run_all(market(14), rb_big(), tmp=str(tmp_path / "j.jsonl"))
    assert book["qty"] > 0 and book["qty"] == b.qty and abs(book["cash"] - b.cash) < 1e-6
    assert sum(1 for e in log if e["kind"] == "decision") >= 1 and not any(e["kind"] == "mismatch" for e in log)

def test_idempotent_rerun(tmp_path):
    _, _, l1 = run_all(market(14), rb_big(), tmp=str(tmp_path / "a.jsonl"))
    _, _, l2 = run_all(market(14), rb_big(), rerun=True, tmp=str(tmp_path / "b.jsonl"))
    n = lambda L: sum(1 for e in L if e["kind"] == "order")
    assert n(l1) == n(l2) and any(e["kind"] == "skip" for e in l2)

def test_risk_violation_blocks_and_halts(tmp_path):
    rb = copy.deepcopy(RB0); rb["orders"]["max_order_value_inr"] = 10          # every real order is too big
    book, b, log = run_all(market(14), rb, tmp=str(tmp_path / "j.jsonl"))
    assert b.qty == 0 and not any(e["kind"] == "order" for e in log)
    assert any(e["kind"] == "pre_trade" and e["violations"] for e in log)

def test_mismatch_halts(tmp_path):
    m = market(14); j = Journal(str(tmp_path / "j.jsonl")); b = PaperBroker(1e6); book = new_book(1e6)
    b.qty = 5                                                            # someone traded in the Kite app by hand
    book = run_day(m.index[230], m.loc[:m.index[230]], book, b, rb_big(), j)
    assert "mismatch" in book["halted"]

def test_kite_broker_sends_limit_cnc_with_tag():
    class FakeKite:
        def __init__(self): self.calls = []
        def place_order(self, **kw): self.calls.append(kw); return "2512010001"
    k = FakeKite(); KiteBroker(k).place(Order("NIFTYBEES", "BUY", 70, "LIMIT", 270.456, "F10261201B0"))
    c = k.calls[0]
    assert c["order_type"] == "LIMIT" and c["product"] == "CNC" and c["price"] == 270.46 and c["tag"] == "F10261201B0" and "market_protection" not in c

def test_atomic_state(tmp_path):
    p = tmp_path / "state.json"; save_state(str(p), dict(a=1)); assert json.load(open(p)) == dict(a=1)
