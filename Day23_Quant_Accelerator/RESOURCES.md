# Day 23 resources: the pipeline and the paper broker (checked 1 Nov 2026)

## Broker docs (what your KiteBroker must handle)
- Kite Connect **Orders**: LIMIT/CNC params, `tag` (max 20 chars; longer is rejected, not truncated, per Zerodha staff on the forum), order statuses, and `market_protection` (mandatory for API MARKET/SL-M orders since Apr 2026; 0 is rejected, −1 = auto). https://kite.trade/docs/connect/v3/orders/
- Kite forum, "Order tag: underscores allowed? Over-20-char rejected or truncated?" (Sep 2026): https://kite.trade/forum/discussion/16261/order-tag-underscores-allowed-over-20-char-rejected-or-truncated-also-default-market-protection
- Kite forum, "market_protection: is it enforced today, and what happens to any unfilled quantity?" (Sep 2026): a partly filled protected order leaves the rest pending. https://kite.trade/forum/discussion/16276/market-protection-is-it-enforced-today-and-what-happens-to-any-unfilled-quantity
- Kite Connect **Portfolio** (holdings incl. `t1_quantity`, positions): what `holdings_qty()` reconciles against. https://kite.trade/docs/connect/v3/portfolio/
- Kite Connect **Postbacks / WebHooks** (order updates pushed to you; polling is fine at your speed): https://kite.trade/docs/connect/v3/postbacks/

## Engineering practice (free)
- Stripe, "Designing robust and predictable APIs with idempotency": why every order needs a deterministic key so a retry never doubles it. https://stripe.com/blog/idempotency
- Google SRE book, ch. 6 "Monitoring Distributed Systems": the four golden signals and alerting on symptoms. https://sre.google/sre-book/monitoring-distributed-systems/
- The Twelve-Factor App, "Logs": treat logs as an event stream (your JSONL journal). https://12factor.net/logs
- ArchWiki, systemd timers (run the pipeline at 15:00 IST on trading days, with logging and restart rules): https://wiki.archlinux.org/title/Systemd/Timers

## Code to study
- **NautilusTrader** (open source, LGPL): built around "the same strategy code in backtest and live". Read the README's backtest/live parity section. Today's replay test is that idea, small. https://github.com/nautechsystems/nautilus_trader
- pykiteconnect (Day 22 kit).

## Already in earlier kits
- SEC Knight order + FIA 2024 controls: **Day 21**. Every pipeline guard below maps to one of them.
- Day 14 ruling: never model fills at the ETF's opening prints. The replay's 09:30 test uses the INDEX open as a stand-in, so treat it as optimistic.

## Build-along (03_build_along), 12 tests pass
- `pipeline.py`: `run_day()` (data → signal → target → `pre_trade_check` → broker → fills → reconcile → `end_of_day` → journal), `PaperBroker` (close mode and limit mode), `KiteBroker` (LIMIT + CNC + tag), atomic state save, deterministic tags.
- `replay.py`: drives the live pipeline day by day over 2008–2018: **parity vs the Day 15 engine**, marketable vs passive limit fills, idempotence → `replay_out/replay_report.md` + JSONL journals.
- `test_pipeline.py`: decision day, signal without peeking, broker rejections, fill rules, idempotence, risk block, mismatch halt, Kite payload.
- Carried over: `engine.py`, `risk_engine.py`, `rulebook.json`, `nse_costs.py`.
