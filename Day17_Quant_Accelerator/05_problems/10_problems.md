# Day 17: 10 problems
1. Unaligned, the filter's max-DD edge is +34 pp; aligned, +18 pp. Explain the mechanism in two sentences. Which number goes in your report, and why?
2. Primary Sharpe 0.18 with a 90% band of −0.32 to +0.64. B&H 0.19 (−0.34 to +0.74). What can you honestly claim about Sharpe? What can't you?
3. The vol ratio band is 0.56 to 0.81 and never crosses 1. Why is a risk claim so much easier to support than a return claim on the same data?
4. Grid: 8m Sharpe 0.22, 10m 0.18, 12m 0.09. Your primary is 10m. Someone says "switch to 8m". Write your reply in 3 lines.
5. Effective N for the three Faber lengths is 1.15. What does that mean, and which N should DSR use on Day 20: 3, 1.15, or your total trial-log count? Defend it.
6. Faber's longest time underwater (1,289 days) is LONGER than buy & hold's (1,086). How can a filter with half the drawdown sit underwater longer? Why does this matter for you as a human running it?
7. While building `is_report.py` I reused one FaberMonthly object for two runs and got −132 bps of "cost drag" (negative drag: costs made it better). Find the mechanism, and say which test now guards it.
8. The cash rate is flat 6.00% for 2007 to 2012 in the OECD series. How much could a wrong cash leg move (a) CAGR, (b) excess Sharpe, for a strategy that's in cash ~30% of the time? Rough numbers.
9. The Politis-White automatic block length for squared excess returns comes out ~1.6 days; the report uses 20. Which is safer for Sharpe bands, and why might the automatic rule mislead you on a strategy that's flat for months?
10. Write your Day 20 predictions now: the vol-ratio and DD-difference bands you expect on 2019+. Why does writing them today matter?
