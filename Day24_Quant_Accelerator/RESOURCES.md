# Day 24 resources: kill switch, recovery, alerts, paper session 1 (checked 1 Nov 2026)

## Broker side
- Kite Connect **Orders**: `GET /orders` returns today's order book only ("lives for a day"); order statuses (OPEN, COMPLETE, CANCELLED, REJECTED and interim ones like VALIDATION PENDING, OPEN PENDING); "successful placement does not imply execution": always check order history. `tag` max 20 chars. https://kite.trade/docs/connect/v3/orders/
- Kite Connect **Portfolio** (holdings incl. `t1_quantity`; positions): https://kite.trade/docs/connect/v3/portfolio/
- Zerodha **Kill switch** (Console): disables a segment; can be re-enabled only after 12 hours; Zerodha asks you to have no open orders or positions before disabling. https://support.zerodha.com/category/console/segments/killswitch/articles/what-is-the-kill-switch
- Zerodha video, "How to disable segments and take a break from trading using Kill Switch?" (Feb 2024): https://www.youtube.com/watch?v=0C99HmwOAGg

## Alerts and the dead man's switch (all free)
- Telegram Bot API (`sendMessage`): https://core.telegram.org/bots/api · beginner tutorial (create a bot with BotFather): https://core.telegram.org/bots/tutorial
- ntfy, publishing (plain HTTP POST, priority header): https://docs.ntfy.sh/publish/
- healthchecks.io: free Hobbyist plan monitors 20 jobs. https://healthchecks.io/pricing/ · ping endpoints `/start`, `/fail`, success; don't ping more than 5×/min. https://healthchecks.io/docs/http_api/

## Read again (earlier kits)
- SEC Knight order (Day 21): the 2012 failure was a dormant code path + no automated kill + alerts nobody acted on. Today closes all three.
- Google SRE ch. 6 (Day 23): alert on symptoms; every page must be actionable.

## Build-along (03_build_along), 22 tests pass
- `alerts.py`: Telegram + ntfy, INFO/WARN/CRIT, 30-min dedupe for WARN, secret redaction, never crashes the trader. `Heartbeat` for healthchecks.io.
- `recovery.py`: on every start, reconcile today's broker orders + holdings: apply a missed fill once, never resend while an order is open, HALT on a foreign order or mismatch.
- `kill.py`: halt (KILL file + cancel our open orders, keep position) / kill (also flatten with a −1% marketable LIMIT) / status / clear (human note ≥ 20 chars → incidents.md).
- `run_live.py`: the paper session: preflight gate → recovery → run_day → alerts → atomic state → heartbeat. `--force-target` paper-only drill.
- `fire_drill.py`: sends the 5 drill alerts to your phone + redaction check.
- Carried: `pipeline.py` (now with `orders_today()`, saved paper-broker state, separate NIFTY signal series), `risk_engine.py`, `rulebook.json`, `kite_session.py`, `preflight.py`, Day 23 tests.
