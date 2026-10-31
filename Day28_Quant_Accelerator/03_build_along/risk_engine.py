"""
risk_engine.py: Day 21. Your rulebook as code. The Day 23 pipeline calls this before EVERY order and after EVERY close.

Design rules (why each exists):
  * Pure functions + a JSON rulebook: rules live in data, are hashed, and can't be "just tweaked" in code at 10:05.
  * Two kinds of stop, never mixed up:
      HALT    = stop sending orders, keep the position, investigate (plumbing smells: stale data, rejects, mismatch,
                or a loss limit). A halt never trades by itself.
      KILL    = flatten to cash and retire pending a written review (rulebook breach / retirement rule).
    Loss limits on a monthly trend overlay HALT; they don't liquidate. Liquidating on a bad day would be a NEW strategy
    (a stop-loss) that was never tested.
  * Knight Capital (SEC 2013): no check compared orders leaving with orders intended, and nobody could stop it quickly.
    Hence the duplicate guard, the max-orders-per-day cap, the position-mismatch halt, and the kill-switch FILE that any
    human (or cron) can create.
  * SEBI retail algo framework (4 Feb 2025, live 1 Apr 2026): API via static IP + 2FA; under 10 orders/second needs no
    algo registration. This engine allows a handful of orders per DAY.
"""
from __future__ import annotations
import datetime as dt, hashlib, json, math, os
from dataclasses import dataclass, field

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))

def load_rulebook(path: str) -> tuple[dict, str]:
    raw = open(path, "rb").read()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()

@dataclass
class Order:
    symbol: str
    side: str            # "BUY" / "SELL"
    qty: int
    order_type: str      # must be "LIMIT"
    limit_price: float
    tag: str             # unique client order id
    reason: str = "signal"   # "signal" or "risk_exit"

@dataclass
class State:
    equity: float                    # account value allocated to this strategy (₹)
    peak_equity: float               # high-water mark since go-live
    day_start_equity: float
    month_start_equity: float
    position_qty: int                # what OUR books say we hold
    broker_qty: int                  # what the BROKER says we hold
    last_price: float                # last traded / close price of the symbol
    data_timestamp: dt.datetime      # time of the last price we trust
    orders_today: int = 0
    rejects_today: int = 0
    recent_tags: list = field(default_factory=list)
    halted: str = ""                 # non-empty = halted, with the reason
    killed: str = ""                 # non-empty = killed, with the reason

# ------------------------------------------------------------------ sizing
def target_weight(signal: float, ewma_vol_annual: float | None, rb: dict) -> float:
    """signal in {0,1} from the pre-registered rule. Vol targeting only if the rulebook enables it (it's a NEW trial
    under the Day 15 ruling, so the default rulebook leaves it off). Hard cap: rb['max_gross_exposure'] (house rule 1.0)."""
    s = rb["sizing"]; w = float(signal) * s["base_weight"]
    if s.get("vol_target_annual") and ewma_vol_annual and ewma_vol_annual > 0:
        w = w * s["vol_target_annual"] / ewma_vol_annual
    return max(0.0, min(w, rb["max_gross_exposure"]))

def kelly_report(sharpe_annual: float, sharpe_lo90: float, vol_annual: float, fraction: float) -> dict:
    """Continuous-time Kelly leverage on excess returns: f* = mu/sigma^2 = SR/sigma. Computed at the point estimate and
    at the LOWER 90% bound, because the point estimate is the thing you're least sure of (Thorp; Carver)."""
    f_pt = sharpe_annual / vol_annual; f_lo = max(0.0, sharpe_lo90 / vol_annual)
    return dict(full_kelly_point=f_pt, frac_kelly_point=f_pt * fraction, full_kelly_lower=f_lo, frac_kelly_lower=f_lo * fraction,
                verdict=("Kelly at the lower bound is 0: the edge is unproven, so size by RISK BUDGET (money you can lose), "
                         "not by edge." if f_lo == 0 else "Lower-bound Kelly is positive; still cap at the house limit."))

# ------------------------------------------------------------------ pre-trade checks
def is_session(now: dt.datetime, rb: dict) -> bool:
    n = now.astimezone(IST)
    if n.weekday() >= 5 or n.date().isoformat() in rb["market"]["holidays"]: return False
    o = dt.time.fromisoformat(rb["market"]["order_window_start"]); c = dt.time.fromisoformat(rb["market"]["order_window_end"])
    return o <= n.time() <= c

def pre_trade_check(o: Order, st: State, now: dt.datetime, rb: dict, kill_file: str) -> list[str]:
    """Every reason this order must NOT go out. Empty list = allowed. Order of checks: cheapest kill first."""
    v = []
    if os.path.exists(kill_file): v.append(f"KILL SWITCH FILE present ({kill_file})")
    if st.killed: v.append(f"strategy KILLED: {st.killed}")
    if st.halted and o.reason != "risk_exit": v.append(f"strategy HALTED: {st.halted}")
    if o.symbol not in rb["universe"]: v.append(f"symbol {o.symbol} not in universe {rb['universe']}")
    if o.order_type != "LIMIT": v.append("only LIMIT orders allowed")
    if o.qty <= 0: v.append("qty must be positive")
    if o.side not in ("BUY", "SELL"): v.append("side must be BUY or SELL")
    if not is_session(now, rb): v.append("outside the order window or not a trading day")
    age = (now - st.data_timestamp).total_seconds() / 60
    if age > rb["data"]["max_staleness_minutes"]: v.append(f"price data is {age:.0f} min old (max {rb['data']['max_staleness_minutes']})")
    if st.position_qty != st.broker_qty: v.append(f"position mismatch: ours {st.position_qty} vs broker {st.broker_qty}")
    band = rb["orders"]["max_price_deviation_pct"] / 100
    if st.last_price > 0 and abs(o.limit_price / st.last_price - 1) > band: v.append(f"limit price {o.limit_price} outside ±{band:.1%} of last {st.last_price}")
    value = o.qty * o.limit_price
    if value > rb["orders"]["max_order_value_inr"]: v.append(f"order value ₹{value:,.0f} > max ₹{rb['orders']['max_order_value_inr']:,.0f}")
    if o.side == "SELL" and o.qty > st.position_qty: v.append("sell qty exceeds holding (no shorting)")
    if o.side == "BUY":
        new_w = (st.position_qty + o.qty) * o.limit_price / st.equity if st.equity > 0 else math.inf
        if new_w > rb["max_gross_exposure"] + 1e-9: v.append(f"post-trade exposure {new_w:.2f}x > cap {rb['max_gross_exposure']}x (no leverage)")
    if st.orders_today >= rb["orders"]["max_orders_per_day"]: v.append(f"max {rb['orders']['max_orders_per_day']} orders/day reached")
    if o.tag in st.recent_tags: v.append(f"duplicate order tag {o.tag} (Knight check: is this order already out?)")
    if st.rejects_today >= rb["orders"]["max_rejects_per_day"]: v.append("too many broker rejects today: halt and investigate")
    return v

# ------------------------------------------------------------------ end-of-day risk update
def end_of_day(st: State, today: dt.date, rb: dict, backtest_max_dd: float) -> tuple[State, list[str]]:
    """Update limits after the close. Returns (state, events). HALTs keep the position; KILL flattens + retires."""
    ev = []; L = rb["loss_limits"]
    st.peak_equity = max(st.peak_equity, st.equity)
    day_ret = st.equity / st.day_start_equity - 1; mon_ret = st.equity / st.month_start_equity - 1
    dd = st.equity / st.peak_equity - 1
    if day_ret <= -L["daily_loss_halt_pct"] / 100:
        st.halted = st.halted or f"daily loss {day_ret:.1%} on {today}: review before next order"; ev.append("HALT daily loss")
    if mon_ret <= -L["monthly_loss_halt_pct"] / 100:
        st.halted = st.halted or f"month-to-date loss {mon_ret:.1%} on {today}: written review"; ev.append("HALT monthly loss")
    kill_dd = -L["kill_drawdown_multiple_of_backtest"] * abs(backtest_max_dd)
    if dd <= kill_dd:
        st.killed = f"drawdown {dd:.1%} beyond {kill_dd:.1%} ({L['kill_drawdown_multiple_of_backtest']}× backtest max DD) on {today}"
        ev.append("KILL drawdown: flatten and retire pending review")
    if st.position_qty != st.broker_qty:
        st.halted = st.halted or f"position mismatch at close on {today}"; ev.append("HALT position mismatch")
    return st, ev

def triple_penance(sharpe_annual: float, vol_annual: float, z: float = 1.645) -> dict:
    """Bailey & Lopez de Prado (2015), IID normal case. Max quantile loss and the time to reach it, plus the 'triple
    penance' time under water (≈ 4× the time to the max loss). Shows why time-based retirement rules are useless at low SR."""
    mu = sharpe_annual * vol_annual
    if mu <= 0: return dict(note="mu <= 0: expected recovery time is infinite, so no time-under-water rule can work")
    t_star = (z * vol_annual / (2 * mu)) ** 2
    return dict(max_quantile_loss=(z * vol_annual) ** 2 / (4 * mu), years_to_max_loss=t_star, max_years_under_water=4 * t_star)
