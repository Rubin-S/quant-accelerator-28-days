# Solutions
1. Both had dated incident notes, so they're documented events, not silent breaches. Abuse: writing a lazy note just to turn the count green. The note must name a cause and a fix. *Documentation is not an excuse.*
2. Actions need a human, a reason and a log. kill.py and the runbook give that; a web button gives one-click mistakes and a new attack surface. *Show on one surface, act on another.*
3. A halt means the system already decided to stop; hiding it behind "data stale" could make you fix the data and restart without reading why it halted. *Show the most severe truth first.*
4. Fri 20 → Mon 23 is 3 days; Mon 23 → Wed 25 (Tue holiday) is 2. A 4-day gap only happens on long weekends with a Friday or Monday holiday, and then it rightly asks you to check. Fine; adjust if the NSE calendar has 3-day closures. *Thresholds come from the calendar, not vibes.*
5. No: one fill, and the "decision close" is yesterday's price; the market moved. Shortfall means something only over many fills, compared with the backtest's 5 bps slippage. *One data point is an anecdote.*
6. A rule change. It changes the tested behaviour (Day 15 timing), so it needs the rulebook amendment process, a pre-registered trial and replay parity again. *If it changes trades, it's not a bug fix.*
7. "It's a week of a strategy that trades twice a year. That number is noise; I'm grading whether it did what the rules said." *Judge process, not P&L.*
8. Because the habit is the control: if drills skip notes, real CRITs will too, and the C7 check exists to catch exactly that. *Train the way you'll fight.*
9. C8 (orders without a decision) and C4 (a guard that logs but doesn't block): Knight's dormant code sent orders nobody decided on, and its warnings didn't stop anything. *Check intent against action.*
10. Examples: that the Kite app shows the same holdings (outside your system); that the NSE holiday list is right for next week; that nobody else has your api_secret. *Some truths live outside your logs.*
