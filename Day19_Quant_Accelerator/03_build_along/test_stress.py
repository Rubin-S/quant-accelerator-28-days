"""Stress code is code. If a stress is wrong, it gives false comfort, which is worse than no stress at all."""
import numpy as np, pandas as pd, pytest
from stress import Delay, ScaledCost, spells, drop_best
from engine import Strategy, CostModel

class Seq(Strategy):
    def __init__(self, xs): self.xs, self.i = xs, -1
    def on_bar(self, feed): self.i += 1; return self.xs[self.i]

class F:  # minimal feed stand-in
    now = None

def test_delay_shifts_targets_by_k():
    s = Delay(Seq([1, 2, 3, 4, 5]), 2)
    assert [s.on_bar(F) for _ in range(5)] == [0.0, 0.0, 1, 2, 3]

def test_delay_zero_is_identity():
    s = Delay(Seq([0.0, 1.0, 1.0]), 0)
    assert [s.on_bar(F) for _ in range(3)] == [0.0, 1.0, 1.0]

def test_scaled_cost_doubles_slippage_and_fees():
    base, two = CostModel(), ScaledCost(mult=2.0)
    assert two.fill_price(100, "buy") - 100 == pytest.approx(2 * (base.fill_price(100, "buy") - 100))
    assert two.fees(1e6, "sell") == pytest.approx(2 * base.fees(1e6, "sell"))

def test_spells_found():
    idx = pd.bdate_range("2010-01-01", periods=10)
    w = pd.Series([0, 1, 1, 0, 0, 1, 1, 1, 0, 1], idx, dtype=float)
    sp = spells(w)
    assert len(sp) == 3 and sp[0] == (idx[1], idx[3])

def test_drop_best_trade_replaces_with_cash_only_inside_spell():
    idx = pd.bdate_range("2010-01-01", periods=6)
    r = pd.Series([0.0, 0.10, 0.10, 0.0, 0.01, 0.0], idx); cash = pd.Series(0.0001, idx)
    sp = [(idx[1], idx[3]), (idx[4], idx[5])]
    out = drop_best(r, cash, sp, 1)
    assert out.iloc[1] == out.iloc[2] == 0.0001 and out.iloc[4] == 0.01

def test_drop_best_days():
    idx = pd.bdate_range("2010-01-01", periods=5)
    r = pd.Series([0.05, -0.01, 0.02, 0.0, 0.03], idx)
    out = drop_best(r, pd.Series(0.0, idx), "days", 2)
    assert out.iloc[0] == 0 and out.iloc[4] == 0 and out.iloc[2] == 0.02
