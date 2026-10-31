# Solutions. Don't open until all 10 are attempted.

1. 1 − 0.95^20 = **64%**. *If you test 20 ideas, a "significant" one is more likely than not, even when all of them are junk.*

2. t ≈ 0.8 × √5 = **1.79** (not even t > 2). For t > 3: √y > 3/0.8 = 3.75, so y > **14 years**. *A good-looking Sharpe on a short history proves very little. This is why the plan demands t > 3.*

3. 2.53/√19 ≈ **0.58** on 19 years. On 5 years: 2.53/√5 ≈ **1.13**. *Shorter data makes luck look better. A Sharpe above 1 from 100 tries on 5 years is exactly what pure noise produces.*

4. (1.90/1.5)² ≈ **1.6 years** for 20 ideas at 1.5; (1.57/1.0)² ≈ **2.5 years** for 10 ideas at 1.0. Note these are minimums for not being *expected* to see that Sharpe; they're no guarantee. *More trials means you need more data. Fix your grid small BEFORE looking.*

5. α = 0.05/20 = 0.0025 overall, two-sided, so z > Φ⁻¹(1 − 0.00125) ≈ **3.02**. *With 20 tries, t > 3 isn't paranoia: it's just the honest bar.*

6. t = 1.0 × √10 = 3.16, single-test p ≈ 0.0016. Bonferroni: × 50 = 0.078. That p corresponds to z ≈ 1.76, so haircut Sharpe ≈ 1.76/√10 ≈ **0.56**: about **44% gone** (Harvey & Liu's method gives haircuts of this order; Bonferroni is the harshest version). *Discount every backtest Sharpe by how many tries it took. Most published ones need about half off.*

7. (a) **Number of trials N:** more trials raise the benchmark, so DSR **down**. (b) **Variance of Sharpe across trials:** more spread raises the benchmark, so **down**. (c) **Sample length T:** longer means more reliable, so **up**. (d) **Skewness and kurtosis:** negative skew or fat tails widen the uncertainty, so **down**. *A short, fat-tailed, heavily-searched backtest gets crushed by DSR. Good.*

8. Neither exactly. They're highly correlated, so the **effective** number of independent trials is closer to 1–2 than 5. DSR handles this partly through the *variance* of Sharpe across trials (correlated trials have similar Sharpes). But don't game it: if you tried 5, write 5 in the log, and let the maths decide. *Count every trial; argue about correlation later, with evidence.*

9. First run: 3 × 4 = 12. Rerun after the bug fix: another 12 (you saw the first 12, so they count, flagged as "pre-fix"). With and without stop-loss doubles the fixed set: 12 more. Total **36 trials**. *Your trial log is the only defence against fooling yourself. That's why we started it on Day 1.*

10. 2022–2026 is now **in-sample**: you used it to choose a parameter. The "pass" proves only that a parameter exists that fits that period, which is always true. You now need **new** data (or a paper-trading period) as out-of-sample. *A holdout can be used exactly once. Peek and it's gone.*
