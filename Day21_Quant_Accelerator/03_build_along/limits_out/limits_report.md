# Limits calibration (in-sample, strategy working as backtested)

Rulebook v1-DRAFT sha256 67a383968098c2e4 · IS Sharpe xs cash 0.18 · vol 14.2% · backtest max DD -25.6% · 4000 one-year resampled paths

## False-alarm rates of candidate limits

| limit             | level                | P(fires within 1 year | strategy working as backtested)   |
|:------------------|:---------------------|:----------------------------------------------------------|
| daily loss halt   | 3%                   | 41.5%                                                     |
| daily loss halt   | 4%                   | 24.1%                                                     |
| daily loss halt   | 5%                   | 18.5%                                                     |
| daily loss halt   | 6%                   | 0.0%                                                      |
| daily loss halt   | 8%                   | 0.0%                                                      |
| monthly loss halt | 8%                   | 20.6%                                                     |
| monthly loss halt | 10%                  | 6.0%                                                      |
| monthly loss halt | 12%                  | 1.2%                                                      |
| monthly loss halt | 15%                  | 0.1%                                                      |
| monthly loss halt | 20%                  | 0.0%                                                      |
| kill drawdown     | 1.0× backtest = 26%  | 1.1%                                                      |
| kill drawdown     | 1.25× backtest = 32% | 0.1%                                                      |
| kill drawdown     | 1.5× backtest = 38%  | 0.0%                                                      |
| kill drawdown     | 2.0× backtest = 51%  | 0.0%                                                      |

**Your rulebook's limits:** daily 6.0% → 0.0%/yr · monthly 12.0% → 1.2%/yr · kill at 1.5× backtest DD → 0.0%/yr

Caveat: a bootstrap can't invent a day worse than the worst in history (strategy's worst day here: -5.9%). A 0.0% at levels beyond that means 'never seen', not 'impossible'.

Rule of thumb: HALT limits may false-fire ~5–15% of years (a halt costs a review, not money). The KILL limit should false-fire well under 5% a year.

## Kelly (diagnostic, not the sizing rule)

Full Kelly at the point Sharpe: 1.23× · half Kelly 0.62× · at the lower 90% Sharpe: 0.00×

Kelly at the lower bound is 0: the edge is unproven, so size by RISK BUDGET (money you can lose), not by edge.

## Triple penance (Bailey & López de Prado 2015)

At SR 0.18 and vol 14.2%: 95%-quantile worst loss ≈ 55%, reached after ≈ 22 years; recovery can take ≈ 88 years under water.
That's why the retirement rule here is drawdown- and plumbing-based, not time-based: at a low Sharpe, time under water says almost nothing.

## What the kill limit means in rupees

Capital at risk ₹20,000 → the kill limit fires after about **₹7,678** of drawdown. Can you lose that and still follow the rules? If not, lower the capital, not the limit.