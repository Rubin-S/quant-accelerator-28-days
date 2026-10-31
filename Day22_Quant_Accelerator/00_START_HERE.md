# DAY 22: Sat 21 Nov 2026: THE PIPES, PART 1
## Broker app, static-IP server, one honest login a day

Today you build the road, not the car. No orders today. Day 23 adds the paper broker.

| Time | Block | What | Files |
|---|---|---|---|
| 20 min | Drill | Token expiry for 5 login times · "which preflight check fails first?" × 5 | |
| 30 min | Read | Kite docs: User, Exceptions, Orders (market_protection) + Zerodha API FAQ | RESOURCES |
| 40 min | Build | VM in Mumbai + static IP → `sudo bash bootstrap_vm.sh <laptop-ip>` | 03_ |
| 25 min | Build | Kite developer console: app (Personal or Connect, and write why), redirect `http://127.0.0.1:5000/callback`, whitelist the static IP | |
| 25 min | Build | Secrets in `/etc/rubin-trader/kite.env` → SSH tunnel → `python kite_session.py login` | 03_ |
| 20 min | Verify | `python preflight.py --static-ip <ip>` → ALL OK; `pytest -q` (9 pass) | 03_ |
| 20 min | Write | `vm-runbook.md` with evidence | 04_ |
| 20 min | Problems | 10 problems | 05_ |
≈ 3.3 h.

## Facts you're building on (checked 1 Nov 2026)
- **Plans:** Personal = free (orders, GTT, portfolio, no market data). Connect = ₹500/month per API key (+ live WebSocket + historical candles). Your signal can come from NSE files, so free may be enough.
- **Static IP:** required for order place/modify/cancel since 1 Apr 2026; up to two IPs (primary + secondary) in the developer console.
- **Login:** manual, once a day. Zerodha says the exchange requires it and doesn't support automating it. Tokens die at **06:00 IST** the next day.
- **Rate limits:** 10 orders/s, 400/min, 5,000/day. You'll send about 2 a month.
- **Market orders via API need `market_protection`** since Apr 2026. You use LIMIT orders anyway (rulebook).
- **AWS:** every public IPv4 costs $0.005/hour (~$3.65/month) unless you're in the 12-month EC2 free tier.

## Mentor's rulings
1. **No TOTP bots.** One human login a day; if you miss it, the system fails closed and does nothing. That's correct.
2. **api_secret lives in one file on one server.** If it touches git, chat or a screenshot, regenerate it the same hour.
3. **Preflight or nothing.** Any FAIL means no orders that day, logged, no exceptions.
4. **No inbound ports but SSH from your own IP.**

Send me: vm-runbook.md with evidence + preflight.json + `pytest -q` output + 10 problems + training-log row.
Day 23 (Sun 22 Nov): the pipeline: data → signal → risk → paper broker → logs.
