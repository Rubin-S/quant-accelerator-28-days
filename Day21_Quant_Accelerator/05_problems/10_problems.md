# Day 21: 10 problems
1. Full Kelly at the point Sharpe is ~1.23×, but 0 at the lower 90% bound. Which do you size from, and why does the house cap of 1.0× make the question almost moot here?
2. A 3% daily-loss halt would false-fire in ~41% of years. Why is a limit that fires that often worse than no limit at all?
3. The calibrator says a 6% daily halt fires 0.0% of the time. Why is that number untrustworthy? (Hint: what's the worst day in the sample?)
4. Why do the loss limits HALT instead of liquidate? What would a "liquidate on −6% days" rule really be?
5. Triple penance: at SR 0.18 the 95% worst loss could take ~88 years to recover. What does that say about a "retire after 2 bad years" rule?
6. Map three Knight Capital failures (from the SEC order) to three checks in `pre_trade_check()`.
7. SEBI: under what condition would your bot need exchange registration? How far below it are you?
8. Your broker shows 70 units; your book says 0. List the first five things you do, in order.
9. You're down 14% this month and the decision day says "stay long". The rulebook says HALT at 12%. What happens to the existing position, and what happens on decision day?
10. You want to raise capital at risk after a good month. Write the amendment exactly as the rulebook requires, and list what must happen before it takes effect.
