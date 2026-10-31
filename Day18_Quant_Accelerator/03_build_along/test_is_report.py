"""Tests for the report generator itself. A report tool with a bug is worse than no report."""
import numpy as np, pandas as pd, pytest
from is_report import stationary_idx, effective_n, max_dd, common_start, GateUntil, stats
from engine import DataFeed, Engine, Constant, FaberMonthly, CostModel, CashModel

def test_bootstrap_indices_valid_and_blocky():
    idx = stationary_idx(500, 20, 50, np.random.default_rng(0))
    assert idx.min() >= 0 and idx.max() < 500
    cont = (np.diff(idx, axis=1) == 1).mean()
    assert 0.9 < cont < 0.99            # ~ 1 - 1/20 of steps continue a block

def test_effective_n_identical_and_independent():
    x = np.random.default_rng(1).normal(size=(2000, 1))
    assert effective_n(pd.DataFrame(np.hstack([x, x, x]))) == pytest.approx(1.0, abs=1e-6)
    y = np.random.default_rng(2).normal(size=(2000, 3))
    assert effective_n(pd.DataFrame(y)) == pytest.approx(3.0, abs=0.1)

def test_max_dd_hand():
    eq = pd.Series([100, 110, 99, 121.0], index=pd.bdate_range("2010-01-01", periods=4))
    assert max_dd(eq) == pytest.approx(99 / 110 - 1)

def test_common_start_is_after_longest_lookback():
    idx = pd.bdate_range("2007-09-17", "2009-12-31")
    t0 = common_start(pd.DataFrame(index=idx), 12)
    assert t0 == pd.Timestamp("2008-09-01")

def test_gate_holds_zero_then_follows_inner():
    idx = pd.bdate_range("2010-01-01", periods=300); p = pd.Series(np.linspace(100, 200, 300), idx)
    df = pd.DataFrame({"signal_close": p, "trade_close": p})
    t0 = idx[150]; r = Engine(DataFeed(df), GateUntil(Constant(1.0), t0), costs=CostModel(0, use_nse=False)).run()
    assert r.weights.loc[:t0].max() == 0 and r.weights.iloc[-1] > 0.95

def test_fresh_strategy_objects_matter():
    """The bug I made writing this tool: reusing one FaberMonthly object across two runs leaks state."""
    rng = np.random.default_rng(3); idx = pd.bdate_range("2008-01-01", periods=900)
    p = pd.Series(np.linspace(100, 300, 900), idx)   # steady uptrend: the object ends holding w=1
    df = pd.DataFrame({"signal_close": p, "trade_close": p}); df = pd.DataFrame({"signal_close": p, "trade_close": p})
    s = FaberMonthly(); a = Engine(DataFeed(df), s).run().equity; b = Engine(DataFeed(df), s).run().equity
    c = Engine(DataFeed(df), FaberMonthly()).run().equity
    assert a.equals(c) and not a.equals(b)
