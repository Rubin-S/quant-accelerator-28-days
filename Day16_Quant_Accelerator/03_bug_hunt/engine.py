"""
engine.py: Day 15 backtester v2 (v2.1: small refactors for speed). Event loop, NSE cost model, vol sizing, look-ahead made structurally hard.

Design (one bar = one NSE session, daily):
    for each session t:
        1. accrue interest on cash held overnight (t-1 -> t)
        2. FILL the order decided at t-1, at session t's close (+ slippage)    <- never at the open (Day 14)
        3. mark to market; record equity
        4. strategy sees ONLY bars <= t (DataFeed refuses anything later) -> target weight
        5. sizer turns the weight into a vol-targeted, capped (<= 1.0x) target -> pending order for t+1
Rules baked in: long/flat only, max 1.0x gross, integer units, cash never negative, every cost from nse_costs.py.

Fill-model note: the order carries a TARGET WEIGHT; units are computed at the fill bar's close. That approximates
placing a limit order near the close of t+1. It's deliberately conservative versus "fill at t's close".
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from nse_costs import leg_costs

class FutureAccessError(Exception):
    """Raised when anything asks the feed for data after the current bar."""

# ----------------------------------------------------------------------------------------------- data
class DataFeed:
    """Walks a DataFrame one row at a time. The strategy only ever gets views up to the cursor."""
    def __init__(self, df: pd.DataFrame, signal_col: str = "signal_close", trade_col: str = "trade_close"):
        need = {signal_col, trade_col}
        assert need <= set(df.columns), f"need columns {need}"
        assert df.index.is_monotonic_increasing and df.index.is_unique, "index must be sorted unique dates"
        assert (df[trade_col] > 0).all(), "trade prices must be positive (clean NaNs in the pipeline, not here)"
        self._df, self.signal_col, self.trade_col, self.i = df, signal_col, trade_col, -1
    def __len__(self): return len(self._df)
    def advance(self): self.i += 1; return self.i < len(self._df)
    @property
    def now(self) -> pd.Timestamp: return self._df.index[self.i]
    def bar(self) -> pd.Series: return self._df.iloc[self.i]
    def history(self, col: str, n: int | None = None) -> pd.Series:
        s = self._df[col].iloc[: self.i + 1]
        return s if n is None else s.iloc[-n:]
    def at(self, k: int) -> pd.Series:
        if k > self.i: raise FutureAccessError(f"asked for bar {k} while at bar {self.i}")
        return self._df.iloc[k]

# ----------------------------------------------------------------------------------------------- strategies
class Strategy:
    def on_bar(self, feed: DataFeed) -> float:  # return target weight in [0, 1]
        raise NotImplementedError

class FaberMonthly(Strategy):
    """10-month SMA filter on the signal series. The decision is made on the FIRST session of a new month, using
    month-end closes up to the PREVIOUS session. On the last day of a month you can't know it's the last day
    without peeking at tomorrow's date, which is a classic hidden leak."""
    def __init__(self, months: int = 10): self.months, self.w, self.prev = months, 0.0, None
    def on_bar(self, feed):
        now = feed.now
        if self.prev is not None and now.month != self.prev.month:
            closes = feed.history(feed.signal_col).iloc[:-1]                  # through the previous session
            m = closes.groupby([closes.index.year, closes.index.month]).last()
            if len(m) >= self.months:
                self.w = 1.0 if m.iloc[-1] > m.iloc[-self.months:].mean() else 0.0
        self.prev = now
        return self.w

class Constant(Strategy):
    def __init__(self, w): self.w = w
    def on_bar(self, feed): return self.w

class FromSeries(Strategy):
    """Plays back precomputed weights (for tests). Reads only today's value."""
    def __init__(self, s: pd.Series): self.s = s
    def on_bar(self, feed): return float(self.s.loc[feed.now])

# ----------------------------------------------------------------------------------------------- sizing
@dataclass
class VolTargetSizer:
    target_vol: float | None = 0.12   # annualised; None = no vol targeting (weight passes through)
    lam: float = 0.94                 # RiskMetrics daily EWMA decay
    cap: float = 1.0                  # house rule: never above 1.0x
    warmup: int = 60
    def size(self, w: float, feed: DataFeed) -> float:
        w = min(max(w, 0.0), 1.0)                                           # long/flat only
        if self.target_vol is None or w == 0.0: return min(w, self.cap)
        r = np.log(feed._df[feed.trade_col].iloc[: feed.i + 2]).diff().dropna()   # direct slice: ~3x faster than history()
        if len(r) < self.warmup: return 0.0                                 # no estimate yet -> stay flat
        var = r.pow(2).ewm(alpha=1 - self.lam, adjust=False).mean().iloc[-1]   # uses returns <= t only
        vol = math.sqrt(var * 252)
        return min(self.cap, w) * self.target_vol / vol if vol > 0 else 0.0

# ----------------------------------------------------------------------------------------------- costs & cash
@dataclass
class CostModel:
    slippage_bps: float = 5.0          # per side, half-spread + impact (Day 10 assumption)
    instrument: str = "etf_equity"
    use_nse: bool = True
    def fill_price(self, px, side):
        k = self.slippage_bps / 1e4
        return px * (1 + k) if side == "buy" else px * (1 - k)
    def fees(self, value, side):
        return leg_costs(value, side, "delivery", self.instrument)["total"] if (self.use_nse and value > 0) else 0.0

@dataclass
class CashModel:
    """Annual rate, constant or a Series indexed by date (e.g. an overnight-rate or LIQUIDBEES-derived series).
    Accrues on calendar days, ACT/365."""
    rate: float | pd.Series = 0.0
    def growth(self, d0, d1):
        r = self.rate if not isinstance(self.rate, pd.Series) else float(self.rate.asof(d0))
        return (1 + r) ** ((d1 - d0).days / 365.0)

# ----------------------------------------------------------------------------------------------- engine
@dataclass
class Result:
    equity: pd.Series
    weights: pd.Series         # held gross exposure at each close
    targets: pd.Series         # target weight decided at each close
    trades: pd.DataFrame
    cash: pd.Series
    units: pd.Series
    total_costs: float
    total_interest: float

class Engine:
    def __init__(self, feed: DataFeed, strategy: Strategy, sizer: VolTargetSizer | None = None,
                 costs: CostModel | None = None, cash: CashModel | None = None,
                 capital: float = 1_000_000.0, integer_units: bool = True, min_trade_value: float = 1_000.0,
                 band: float = 0.0):
        self.feed, self.strategy = feed, strategy
        self.sizer = sizer or VolTargetSizer(target_vol=None)
        self.costs, self.cashm = costs or CostModel(), cash or CashModel()
        self.cash, self.units, self.capital = capital, 0.0, capital
        self.integer_units, self.min_trade_value = integer_units, min_trade_value
        self.band = band   # no-trade band in weight units: skip rebalances smaller than this (vol sizing churns daily otherwise)

    def _fill(self, target_w, px, date, log):
        equity = self.cash + self.units * px
        want = target_w * equity
        cur = self.units * px
        if abs(want - cur) < self.min_trade_value: return 0.0
        if target_w > 0 and self.units > 0 and abs(target_w - cur / equity) < self.band: return 0.0  # entries/exits always go through
        side = "buy" if want > cur else "sell"
        fpx = self.costs.fill_price(px, side)
        if side == "buy":
            budget = min(want - cur, self.cash)
            q = budget / fpx
            if self.integer_units: q = math.floor(q)
            while q > 0 and q * fpx + self.costs.fees(q * fpx, "buy") > self.cash + 1e-9:  # fees must fit in cash
                q = q - 1 if self.integer_units else q * 0.999
        else:
            q = (cur - want) / px
            q = min(math.ceil(q) if self.integer_units else q, self.units)
        if q <= 0: return 0.0
        value = q * fpx; fee = self.costs.fees(value, side)
        if side == "buy": self.cash -= value + fee; self.units += q
        else:             self.cash += value - fee; self.units -= q
        log.append(dict(date=date, side=side, units=q, ref_px=px, fill_px=fpx, value=value, fees=fee))
        return fee

    def run(self) -> Result:
        f = self.feed; eq, wt, tg, cs, un, log = {}, {}, {}, {}, {}, []
        pending, prev_date, tot_cost, tot_int = None, None, 0.0, 0.0
        while f.advance():
            date, px = f.now, float(f.bar()[f.trade_col])
            if pending is not None:                                             # 1. fill yesterday's decision
                tot_cost += self._fill(pending, px, date, log); pending = None
            if prev_date is not None and self.cash > 0:                        # 2. overnight interest
                g = self.cashm.growth(prev_date, date); tot_int += self.cash * (g - 1); self.cash *= g
            equity = self.cash + self.units * px                                # 3. mark to market
            eq[date], wt[date], cs[date], un[date] = equity, self.units * px / equity, self.cash, self.units
            w = self.sizer.size(self.strategy.on_bar(f), f)                     # 4-5. decide for t+1
            tg[date] = w; pending = w; prev_date = date
            assert self.cash >= -1e-6, f"cash went negative on {date}"
            assert self.units >= 0, "short position: forbidden"
        return Result(pd.Series(eq), pd.Series(wt), pd.Series(tg), pd.DataFrame(log), pd.Series(cs), pd.Series(un),
                      tot_cost, tot_int)

# ----------------------------------------------------------------------------------------------- metrics
def metrics(eq: pd.Series, periods: int = 245, rf: float = 0.0) -> dict:
    """rf = annual cash rate. Report Sharpe in EXCESS of cash: a filter that sits in 6% cash half the time
    looks great on a 0%-rf Sharpe, and that's the cash talking, not the signal."""
    r = eq.pct_change().dropna(); yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    x = r - ((1 + rf) ** (1 / periods) - 1)
    dd = eq / eq.cummax() - 1
    return dict(CAGR=(eq.iloc[-1] / eq.iloc[0]) ** (1 / yrs) - 1, vol=r.std() * math.sqrt(periods),
                sharpe_xs=x.mean() / r.std() * math.sqrt(periods), max_dd=dd.min())

def load_frame(signal_csv, trade_csv, start=None, end="2018-12-31"):
    """Signal = NIFTY 50 index close; trade = the instrument you'll actually buy. Exploration window only."""
    s = pd.read_csv(signal_csv, parse_dates=["Date"], index_col="Date")["Close"].rename("signal_close")
    t = pd.read_csv(trade_csv, parse_dates=["Date"], index_col="Date")["Close"].rename("trade_close")
    df = pd.concat([s, t], axis=1, join="inner").dropna().loc[start:end]
    if df.index.max() >= pd.Timestamp("2019-01-01"): raise RuntimeError("holdout is sealed until Day 20")
    return df
