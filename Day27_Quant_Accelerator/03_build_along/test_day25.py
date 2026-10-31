import datetime as dt, json, os, pandas as pd
from session_review import review, to_markdown
from dashboard import status, headroom, build, svg_lines
from risk_engine import load_rulebook

HERE = os.path.dirname(os.path.abspath(__file__)); RB, _ = load_rulebook(os.path.join(HERE, "rulebook.json"))
T = "2026-11-23T15:00:00+05:30"

def ev(kind, date="2026-11-23", **kw): return dict(ts=T, kind=kind, date=date, **kw)

def test_clean_session_has_no_breaches():
    r = review([ev("eod", equity=20000, halted="")], None, [])
    assert r["anomalies"] == []

def test_contract_breaches_detected():
    j = [ev("eod", equity=1, halted=""), ev("eod", equity=1, halted=""),                                # C1 twice
         ev("crash", date="2026-11-25", error="KeyError"),                                              # C1 missing + C2
         ev("pre_trade", date="2026-11-26", order=dict(tag="F10X"), violations=["max_order_value"]),
         ev("order", date="2026-11-26", tag="F10X", status="OPEN"), ev("eod", date="2026-11-26", equity=1, halted="")]  # C3, C4, C8
    a = " ".join(review(j, None, [])["anomalies"])
    for c in ("C1", "C2", "C3", "C4", "C8"): assert c in a

def test_incident_note_explains_breach_and_crit():
    j = [ev("mismatch", book=5, broker=0), ev("eod", equity=1, halted="mismatch")]
    al = [dict(ts="2026-11-23T15:01:00+05:30", level="CRIT", text="[CRIT] 2026-11-23: position mismatch")]
    assert len(review(j, None, al)["anomalies"]) == 2
    assert review(j, None, al, incidents_text="## 2026-11-23 mismatch\nexplained")["anomalies"] == []

def test_state_book_vs_broker():
    st = dict(book=dict(qty=70, cash=100.0), broker=dict(qty=0, cash=100.0))
    assert any("C6" in x for x in review([], st, [])["anomalies"])

def test_shortfall_sign():
    closes = pd.Series([100.0, 101.0], pd.to_datetime(["2026-11-20", "2026-11-23"]))
    j = [ev("forced_drill", target=1.0), ev("order", tag="F10A", status="OPEN"),
         ev("fill", tag="F10A", side="BUY", avg_price=101.0, limit_price=101.5, fees=3.0), ev("eod", equity=1, halted="")]
    s = review(j, None, [], closes=closes)["shortfalls"][0]
    assert s["shortfall_bps"] == 100.0 and s["vs_limit_bps"] < 0
    assert "Order path quality" in to_markdown(review(j, None, [], closes=closes))

def test_status_priority():
    d = dt.date(2026, 11, 26)
    assert status(dict(book=dict(killed="dd", halted="x")), True, "2026-11-25", d)[0] == "KILLED"
    assert status(dict(book=dict(halted="x")), True, "2026-11-25", d)[0] == "HALTED"
    assert status(dict(book={}), True, "2026-11-25", d)[0] == "KILL FILE"
    assert status(dict(book={}), False, "2026-11-16", d)[0] == "STALE"
    assert status(dict(book={}), False, "2026-11-25", d)[0] == "OK"
    assert status(None, False, None, d)[0] == "NO DATA"

def test_headroom_fractions():
    st = dict(book=dict(cash=0, equity=18800, day_start=20000, month_start=20000, peak=20000))
    h = {n: u for n, u, _ in headroom(st, RB, -0.256)}
    assert abs(h["Daily loss"] - 1.0) < 1e-9 and abs(h["Monthly loss"] - 0.5) < 1e-9 and abs(h["Drawdown → KILL"] - 0.06 / 0.384) < 1e-9

def test_dashboard_escapes_and_renders():
    j = [ev("eod", equity=20000, halted=""), ev("note", msg="<script>alert(1)</script>")]
    st = dict(book=dict(qty=0, cash=20000, equity=20000, day_start=20000, month_start=20000, peak=20000, halted="", killed=""), broker=dict(qty=0, cash=20000))
    bars = pd.DataFrame(dict(Close=[100.0]), index=pd.to_datetime(["2026-11-23"]))
    page = build(j, st, [], None, RB, bars, today=dt.date(2026, 11, 23))
    assert "<script>alert" not in page and "trader: OK" in page and "Risk headroom" in page

def test_svg_has_one_line_per_series():
    s = pd.Series([1.0, 1.1], pd.to_datetime(["2026-11-23", "2026-11-25"]))
    assert svg_lines({"a": s, "b": s * 0.9}).count("<polyline") == 2
