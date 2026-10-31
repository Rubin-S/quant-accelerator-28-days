# DAY 6: Thu 5 Nov 2026
## Microstructure: the order book, the spread, adverse selection, slippage

Until today, a "price" was one number in a CSV. Today you learn it's a fight between two queues of orders, and that every trade you make has someone on the other side who chose to trade with you.

Two ideas to take away from today:
1. **The spread exists because some traders know more than the market maker** (Glosten–Milgrom). It's the fee for the risk of trading with them.
2. **The price you see is not the price you get.** Spread, queue position, impact and missed fills sit between your backtest and your bank account.

You'll prove idea 1 by building a market maker that loses money for exactly this reason. You'll use idea 2 to write your first cost model.

**Deliverable (from the plan):** a naive market maker that loses, and why = `naive_mm_lab` run (predictions first) + its session replayed through YOUR C++ orderbook + the 10 problems + `cost-model-template.md` started.

---

## Your day (about 6 h; deep work about 4 h)

| Time | Block | What | Files |
|---|---|---|---|
| 30 min | Drill | Zetamac + market-making game, 5 rounds. Today, while you play: notice when you got picked off. | |
| 75 min | Deep 1: Read | **Glosten & Milgrom (1985)**: sections 1–3, the model only. Then **Hasbrouck's notes**: the chapters on the Roll model and sequential trade models. **Avellaneda–Stoikov (2008)**: sections 1–3 (reservation price, optimal spread). | 01_, 02_ |
| 90 min | Deep 2: Lab | Fill `prediction-sheet.md` → run `naive_mm_lab.py` → answer its 5 questions. | 06_build_along/ |
| 45 min | Deep 3: Your C++ book | Replay `naive_mm_session.csv` through `orderbook_replay`, then run `pnl_from_replay.py`. Does your engine's P&L agree with the sign and rough size the Python lab predicts? If not, find out why. | 06_build_along/ |
| 45 min | Deep 4: Problems | The 10 problems. Then fill as much of `cost-model-template.md` as you can from REAL sources (your broker's charges page). | 07_, 08_ |
| 45 min | Light | Video: UCPH *Financial Markets Microstructure*, lectures 1 and 2, plus the Glosten–Milgrom lecture. Skim the NSE pre-open FAQ (in the ZIP) and the market timings page. | RESOURCES.md, 04_ |
| 15 min | Review | Training log row | |

**Setup:** `pip install numpy pandas matplotlib scipy`.

About the C++ replay: I wrote the session CSV in exactly the format your README specifies (`ADD,id,BUY|SELL,price,qty,GTC|IOC` and `CANCEL,id`; prices in integer ticks of ₹0.01). I couldn't compile your engine in my sandbox, so **you** are the first test. If something rejects, that's a free bug hunt. Some `CANCEL` lines will hit already-filled quotes and print `NOT_FOUND`: that's expected.

---

## What to pull from each reading
- **Glosten–Milgrom:** bid = E[value | someone sells to me]; ask = E[value | someone buys from me]. The spread is pure information cost, even with zero fees.
- **Kyle (1985):** skim the intro only. An informed trader hides inside noise trading; λ ("Kyle's lambda") is how much the price moves per unit of order flow.
- **Roll (1984):** bid-ask bounce creates negative autocorrelation in price changes. That's why short-horizon "reversal" in daily closes can be fake.
- **Avellaneda–Stoikov:** skew your quotes against your inventory. Inventory is risk you get paid nothing for.
- **Gould et al. (2013):** the survey of how limit order books actually behave. Read sections 1–3.
- **NSE documents:** how the 9:00–9:15 pre-open call auction sets the open, plus the order types and price bands. Your future strategy trades inside these rules.

---

## Mentor's rules for Day 6
1. **You are the one crossing the spread, not the market maker.** Every assumption of a "free" fill is a lie until proven otherwise.
2. **Judge fills by markouts,** meaning where the price goes after, not the price you got.
3. **Cost numbers come from sources, never memory.** Run every backtest at a low and a high cost case.
4. **A trade "at the open" happens in an auction.** Don't backtest as if you got the open price for free.

Send me: lab predictions vs actuals, the 5 lab answers, your C++ replay P&L (and any bugs you found), the 10 problems, and cost model v0.
