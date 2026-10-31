# RULEBOOK: <strategy name> v1
Signed: ______________ Date/time (IST): ______________
rulebook.json sha256: ______________ (from `sha256sum rulebook.json`)

## 1. What I trade
- Instrument(s): NIFTYBEES only (NSE, cash segment, delivery). Long or flat. No F&O, no shorting, no margin.
- Signal: pre-registered Faber 10m on NIFTY 50 closes, decided on the first NSE session of each month from month-end closes up to the previous session.
- Holdout verdict (Day 20) attached: claims kept = ______; claims dropped = ______.

## 2. How much
- Capital at risk: ₹______. Money I can lose entirely without changing my life or my studies. (The kill limit fires near ₹______ of drawdown; see limits_report.md.)
- Max gross exposure: 1.0× (house rule since Day 3). No borrowing, ever.
- Sizing: signal × 1.0. Vol targeting: OFF (it would be a new trial). Kelly: diagnostic only (lower-bound Kelly = ____).

## 3. How I trade
- Orders: LIMIT only, within ±1% of LTP; window 09:30–15:00 IST; max 4 orders/day; never at the open's first prints (Day 14).
- If unfilled by 15:00: (pick one, write it, test it) ______
- Static IP + 2FA per SEBI (4 Feb 2025 circular, live 1 Apr 2026). Far under 10 orders/second.

## 4. Stops
| Type | Trigger | Action | Who can reset |
|---|---|---|---|
| HALT | daily loss ≥ __% | no new orders, keep position, write incident note | me, after the note |
| HALT | month-to-date loss ≥ __% | no new orders until a written review | me + mentor |
| HALT | stale data > 15 min, position mismatch, 2 rejects, duplicate order id | stop, reconcile with broker, note | me, after reconciling |
| KILL | drawdown from live peak ≥ __× backtest max DD (= __%) | flatten, retire, full review | nobody for 30 days |
| KILL | file `KILL` exists on the server | flatten, stop | whoever created it |

## 5. No-override clause
- I won't change a rule, skip a signal, or "wait a day" because of news, gut, or P&L.
- Amendments: written here with date and reason, 48-hour cooling-off, never during market hours, new sha256, logged in trial-log if they change the rule.
- Breaking a rule benches me for a week, even if the trade made money.

## 6. Retirement rule (when this strategy stops for good)
- Any KILL trigger, or
- the pre-registered falsifier fails on 3 years of live data, or
- the instrument changes (NIFTYBEES delisted/merged, a big jump in tracking error), or
- 3 plumbing incidents in a month.
Not a retirement reason: a year of underperforming buy & hold (expected; see triple penance).

## 7. Daily and monthly routine
- Daily: 15:35 IST check fills vs intended, broker vs book positions, log. 5 minutes.
- Monthly: decision day + a 1-page review: rule adherence first, P&L last.
