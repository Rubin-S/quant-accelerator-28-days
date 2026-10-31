"""Hand-checked tests. Run: python3 -m pytest -q   (or: python3 test_nse_costs.py)"""
from nse_costs import leg_costs, round_trip, after_tax_gain, Rates
import math

def close(a, b, tol=0.01): return math.isclose(a, b, abs_tol=tol)

def test_delivery_equity_1lakh():
    rt = round_trip(1e5, 1e5, "delivery", "equity")
    assert rt["stt"] == 200                       # 0.1% x 2 legs
    assert close(rt["exchange_txn"], 6.14)        # 0.00307% x 2 lakh
    assert close(rt["sebi_fee"], 0.20)            # Rs 10/crore x 2 lakh
    assert close(rt["stamp_duty"], 15.0)          # 0.015% on buy only
    assert close(rt["gst"], 0.18 * (6.14 + 0.20))
    assert close(rt["dp_charge"], 15.34)
    assert close(rt["total"], 200 + 6.14 + 0.20 + 15 + 1.1412 + 15.34, 0.02)

def test_etf_equity_stt_tiny():
    rt = round_trip(1e5, 1e5, "delivery", "etf_equity")
    assert rt["stt"] == 1                          # 0.001% of 1 lakh on sell = Rs 1
    assert rt["total"] < 40

def test_gold_etf_no_stt():
    assert round_trip(1e5, 1e5, "delivery", "etf_other")["stt"] == 0

def test_intraday_brokerage_cap():
    assert close(leg_costs(1e6, "buy", "intraday")["brokerage"], 20.0)     # 0.03% of 10 lakh = 300 -> capped at 20
    assert close(leg_costs(5e4, "buy", "intraday")["brokerage"], 15.0)     # 0.03% of 50k = 15

def test_intraday_stt_sell_only():
    assert leg_costs(1e5, "buy", "intraday")["stt"] == 0
    assert leg_costs(1e5, "sell", "intraday")["stt"] == 25

def test_no_stamp_on_sell():
    assert leg_costs(1e5, "sell", "delivery")["stamp_duty"] == 0

def test_tax():
    assert close(after_tax_gain(10000, 100), 10000 - 10000 * 0.20 * 1.04)
    assert close(after_tax_gain(100000, 400), 100000)        # under the Rs 1.25 lakh LTCG exemption

if __name__ == "__main__":
    for name, f in list(globals().items()):
        if name.startswith("test_"): f(); print("PASS", name)
