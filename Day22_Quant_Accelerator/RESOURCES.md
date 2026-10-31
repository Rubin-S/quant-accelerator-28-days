# Day 22 resources: broker API, static IP, daily login (checked 1 Nov 2026)

## Official docs (read these, in this order)
- Kite Connect v3, **User / login flow**: request_token → checksum → access_token; tokens expire 06:00 next day. https://kite.trade/docs/connect/v3/user/
- Kite Connect v3, **Exceptions and rate limits**: TokenException = re-login; order placement 10 req/s, 400 orders/min, 5,000 orders/day per user. https://kite.trade/docs/connect/v3/exceptions/
- Kite Connect v3, **Orders** (read the market_protection section: API market orders without it are rejected since Apr 2026). https://kite.trade/docs/connect/v3/orders
- Zerodha support, **Kite Connect API FAQs**: Personal (free: orders, GTT, portfolio, no market data) vs Connect (₹500/month per API key: + WebSocket + historical candles); up to two static IPs (one primary, one secondary). https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/kite-connect-api-faqs
- Zerodha support, **Static IP**: https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip
- Kite forum, "Revising Kite Connect fees from ₹2000 to ₹500 per month" (May 2025; Zerodha staff confirm the static IP is only needed for order place/modify/cancel). https://kite.trade/forum/discussion/15015/revising-kite-connect-fees-from-2000-to-500-per-month
- Kite forum, "How to keep the API running" (Sep 2026): manual login once a day is an exchange requirement; Zerodha does not support automating it. https://kite.trade/forum/discussion/16226/how-to-keep-the-api-running

## Code
- **pykiteconnect** (official Python client, MIT): https://github.com/zerodha/pykiteconnect. Check that your pinned version's `place_order()` accepts `market_protection`. Issue #225 (Apr 2026) reports PyPI 5.1.0 lacking it while `main` had it. https://github.com/zerodha/pykiteconnect/issues/225
- Official clients for other languages (Go, C++, Rust…): listed at https://zerodha.com/products/api

## Video
- Zerodha's Kite Connect webinar, linked from the login-flow docs (shows the handshake end to end): https://www.youtube.com/watch?v=9vzd289Eedk

## Cloud and static IP
- AWS Elastic IP addresses (what survives stop/start, how to attach): https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html
- AWS public IPv4 pricing ($0.005/hour per address, in use or idle, since 1 Feb 2024): https://aws.amazon.com/vpc/pricing/ and the free-tier note (750 h/month for 12-month free-tier EC2 accounts): https://aws.amazon.com/about-aws/whats-new/2024/02/aws-free-tier-750-hours-free-public-ipv4-addresses

## Regulation (already in Day 21, re-read the API part)
- SEBI circular, 4 Feb 2025 (static IP, 2FA, OPS threshold): Day 21 kit, `02_regulation_and_cases`.

## Build-along (03_build_along), 9 tests pass, no network needed
- `bootstrap_vm.sh`: hardens a fresh Ubuntu 24.04 VM: IST + NTP, ufw (SSH only from your laptop), fail2ban, key-only SSH, `trader` user, venv, secrets dir.
- `kite_session.py`: the daily manual login through an SSH tunnel (no public web server), token saved 0600 with its 06:00 expiry, `status` command.
- `preflight.py`: 8 go/no-go checks every morning (egress IP = whitelisted IP, clock, timezone, token, profile, funds, instrument, disk).
- `test_day22.py`: every check proven able to fail, using a fake Kite client.
