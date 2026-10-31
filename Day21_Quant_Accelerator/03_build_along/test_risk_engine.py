"""Every rule in the rulebook gets a test that proves it can say NO. A risk check that can't fail is decoration."""
import datetime as dt, json, os, pytest
from risk_engine import Order, State, pre_trade_check, end_of_day, target_weight, kelly_report, triple_penance, is_session, IST, load_rulebook

HERE = os.path.dirname(os.path.abspath(__file__))
RB, _ = load_rulebook(os.path.join(HERE, "rulebook.json"))
NOW = dt.datetime(2026, 12, 1, 10, 0, tzinfo=IST)          # Tuesday 1 Dec 2026, 10:00 IST

def st(**kw):
    s = State(equity=20000, peak_equity=20000, day_start_equity=20000, month_start_equity=20000, position_qty=0, broker_qty=0,
              last_price=270.0, data_timestamp=NOW - dt.timedelta(minutes=2))
    for k, v in kw.items(): setattr(s, k, v)
    return s

def buy(**kw):
    o = Order("NIFTYBEES", "BUY", 70, "LIMIT", 270.5, "T1")
    for k, v in kw.items(): setattr(o, k, v)
    return o

def check(o=None, s=None, now=NOW, kill="/nonexistent/KILL"):
    return pre_trade_check(o or buy(), s or st(), now, RB, kill)

def test_clean_order_passes():
    assert check() == []

@pytest.mark.parametrize("o,frag", [
    (buy(symbol="RELIANCE"), "universe"), (buy(order_type="MARKET"), "LIMIT"), (buy(qty=0), "positive"),
    (buy(limit_price=280.0), "outside"), (buy(qty=100), "max"), (buy(side="SELL"), "no shorting")])
def test_bad_orders_rejected(o, frag):
    assert any(frag in v for v in check(o=o))

def test_leverage_blocked():
    assert any("exposure" in v for v in check(o=buy(qty=74), s=st(equity=20000)))    # 74 x 270.5 = 20,017 > 1.0x

def test_kill_file(tmp_path):
    k = tmp_path / "KILL"; k.write_text("stop")
    assert any("KILL SWITCH" in v for v in check(kill=str(k)))

def test_halt_blocks_signal_but_not_risk_exit():
    s = st(halted="test", position_qty=70, broker_qty=70)
    assert any("HALTED" in v for v in check(s=s))
    assert not any("HALTED" in v for v in check(o=buy(side="SELL", reason="risk_exit"), s=s))

def test_stale_data_mismatch_duplicates_rejects():
    assert any("old" in v for v in check(s=st(data_timestamp=NOW - dt.timedelta(hours=1))))
    assert any("mismatch" in v for v in check(s=st(broker_qty=5)))
    assert any("duplicate" in v for v in check(s=st(recent_tags=["T1"])))
    assert any("rejects" in v for v in check(s=st(rejects_today=2)))
    assert any("orders/day" in v for v in check(s=st(orders_today=4)))

def test_session_rules():
    assert not is_session(dt.datetime(2026, 11, 10, 11, 0, tzinfo=IST), RB)    # NSE holiday
    assert not is_session(dt.datetime(2026, 11, 21, 11, 0, tzinfo=IST), RB)    # Saturday
    assert not is_session(dt.datetime(2026, 12, 1, 9, 16, tzinfo=IST), RB)     # before the 09:30 window
    assert is_session(NOW, RB)

def test_end_of_day_halts_and_kills():
    s, ev = end_of_day(st(equity=18700), dt.date(2026, 12, 1), RB, -0.256)      # −6.5% day
    assert "HALT daily loss" in ev and s.halted and not s.killed
    s, ev = end_of_day(st(equity=12000, day_start_equity=12100, month_start_equity=12500), dt.date(2026, 12, 1), RB, -0.256)
    assert s.killed                                                                # −40% from peak > 1.5 × 25.6%

def test_sizing_caps():
    assert target_weight(1, None, RB) == 1.0 and target_weight(0, None, RB) == 0.0
    rb2 = json.loads(json.dumps(RB)); rb2["sizing"]["vol_target_annual"] = 0.30
    assert target_weight(1, 0.10, rb2) == 1.0                                      # vol scaling can't lever up past the cap

def test_kelly_and_penance():
    k = kelly_report(0.18, -0.32, 0.142, 0.5)
    assert k["full_kelly_lower"] == 0 and k["full_kelly_point"] == pytest.approx(1.268, abs=0.01)
    tp = triple_penance(0.5, 0.2)
    assert tp["max_years_under_water"] == pytest.approx(4 * tp["years_to_max_loss"])
    assert "infinite" in triple_penance(0.0, 0.2)["note"]
