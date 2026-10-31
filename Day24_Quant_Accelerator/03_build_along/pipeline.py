"""
pipeline.py: Day 23. One trading day, end to end:  data → signal → target → risk checks → broker → fills → reconcile → log.

The SAME run_day() drives three brokers:
  PaperBroker(mode="close")   fills at that session's close ± slippage: must reproduce the Day 15 backtest exactly (parity)
  PaperBroker(mode="limit")   fills only if the day's range trades through your limit: what real limit orders feel like
  KiteBroker                  thin wrapper over pykiteconnect: LIMIT, CNC, tagged; same interface, swapped in on Week 4

Design rules:
  * Idempotent: run it twice on one day and the second run sends NOTHING (state.last_run + deterministic order tags ≤ 20 chars).
  * Append-only JSONL journal: every decision, check, order, fill and reconciliation, with timestamps. State is rebuilt from it.
  * The risk engine (Day 21) is called before every order and after every close. A violation = no order, logged.
  * Fail closed: missing data, mismatch, or any exception → HALT and log. Never "try again harder".
"""
from __future__ import annotations
import dataclasses as dc, datetime as dt, json, math, os, tempfile
import pandas as pd
from risk_engine import Order, State, pre_trade_check, end_of_day, target_weight, IST
from nse_costs import leg_costs

# ------------------------------------------------------------------ signal (pure functions)
def is_decision_day(today: pd.Timestamp, prev_session: pd.Timestamp | None) -> bool:
    """First session of a calendar month. Known in the morning without peeking: the previous session was last month."""
    return prev_session is not None and (today.year, today.month) != (prev_session.year, prev_session.month)

def faber_signal(closes_to_prev_session: pd.Series, months: int = 10) -> int | None:
    """1 if the last month-end close > mean of the last `months` month-end closes, else 0. None = not enough history.
    Input must END at the previous session (the Day 15 rule: never use today's close for today's decision)."""
    m = closes_to_prev_session.groupby([closes_to_prev_session.index.year, closes_to_prev_session.index.month]).last()
    if len(m) < months: return None
    return int(m.iloc[-1] > m.iloc[-months:].mean())

def order_tag(date: pd.Timestamp, side: str, attempt: int = 0) -> str:
    t = f"F10{date:%y%m%d}{side[0]}{attempt}"          # e.g. F10181203B0: 11 chars, under Kite's 20-char limit
    assert len(t) <= 20
    return t

# ------------------------------------------------------------------ brokers
@dc.dataclass
class BrokerOrder:
    order_id: str; tag: str; symbol: str; side: str; qty: int; order_type: str; limit_price: float
    status: str = "OPEN"; filled_qty: int = 0; avg_price: float = 0.0; fees: float = 0.0; reason: str = ""

class PaperBroker:
    """Your own fill simulator. Holdings live HERE (the 'broker's' truth); the pipeline keeps its own book and reconciles."""
    def __init__(self, cash: float, mode: str = "close", slippage_bps: float = 5.0, instrument: str = "etf_equity"):
        assert mode in ("close", "limit")
        self.cash, self.qty, self.mode, self.slip, self.instrument = cash, 0, mode, slippage_bps / 1e4, instrument
        self.orders: dict[str, BrokerOrder] = {}; self._n = 0

    def place(self, o: Order, market_protection: float | None = None) -> BrokerOrder:
        self._n += 1; bo = BrokerOrder(f"P{self._n:06d}", o.tag, o.symbol, o.side, o.qty, o.order_type, o.limit_price)
        if len(o.tag) > 20: bo.status, bo.reason = "REJECTED", "tag > 20 chars"
        elif o.order_type == "MARKET" and not market_protection: bo.status, bo.reason = "REJECTED", "market order without market_protection"
        elif o.qty <= 0: bo.status, bo.reason = "REJECTED", "qty <= 0"
        elif o.side == "SELL" and o.qty > self.qty: bo.status, bo.reason = "REJECTED", "insufficient holdings"
        elif o.side == "BUY" and o.qty * o.limit_price > self.cash: bo.status, bo.reason = "REJECTED", "insufficient funds"
        self.orders[bo.order_id] = bo
        return bo

    def on_bar(self, bar: pd.Series) -> list[BrokerOrder]:
        """Process OPEN orders against one session's OHLC. Unfilled orders are cancelled at the close (DAY validity)."""
        done = []
        for bo in self.orders.values():
            if bo.status != "OPEN": continue
            buy = bo.side == "BUY"
            if self.mode == "close":
                px = bar.Close * (1 + self.slip if buy else 1 - self.slip)
                ok = px <= bo.limit_price if buy else px >= bo.limit_price
            else:   # limit mode: the day must trade through the limit; you get the better of open and limit
                ok = bar.Low <= bo.limit_price if buy else bar.High >= bo.limit_price
                px = min(bar.Open, bo.limit_price) if buy else max(bar.Open, bo.limit_price)
            if not ok: bo.status, bo.reason = "CANCELLED", "not filled by close"; done.append(bo); continue
            value = bo.qty * px; fee = leg_costs(value, "buy" if buy else "sell", "delivery", self.instrument)["total"]
            if buy and value + fee > self.cash: bo.status, bo.reason = "REJECTED", "insufficient funds at fill"; done.append(bo); continue
            self.cash += -(value + fee) if buy else (value - fee); self.qty += bo.qty if buy else -bo.qty
            bo.status, bo.filled_qty, bo.avg_price, bo.fees = "COMPLETE", bo.qty, px, fee; done.append(bo)
        return done

    def holdings_qty(self, symbol: str) -> int: return self.qty

    def orders_today(self, symbol: str = "NIFTYBEES") -> list[dict]:
        """Kite-shaped order book, so recovery.reconcile() runs unchanged against paper and live."""
        return [dict(order_id=o.order_id, tradingsymbol=o.symbol, tag=o.tag, status=o.status, transaction_type=o.side,
                     filled_quantity=o.filled_qty, average_price=o.avg_price, status_message=o.reason) for o in self.orders.values()]

    def to_dict(self) -> dict:
        return dict(cash=self.cash, qty=self.qty, mode=self.mode, slip=self.slip, n=self._n)

    @classmethod
    def from_dict(cls, d: dict) -> "PaperBroker":
        b = cls(d["cash"], d["mode"], d["slip"] * 1e4); b.qty, b._n = d["qty"], d["n"]; return b

class KiteBroker:
    """Week 4. Same interface. LIMIT + CNC + tag; never MARKET. Fills arrive by polling orders() (or postbacks)."""
    def __init__(self, kite): self.kite = kite
    def place(self, o: Order, market_protection: float | None = None) -> BrokerOrder:
        kw = dict(variety="regular", exchange="NSE", tradingsymbol=o.symbol, transaction_type=o.side, quantity=o.qty,
                  product="CNC", order_type=o.order_type, validity="DAY", tag=o.tag)
        if o.order_type == "LIMIT": kw["price"] = round(o.limit_price, 2)
        if o.order_type == "MARKET": kw["market_protection"] = market_protection   # mandatory via API since Apr 2026
        oid = self.kite.place_order(**kw)
        return BrokerOrder(str(oid), o.tag, o.symbol, o.side, o.qty, o.order_type, o.limit_price)
    def holdings_qty(self, symbol: str) -> int:
        h = sum(x["quantity"] + x.get("t1_quantity", 0) for x in self.kite.holdings() if x["tradingsymbol"] == symbol)
        p = sum(x["quantity"] for x in self.kite.positions()["net"] if x["tradingsymbol"] == symbol and x["product"] == "CNC")
        return int(h + p)

# ------------------------------------------------------------------ journal + state
class Journal:
    def __init__(self, path: str): self.path = path
    def log(self, kind: str, **payload):
        rec = dict(ts=dt.datetime.now(IST).isoformat(timespec="seconds"), kind=kind, **payload)
        with open(self.path, "a") as f: f.write(json.dumps(rec, default=str) + "\n")
        return rec

def save_state(path: str, d: dict):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)) or ".")
    with os.fdopen(fd, "w") as f: json.dump(d, f, default=str)
    os.replace(tmp, path)                      # atomic: a crash mid-write never leaves half a state file

# ------------------------------------------------------------------ one trading day
def run_day(today: pd.Timestamp, hist: pd.DataFrame, book: dict, broker, rb: dict, journal: Journal,
            symbol: str = "NIFTYBEES", order_time: str = "15:00", limit_pct: float = 0.5, backtest_max_dd: float = -0.256,
            signal_closes: pd.Series | None = None) -> dict:
    """hist = OHLC sessions up to and including `today` (today's bar is used ONLY by the paper broker to fill, and to mark
    at the close). `book` = our own record: cash, qty, pending_target, last_run, peak, day/month start equity, halted, killed."""
    if book.get("last_run") == str(today.date()):
        journal.log("skip", date=today, why="already ran today (idempotent)"); return book
    sessions = hist.index; i = sessions.get_loc(today); prev = sessions[i - 1] if i > 0 else None
    bar = hist.loc[today]; last_close = hist.Close.iloc[i - 1] if i > 0 else bar.Open

    # 1. execute yesterday's decision today (Day 15 timing: decide on t, trade on t+1)
    tgt = book.get("pending_target")
    if tgt is not None:
        ref = bar.Close if order_time >= "15:00" else bar.Open           # the LTP we'd see when sending (no peeking at the close at 09:30)
        equity_est = book["cash"] + book["qty"] * ref
        want_qty = math.floor(equity_est * tgt / ref) if tgt > 0 else 0
        dq = want_qty - book["qty"]
        if dq != 0:
            side = "BUY" if dq > 0 else "SELL"
            # limit_pct > 0: marketable cushion (pay up to +x% to be sure of a fill); < 0: passive (try to save x%, may miss)
            lim = ref * (1 + limit_pct / 100) if side == "BUY" else ref * (1 - limit_pct / 100)
            o = Order(symbol, side, abs(dq), "LIMIT", round(lim, 2), order_tag(today, side, book.get("attempt", 0)))
            if side == "BUY" and o.qty * o.limit_price > book["cash"]:      # size to cash after the limit cushion
                o.qty = max(int(book["cash"] // (o.limit_price * 1.001)), 0)
            now = dt.datetime.combine(today.date(), dt.time.fromisoformat(order_time), tzinfo=IST)
            st = State(equity=equity_est, peak_equity=book["peak"], day_start_equity=book["day_start"], month_start_equity=book["month_start"],
                       position_qty=book["qty"], broker_qty=broker.holdings_qty(symbol), last_price=ref,
                       data_timestamp=now - dt.timedelta(minutes=1), orders_today=0, rejects_today=0,
                       recent_tags=book.get("tags", [])[-50:], halted=book.get("halted", ""), killed=book.get("killed", ""))
            v = pre_trade_check(o, st, now, rb, kill_file=book.get("kill_file", "/nonexistent/KILL"))
            journal.log("pre_trade", date=today, order=dc.asdict(o), violations=v)
            if v:
                book["halted"] = book.get("halted") or f"pre-trade violation {v[0]} on {today.date()}"
            else:
                bo = broker.place(o); book.setdefault("tags", []).append(o.tag); journal.log("order", date=today, **dc.asdict(bo))
                if isinstance(broker, PaperBroker):
                    for f in broker.on_bar(bar): journal.log("fill" if f.status == "COMPLETE" else "unfilled", date=today, **dc.asdict(f))
                fills = [x for x in broker.orders.values() if x.tag == o.tag] if isinstance(broker, PaperBroker) else []
                if fills and fills[-1].status == "COMPLETE":
                    f = fills[-1]; sgn = 1 if f.side == "BUY" else -1
                    book["qty"] += sgn * f.filled_qty; book["cash"] -= sgn * f.filled_qty * f.avg_price + f.fees
                    book["pending_target"] = None; book["attempt"] = 0
                else:
                    book["attempt"] = book.get("attempt", 0) + 1                 # retry tomorrow with a new tag
                    if book["attempt"] >= 3: book["halted"] = f"3 unfilled attempts by {today.date()}"
        else:
            book["pending_target"] = None

    # 2. decide (on the first session of a month, from closes up to the previous session)
    if is_decision_day(today, prev):
        sc = hist.Close.iloc[:i] if signal_closes is None else signal_closes.loc[:prev]   # live: NIFTY index closes to the previous session
        sig = faber_signal(sc, rb.get("months", 10))
        if sig is not None:
            book["pending_target"] = target_weight(sig, None, rb); book["attempt"] = 0
            journal.log("decision", date=today, signal=sig, target=book["pending_target"])

    # 3. reconcile + end-of-day risk
    bq = broker.holdings_qty(symbol)
    if bq != book["qty"]:
        book["halted"] = book.get("halted") or f"position mismatch book {book['qty']} vs broker {bq}"; journal.log("mismatch", date=today, book=book["qty"], broker=bq)
    equity = book["cash"] + book["qty"] * bar.Close
    st = State(equity=equity, peak_equity=book["peak"], day_start_equity=book["day_start"], month_start_equity=book["month_start"],
               position_qty=book["qty"], broker_qty=bq, last_price=bar.Close, data_timestamp=dt.datetime.now(IST),
               halted=book.get("halted", ""), killed=book.get("killed", ""))
    st, ev = end_of_day(st, today.date(), rb, backtest_max_dd)
    for e in ev: journal.log("risk_event", date=today, event=e)
    nxt = sessions[i + 1] if i + 1 < len(sessions) else None
    book.update(peak=st.peak_equity, halted=st.halted, killed=st.killed, equity=equity, last_run=str(today.date()), day_start=equity)
    if nxt is None or (nxt.year, nxt.month) != (today.year, today.month): book["month_start"] = equity
    journal.log("eod", date=today, equity=round(equity, 2), qty=book["qty"], cash=round(book["cash"], 2), halted=book["halted"], killed=book["killed"])
    return book

def new_book(capital: float) -> dict:
    return dict(cash=capital, qty=0, pending_target=None, last_run=None, peak=capital, day_start=capital, month_start=capital,
                halted="", killed="", tags=[], attempt=0)
