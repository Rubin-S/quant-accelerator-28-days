# Day 15: 10 problems
1. Why can't FaberMonthly decide on the last session of the month, even though that's what the paper says?
2. The order holds a target WEIGHT and units are computed at the fill bar's close. What's realistic and what's optimistic about that?
3. Test 5 compares the engine to `(1 + w.shift(2) * r).cumprod()`. Why shift(2) and not shift(1)?
4. Buy & hold shows 2 trades, not 1. Find the second one in the trade log and explain it.
5. Vol targeting made 1,184 trades. Why does an EWMA sizer trade almost daily, and why is a 10% band a reasonable fix?
6. Excess Sharpe: Faber 0.22, Faber + vol target 0.11, yet the vol-targeted drawdown is smaller. Harvey et al. (2018) say vol targeting improves equity Sharpe. Why didn't it here? Give two reasons.
7. The "no costs, cash 0%" row has a 0%-rf Sharpe of 0.50 but the real run has an excess Sharpe of 0.22. Where did the difference go?
8. Which test catches swapping step 1 (interest) and step 2 (fill)? If none, design one.
9. Property-based test 14: what does Hypothesis buy you over 40 hand-picked examples?
10. You like the vol-targeted version's −16.5% max DD. Can you switch to it now? What does the process require?
