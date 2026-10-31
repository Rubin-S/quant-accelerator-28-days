# Day 16: 10 problems (do AFTER the hunt)
1. The 3 bugs together moved the excess Sharpe from 0.121 to 0.122. What does that tell you about finding bugs by looking at results?
2. A perturbation test passed at t=250 and t=400 but failed at t=520 on the same leaky engine. How can that happen, and how do you make the test reliable?
3. Your risk-limit test checks the HELD weight. Why is that weaker than checking the TARGET? Give the live-trading scenario where it matters.
4. Define an "equivalent mutant". Give one from the baseline and explain why no test could ever kill it.
5. Just et al. (2014) found mutant detection correlates with real-fault detection, even after controlling for coverage. Why is coverage alone a weak measure? Give an engine line that's 100% covered and still wrong.
6. 18 survivors sit in `metrics()`. Write one test that kills at least 10 of them (hint: a hand-computable equity curve).
7. The holdout-seal mutant `>= → >` survives. Write the 3-line test. Why is this the most expensive survivor in the whole engine?
8. Scientific debugging: write the hypothesis → prediction → experiment for "interest is accrued on the wrong cash balance".
9. When is `git bisect` the right tool, and why wasn't it useful today?
10. After today, what's your rule for every future engine change?
