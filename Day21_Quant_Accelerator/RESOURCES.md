# Day 21 resources: the rulebook (checked 1 Nov 2026). ✅ = in this ZIP

## Regulation and real failures (02_regulation_and_cases)
- ✅ **SEBI circular, 4 Feb 2025, "Safer participation of retail investors in Algorithmic trading"** (SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/0000013, 6 pp). API access only via a unique key + static IP + 2FA; registration needed above a broker-set orders-per-second threshold; brokers keep a kill switch. Page: https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html
  - Went live **1 April 2026** after extensions (Livemint, 1 Apr 2026: https://www.livemint.com/market/stock-market-news/sebi-algo-trading-norms-kick-in-today-2fa-audit-trails-for-brokers-now-mandatory-11775022862982.html)
  - Zerodha's plain-English read of the NSE implementation standards: individuals under **10 orders/second** per segment per exchange need no registration, just a static IP tied to the API key. https://zerodha.com/z-connect/general/a-comprehensive-overview-of-nses-circular-on-the-new-retail-algo-trading-framework
- ✅ **SEC order against Knight Capital (16 Oct 2013, Release 34-70694)**, 10 pp. 45 minutes, millions of erroneous orders, ~$460M lost. No check comparing orders sent with orders intended, no automated kill, and a dead flag reused. Read paragraphs 1–30. Each failure maps to a check in `risk_engine.py`.
- ✅ **FIA, *Best Practices for Automated Trading Risk Controls and System Safeguards*** (July 2024, 22 pp). The industry checklist: pre-trade limits, price bands, max order size, kill switches, post-trade reconciliation. Read section 1.

## Papers (01_papers)
- ✅ Bailey & López de Prado (2015), "Stop-Outs Under Serial Correlation and 'The Triple Penance Rule'," *J. of Risk* 18(2) (author copy). Recovery takes ~3× as long as the fall; low-Sharpe strategies can stay under water for decades. Read sections 1–3 and 6.
- ✅ Van Hemert, Ganz, Harvey, Rattray, Sánchez Martin & Van Hemert (2020), "Drawdowns," *JPM* (Duke copy). Max drawdown is mostly a function of Sharpe and track length, not skill. How deep a drawdown should look, before you panic.

## Already in earlier kits (re-read, not repeated)
- Thorp (2006) Kelly chapter; MacLean, Thorp & Ziemba (2010): **Day 3**. Today's `kelly_report()` is that chapter applied to your numbers.
- Carver, "How much risk should we take?" and the Kelly posts: **Days 3 and 15**.

## Blogs (free)
- Rob Carver, "Random data: Evaluating 'Trading the equity curve'" (2015): why switching a system off after losses usually hurts. It's the reason your loss limits HALT and don't liquidate. https://qoppac.blogspot.com/2015/11/random-data-evaluating-trading-equity.html
- Rob Carver, "When endogenous risk management isn't enough: a simple risk overlay" (2020): https://qoppac.blogspot.com/2020/05/when-endogenous-risk-management-isnt.html
- SEC press release on Knight (1-page summary): https://www.sec.gov/newsroom/press-releases/2013-222

## Videos (light block)
- "the worst trading algorithm ever created" (2026): a clear walk-through of Knight's SMARS router and what failed. https://www.youtube.com/watch?v=IQ8Giwy8qmE
- "The $440 Million Software Bug That Destroyed Knight…": shorter post-mortem. https://www.youtube.com/watch?v=YpwvXXl-r8s

## Build-along (03_build_along), run and tested here (15 tests pass)
- `rulebook.json`: your rules as data (hashed). DRAFT values; replace them with yours.
- `risk_engine.py`: `pre_trade_check()` (16 reasons an order must not go out), `end_of_day()` (HALT vs KILL), `target_weight()` (1.0× cap), `kelly_report()`, `triple_penance()`. The Day 23 pipeline calls these.
- `limits_calibrator.py`: how often each loss limit would fire **while the strategy is working as backtested** (4,000 resampled years), plus Kelly and the rupee size of your kill limit → `limits_out/limits_report.md`.
- `test_risk_engine.py`: every rule proven able to say no.
