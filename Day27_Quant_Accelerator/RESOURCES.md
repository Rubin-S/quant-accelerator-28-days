# Day 27 resources: failure drills (checked 1 Nov 2026)

All free. Read in this order.

## Core reading
1. **Principles of Chaos Engineering** (principlesofchaos.org, last updated March 2019), 10 min. The four-step recipe drills.py follows: define steady state → hypothesis → inject a real-world fault → look for a difference. Plus: minimise blast radius. https://principlesofchaos.org/
2. **Kripa Krishnan, "Weathering the Unexpected"** (ACM Queue vol. 10 no. 9, 16 Sep 2012), 20 min. Google's DiRT disaster-recovery drills. Best lines for you: only one person found the emergency plan on the first drill; "copious documentation on how something should work doesn't mean anyone will use it". Read Limoncelli's sidebar (a drill seen from the person being tested). https://queue.acm.org/detail.cfm?id=2371516
3. **Google SRE Book ch. 17, "Testing for Reliability"** (Perry & Luebbe), 30 min. Opens with "If you haven't tried it, assume it's broken." Read: "tests that are failing generally prove the absence of reliability", turning every bug into a test, and the break-glass section. https://sre.google/sre-book/testing-reliability/
4. **Google SRE Book ch. 13, "Emergency Response"**, 15 min: what to do when the drill is real. https://sre.google/sre-book/emergency-response/

## The broker side (what your fakes imitate)
- **Kite Connect, "Exceptions and errors"**: TokenException (403, session expired: log in again), NetworkException (can't reach the OMS), MarginException, HoldingException, InputException, OrderException; HTTP 429/502/503/504; limits of 10 orders a second, 400 a minute, 5,000 a day, and 25 modifications per order. https://kite.trade/docs/connect/v3/exceptions/
- Zerodha Console kill switch: disables a segment, can only be re-enabled after 12 hours (Day 24 kit).

## From earlier kits (not repeated)
Knight Capital SEC order (Day 21), the kill.py / recovery.py design (Day 24), postmortem templates (Day 25), live-vs-backtest diff (Day 26).

## Build-along (03_build_along): 49 tests pass, plus 2 marked "expected to fail" (your bugs)
- `drills.py`: 12 code drills against your real pipeline, run in temp folders with Kite-shaped fake brokers: kill file, kill.py cancel and flatten, connection lost before or after the send, rejection, missing data, stale preflight, expired token, disk full, double run, a manual trade.
- `test_day27.py`: every drill as a test, a check that the harness itself catches a broken kill switch, and **2 strict-xfail bugs the drills found**.
