# Day 5: 10 problems on overfitting
Rules as always: gut guess → worked answer → one-line trading implication. Solutions after all 10.
Handy: a zero-skill strategy's annual Sharpe over y years is roughly Normal(0, 1/y). t-stat ≈ annual Sharpe × √years.
Expected max of N standard normals: N=10 → 1.57, N=20 → 1.90, N=100 → 2.53.

1. **Twenty tests.** You test 20 useless strategies, each at the usual 5% significance level. What's the chance at least one looks "significant"?

2. **t from Sharpe.** A backtest shows annual Sharpe 0.8 over 5 years. What's its t-stat? How many years would it need to reach t > 3 (Harvey, Liu & Zhu's bar)?

3. **Luck's Sharpe.** You try 100 zero-skill variants on 19 years of NIFTY. What's the expected best Sharpe? On just 5 years of data?

4. **MinBTL.** You want the best of your 20 ideas to be unlikely to show a fake Sharpe of 1.5. How many years of data do you need? For 10 ideas and a target of 1.0?

5. **Bonferroni.** With 20 tests and an overall 5% false-alarm budget (two-sided), what z-score (t-stat) must a single strategy clear?

6. **The haircut.** A strategy shows Sharpe 1.0 over 10 years, and the researcher admits trying 50 variants. Use a Bonferroni correction to find the "haircut" Sharpe. What % of the Sharpe disappears?

7. **What deflates the Sharpe?** Name the four things the Deflated Sharpe Ratio takes into account besides the Sharpe itself. For each, say whether more of it makes DSR go up or down.

8. **Correlated trials.** You test SMA crossovers with slow length 190, 195, 200, 205, 210. Is that 5 trials? 1 trial? Why does it matter for DSR?

9. **Counting honestly.** Over a week you: tried 3 lookbacks, on 4 ETFs, then "fixed a bug" and reran everything, then also tried the whole thing with and without a stop-loss. How many trials go in the log?

10. **The peeked holdout.** You kept 2022–2026 as out-of-sample. Your strategy failed it, so you tweaked one parameter and it passed. What's the status of 2022–2026 now, and what has the "pass" proved?
