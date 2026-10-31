# Day 19 resources: stress testing (checked 1 Nov 2026). ✅ = in this ZIP

## Papers
- ✅ Hoffstein, Faber & Braun (2020), "Rebalance Timing Luck: The (Dumb) Luck of Smart Beta" (22 pp; SSRN 3673910, open copy via Epsilon Theory). Same rule, different rebalance day, results 100+ bps apart. That's stress S3. Read the intro, section 2 and the conclusion.
- ✅ Novy-Marx & Velikov (2016), "A Taxonomy of Anomalies and Their Trading Costs," *RFS* 29(1) (NBER WP 20721). Turnover decides whether costs kill a strategy. Your rule trades ~11 times in 10 years, which is why S1 barely moves it. Read the intro + section on the buy/hold spread (it's your band from Day 15).
- Hoffstein, Sibears & Faber (2019), "Rebalance Timing Luck: The Difference between Hired and Fired," *J. Index Investing* 10(1), DOI 10.3905/jii.2019.1.070. Derives the timing-luck formula and the fix (tranching). Paywalled; the Newfound summary page below covers it.
- Timothy Masters, *Permutation and Randomization Tests for Trading System Development* (2020, book, not free): the reference for S7. The neurotrader video below teaches the core idea free.

## Already in earlier kits (re-read, not repeated)
- Frazzini, Israel & Moskowitz, *Trading Costs*: Day 7. Your costs ×2/×3 should be judged against real NSE costs from `nse_costs.py`.
- Politis & Romano stationary bootstrap / Politis & White block length: Day 17 (`is_report.py`). S8 reuses it.
- Hansen SPA, Bergmeir et al.: Day 18. Aronson, *Evidence-Based TA*: Day 5.

## Videos
- neurotrader, "How I Develop Trading Strategies | Permutation Tests and Trading Strategy Development with Python": in-sample excellence → in-sample permutation test → walk-forward → walk-forward permutation. https://www.youtube.com/watch?v=NLBXgSmRBgU
- (Re-watch the Pardo Part II segment on robustness from Day 18 if you skipped it.)

## Blogs and guides (free)
- Newfound Research, "Rebalance Timing Luck" hub (all their papers + plain-English summary): https://www.thinknewfound.com/rebalance-timing-luck
- Newfound, "The Dumb (Timing) Luck of Smart Beta" (2019 blog version): https://blog.thinknewfound.com/2019/11/the-dumb-timing-luck-of-smart-beta
- Newfound, "Timing Luck and Systematic Value" (case study on their own fund, honest about it): https://blog.thinknewfound.com/2019/07/timing-luck-and-systematic-value

## Code
- neurotrader888/mcpt (MIT): bar-permutation Monte Carlo tests, in-sample and walk-forward. Read `bar_permute.py`; compare its null (shuffle the market) with S7's null (shuffle your timing). https://github.com/neurotrader888/mcpt
- `arch` bootstrap docs (S8's engine, cross-checked on Day 17): https://bashtage.github.io/arch/bootstrap/bootstrap.html

## Build-along (03_build_along), run and tested here
- `stress.py`: 8 stress families (S1–S8) on the pre-registered rule, with your falsifier lines → `stress_out/stress_report.md` + 3 charts. ~13 s.
- `test_stress.py`: 6 tests (delay shifts exactly k bars, cost scaling, spell detection, drop-best logic). Carried over: Day 17–18 scripts.
