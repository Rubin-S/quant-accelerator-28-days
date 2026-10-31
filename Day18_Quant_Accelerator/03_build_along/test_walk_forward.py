"""The walk-forward harness is itself a backtest: it can leak. These tests make it prove it doesn't."""
import numpy as np, pandas as pd, pytest
from walk_forward import walk_forward, sharpe_xs

def fake(seed=0, years=10):
    idx = pd.bdate_range("2009-01-01", periods=252 * years); rng = np.random.default_rng(seed)
    rets = pd.DataFrame({m: rng.normal(0.0003 * k, 0.01, len(idx)) for k, m in enumerate([8, 10, 12], 1)}, idx)
    W = pd.DataFrame(1.0, idx, rets.columns); cash = pd.Series(0.0, idx)
    return rets, W, cash

def test_pick_ignores_the_test_year():
    rets, W, cash = fake()
    _, p1 = walk_forward(rets, W, cash, [8, 10, 12], "expanding")
    y = sorted(p1)[3]; bumped = rets.copy(); bumped.loc[str(y), 8] += 0.05     # make 8m wildly great IN year y
    _, p2 = walk_forward(bumped, W, cash, [8, 10, 12], "expanding")
    assert p1[y][0] == p2[y][0]                 # the pick for year y cannot see year y
    assert p2[y + 1][0] == 8                    # ...but next year it can

def test_stitched_oos_uses_only_picked_column():
    rets, W, cash = fake(1)
    r, picks = walk_forward(rets, W, cash, [8, 10, 12], "rolling")
    for y, (m, _) in picks.items():
        assert np.allclose(r.loc[str(y)].iloc[1:], rets.loc[str(y), m].iloc[1:])

def test_min_training_years_respected():
    rets, W, cash = fake(2)
    _, picks = walk_forward(rets, W, cash, [8, 10, 12], "expanding", min_train_years=3)
    assert min(picks) == rets.index.year.min() + 3

def test_switch_cost_charged_only_on_exposure_change():
    rets, W, cash = fake(3)
    r, picks = walk_forward(rets, W, cash, [8, 10, 12], "expanding")   # W all 1.0 -> |dw| = 0 -> no charge
    for y, (m, _) in picks.items():
        assert r.loc[str(y)].iloc[0] == pytest.approx(rets.loc[str(y), m].iloc[0])

def test_sharpe_zero_vol_is_zero():
    idx = pd.bdate_range("2010-01-01", periods=10)
    assert sharpe_xs(pd.Series(0.0, idx), pd.Series(0.0, idx)) == 0.0
