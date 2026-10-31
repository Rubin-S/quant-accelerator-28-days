"""pytest -q test_engine.py   — 15 tests. Every engine change must keep these green (tomorrow I plant bugs; these are your nets)."""
import math, numpy as np, pandas as pd, pytest
from hypothesis import given, settings, strategies as st
from engine import (DataFeed, Engine, FaberMonthly, Constant, FromSeries, VolTargetSizer, CostModel, CashModel,
                    FutureAccessError, Strategy)
from nse_costs import leg_costs

def synth(n=600, seed=0, vol=0.01, start="2010-01-01"):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start, periods=n)
    p = 100 * np.exp(np.cumsum(rng.normal(0.0003, vol, n)))
    return pd.DataFrame({"signal_close": p, "trade_close": p}, index=idx)

FRICTIONLESS = dict(costs=CostModel(slippage_bps=0, use_nse=False), cash=CashModel(0.0), integer_units=False, min_trade_value=0)

# 1 ── the feed refuses the future
def test_feed_refuses_future():
    f = DataFeed(synth(10)); f.advance(); f.advance()
    assert len(f.history("trade_close")) == 2
    with pytest.raises(FutureAccessError): f.at(5)

# 2 ── a strategy that peeks crashes instead of silently winning
def test_peeking_strategy_crashes():
    class Peek(Strategy):
        def on_bar(self, feed): return 1.0 if feed.at(feed.i + 1)["trade_close"] > feed.bar()["trade_close"] else 0.0
    with pytest.raises(FutureAccessError): Engine(DataFeed(synth(50)), Peek()).run()

# 3 ── perturbation: scrambling prices after t changes nothing up to t
@pytest.mark.parametrize("t", [250, 400, 520])
def test_perturbation(t):
    df = synth(); base = Engine(DataFeed(df), FaberMonthly(), VolTargetSizer(0.12)).run()
    q = df.copy(); q.iloc[t + 1:] *= np.random.default_rng(1).uniform(0.5, 1.5, (len(q) - t - 1, 1))
    alt = Engine(DataFeed(q), FaberMonthly(), VolTargetSizer(0.12)).run()
    d = df.index[t]
    pd.testing.assert_series_equal(base.equity.loc[:d], alt.equity.loc[:d])
    pd.testing.assert_series_equal(base.targets.loc[:d], alt.targets.loc[:d])

# 4 ── timing: a decision at close t fills at close t+1, never t
def test_fill_is_next_session():
    df = synth(30); w = pd.Series(0.0, df.index); w.iloc[10:] = 1.0
    res = Engine(DataFeed(df), FromSeries(w)).run()
    assert res.trades.date.iloc[0] == df.index[11]
    assert res.weights.iloc[10] == 0.0 and res.weights.iloc[11] > 0.9

# 5 ── frictionless engine == one-line vectorised backtest (to 1e-10)
def test_matches_vectorised():
    df = synth(); w = pd.Series(np.random.default_rng(3).uniform(0, 1, len(df)), df.index)
    res = Engine(DataFeed(df), FromSeries(w), **FRICTIONLESS).run()
    r = df.trade_close.pct_change().fillna(0)
    ref = 1e6 * (1 + w.shift(2).fillna(0) * r).cumprod()
    np.testing.assert_allclose(res.equity.values, ref.values, rtol=1e-10)

# 6 ── accounting identity every day: equity = cash + units × price
def test_accounting_identity():
    df = synth(); res = Engine(DataFeed(df), FaberMonthly(), VolTargetSizer(0.12), cash=CashModel(0.06)).run()
    np.testing.assert_allclose(res.equity, res.cash + res.units * df.trade_close, rtol=1e-12)

# 7 ── cash-flow ledger: final cash = start − buys + sells − fees + interest
def test_cash_ledger():
    df = synth(); res = Engine(DataFeed(df), FaberMonthly(), cash=CashModel(0.06)).run()
    t = res.trades; buys = t[t.side == "buy"].value.sum(); sells = t[t.side == "sell"].value.sum()
    assert math.isclose(res.cash.iloc[-1], 1e6 - buys + sells - t.fees.sum() + res.total_interest, rel_tol=1e-10)

# 8 ── house rules: never above 1.0x, never short, cash never negative, whole units
def test_house_rules():
    df = synth(vol=0.002)   # very low vol tempts the sizer to lever up
    res = Engine(DataFeed(df), Constant(1.0), VolTargetSizer(0.50)).run()
    assert res.weights.max() <= 1.0 + 1e-9 and res.units.min() >= 0 and res.cash.min() >= 0
    assert (res.trades.units == res.trades.units.round()).all()

# 9 ── flat strategy earns exactly the cash rate (ACT/365)
def test_flat_earns_cash():
    df = synth(300); res = Engine(DataFeed(df), Constant(0.0), cash=CashModel(0.065)).run()
    days = (df.index[-1] - df.index[0]).days
    assert math.isclose(res.equity.iloc[-1], 1e6 * 1.065 ** (days / 365), rel_tol=1e-12)

# 10 ── fees equal nse_costs.leg_costs exactly; slippage applied on the right side
def test_costs_wired_to_nse_costs():
    df = synth(40); w = pd.Series(0.0, df.index); w.iloc[5:20] = 1.0
    res = Engine(DataFeed(df), FromSeries(w), costs=CostModel(slippage_bps=5)).run()
    b, s = res.trades.iloc[0], res.trades.iloc[1]
    assert b.side == "buy" and math.isclose(b.fill_px, b.ref_px * 1.0005)
    assert s.side == "sell" and math.isclose(s.fill_px, s.ref_px * 0.9995)
    assert math.isclose(b.fees, leg_costs(b.value, "buy", "delivery", "etf_equity")["total"])
    assert math.isclose(s.fees, leg_costs(s.value, "sell", "delivery", "etf_equity")["total"])

# 11 ── vol sizer: weight ≈ target/vol, smaller when vol is higher, capped at 1
def test_vol_sizer():
    for v, expect in [(0.02, 0.12 / (0.02 * math.sqrt(252))), (0.002, 1.0)]:
        f = DataFeed(synth(400, vol=v)); [f.advance() for _ in range(400)]
        w = VolTargetSizer(0.12).size(1.0, f)
        assert math.isclose(w, expect, rel_tol=0.30) if expect < 1 else w == 1.0   # EWMA(0.94) ≈ 33 obs: ~12% noise in vol

# 12 ── Faber decides only on month turns, using last month's close
def test_faber_month_turn():
    df = synth(); res = Engine(DataFeed(df), FaberMonthly()).run()
    changes = res.targets[res.targets.diff().fillna(0) != 0].index
    prev = [df.index[df.index.get_loc(d) - 1] for d in changes]
    assert all(d.month != p.month for d, p in zip(changes, prev))

# 13 ── determinism
def test_deterministic():
    df = synth(); a = Engine(DataFeed(df), FaberMonthly(), VolTargetSizer()).run(); b = Engine(DataFeed(df), FaberMonthly(), VolTargetSizer()).run()
    pd.testing.assert_series_equal(a.equity, b.equity)

# 15 ── no-trade band cuts churn but never blocks a full exit
def test_band_cuts_churn_not_exits():
    df = synth(); a = Engine(DataFeed(df), FaberMonthly(), VolTargetSizer(0.12)).run()
    b = Engine(DataFeed(df), FaberMonthly(), VolTargetSizer(0.12), band=0.10).run()
    assert len(b.trades) < len(a.trades) / 3
    flat_days = b.targets[b.targets == 0].index
    later = [df.index[df.index.get_loc(d) + 1] for d in flat_days if df.index.get_loc(d) + 1 < len(df)]
    assert (b.units.loc[later] == 0).all()

# 14 ── property test: random paths + random weights never break the rules or the identity
@settings(max_examples=40, deadline=None)
@given(seed=st.integers(0, 10_000), slip=st.floats(0, 50), rate=st.floats(0, 0.1))
def test_property_rules_hold(seed, slip, rate):
    df = synth(250, seed=seed, vol=0.02); w = pd.Series(np.random.default_rng(seed).choice([0, .3, 1], len(df)), df.index)
    res = Engine(DataFeed(df), FromSeries(w), costs=CostModel(slippage_bps=slip), cash=CashModel(rate)).run()
    assert res.cash.min() >= -1e-6 and res.units.min() >= 0 and res.weights.max() <= 1.0 + 1e-9
    np.testing.assert_allclose(res.equity, res.cash + res.units * df.trade_close, rtol=1e-10)
