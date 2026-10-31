import json, pandas as pd, numpy as np, pytest
import live_vs_backtest as lvb

def mk(n=300, start="2025-01-01", up=True):
    idx = pd.bdate_range(start, periods=n); px = pd.Series([100 + (0.2 if up else -0.2) * i for i in range(n)], idx)
    return idx, px

def J(kind, d, **kw): return dict(ts="x", kind=kind, date=str(pd.Timestamp(d).date()), **kw)

def test_backtest_positions_timing():
    idx, px = mk()
    window = idx[200:260]; pos = lvb.backtest_positions(window, px, 10, start_in=False)
    dec = [d for k, d in enumerate(window) if k > 0 and d.month != window[k - 1].month][0]
    k = list(window).index(dec)
    assert not pos.iloc[k] and pos.iloc[k + 1]          # decide on t, hold from t+1

def test_signal_mismatch_flagged():
    idx, px = mk(); d = [x for x in idx[220:] if x.day <= 3 and x.month != (x - pd.Timedelta(days=4)).month][0]
    j = [J("eod", d, qty=0, equity=20000), J("decision", d, signal=0, target=0.0)]   # live said 0, uptrend says 1
    r = lvb.diff(j, pd.DataFrame(dict(Close=px / 100)), px)
    assert r["d1"][0]["recomputed"] == 1 and not r["d1"][0]["match"]

def test_position_mismatch_and_drill_explanation():
    idx, px = mk(); days = idx[250:255]
    j = [J("eod", d, qty=10, equity=20000) for d in days]                  # live held, backtest (start out, no decision) didn't
    j0 = [J("eod", days[0], qty=0, equity=20000)] + j[1:]
    r = lvb.diff(j0, pd.DataFrame(dict(Close=px / 100)), px)
    assert len(r["d2_mismatch_days"]) == 4 and r["d2_explained_by_drill"] == []
    r2 = lvb.diff(j0 + [J("forced_drill", days[1], target=1.0)], pd.DataFrame(dict(Close=px / 100)), px)
    assert len(r2["d2_explained_by_drill"]) == 4

def test_fill_slippage_math_and_attribution_adds_up():
    idx, px = mk(); days = idx[250:254]; bars = pd.DataFrame(dict(Close=px / 100))
    c = float(bars.Close.loc[days[1]]); fill = c * 1.0015                      # paid 15 bps over the close
    j = [J("eod", days[0], qty=0, equity=20000), J("forced_drill", days[1], target=1.0),
         J("fill", days[1], tag="F10A", side="BUY", filled_qty=100, avg_price=fill, limit_price=fill * 1.01, fees=3.0, status="COMPLETE"),
         J("eod", days[1], qty=100, equity=20000 - 100 * (fill - c) - 3.0)]
    for d in days[2:]: j.append(J("eod", d, qty=100, equity=j[-1]["equity"] + 100 * float(bars.Close.loc[d] - bars.Close.loc[d - pd.tseries.offsets.BDay()])))
    r = lvb.diff(j, bars, px)
    x = r["d3"][0]; assert abs(x["slip_vs_close_bps"] - 15) < 1e-6 and abs(x["excess_vs_assumption_bps"] - 10) < 0.01
    a = r["d5"]; assert abs(a["residual"]) < 5e-4

def test_verdict_needs_samples():
    idx, px = mk(); bars = pd.DataFrame(dict(Close=px / 100)); days = idx[250:262]
    j = [J("eod", d, qty=0, equity=20000) for d in days]
    assert lvb.diff(j, bars, px)["slip"]["verdict"] == "NO FILLS"
