# DAY 1 — Sat 31 Oct 2026
## "Why do most traders lose, and why should anyone pay ME?"

Today's one question: **where does trading money come from?**
If you can't name who is on the other side of your trade and why they agree to lose to you, you have no edge. You have a hobby.

Gate for today: the one-page essay (05_templates/why-should-anyone-pay-me.md), written by you, defended to me.

---

## Your day (about 6 hours, deep work capped near 4)

| Time | Block | What | Files |
|---|---|---|---|
| 30 min | Drill | (1) Zetamac arithmetic, 2 rounds of 2 min, log both scores: https://arithmetic.zetamac.com/  (2) Fermi: SEBI says individuals lost Rs 1,05,603 crore in F&O in FY25. Roughly how much is that per trading day? Per loss-maker? Do it in your head first, then check. | — |
| 30 min | Setup | Run the setup script, create your research repo, copy in the logs | 06_setup/setup_repo.sh, 05_templates/ |
| 90 min | Deep 1: Who loses | Read in this order (see reading guide below) | 01_why_retail_loses/ |
| 90 min | Deep 2: Where edge comes from | Read in this order | 02_sources_of_edge/ |
| 45 min | Deep 3: Build-along | Run who_pays_whom.py, PREDICT before each change, answer the 4 questions | 04_build_along/ |
| 45 min | Deep 4: Essay | Write the one page. No copying phrases from papers. | 05_templates/why-should-anyone-pay-me.md |
| 60–90 min | Light | Videos + optional reading (evening, relaxed) | RESOURCES.md, 03_optional_deeper/ |
| 15 min | Review | Fill training log; send me the essay | training-log.md |

---

## Reading guide (read with a question in your head, not cover to cover)

### Deep 1 — Who loses, and how? (folder 01)
1. **SEBI_2024_FnO_FY22-FY24_press_release.pdf** (3 pages, 10 min). 93% of individual F&O traders lost money over FY22–FY24. *Question: what share of losses was transaction costs?*
2. **SEBI_2024_Intraday_Cash_Study.pdf**, read only "Summary Findings" (pages 9–11, 20 min). 71% of intraday cash traders lost in FY23; 80% of those with 500+ trades a year. *Question: why do frequent traders lose more?*
3. **SEBI_2025_Derivatives_vs_Cash_FY25_losses.pdf**, section C only (5 min). FY25: about 91% lost; net losses Rs 1,05,603 crore.
4. **Barber_Lee_Liu_Odean_2009_Just_How_Much_Lose.pdf** (30 min). Abstract, intro, and the aggressive vs passive orders section. Every trade in Taiwan, 5 years. *Key line: virtually all individual losses come from aggressive orders. Institutions win on both. Why?*
5. **Chague_et_al_2019_Day_Trading_for_a_Living.pdf** (16 pages, 20 min). 97% of Brazilian day traders who kept going 300+ days lost money. No evidence of learning. *Question: if they don't learn, why do they keep going?*
6. Skim abstract + conclusion only: **Barber_Odean_2000_Trading_Is_Hazardous.pdf** (most active traders earned 11.4% vs 17.9% market), **Barber_et_al_Do_Day_Traders_Rationally_Learn.pdf**.

### Deep 2 — Where can edge come from? (folder 02)
1. **Harris_2015_Trading_and_Electronic_Markets_CFA_RF.pdf**, chapters 1–3 only (pages ~1–25, 50 min). Free CFA monograph by Larry Harris, ex-SEC chief economist. The best plain-English map of who trades, why, and who wins. *Write down his taxonomy of traders from memory afterwards.*
2. **Hasbrouck_slides_Private_Information_Treynor_model.pdf** (15 min). The Treynor/Bagehot model in slides: informed traders, liquidity traders, and the dealer in between. This is what your build-along simulates.
3. **AQR_Asness_How_Can_a_Strategy_Still_Work.pdf** (15 min). Cliff Asness on why a known strategy can keep working: it's either a risk you're paid to hold, or a mistake others keep making.
4. **AQR_Understanding_Style_Premia.pdf** (10 min skim). Value, momentum, carry, defensive: each with its risk story and its behavioural story.
5. Evening/optional: **Lo_2004_Adaptive_Markets_Hypothesis.pdf** (sections 1 and 5), **Grossman_Stiglitz_1980** (intro + conclusion only; it proves prices can't be perfectly efficient, or nobody would pay to research), **NBER_Noise_Traders_review.pdf**, **Lo_2007_EMH_Palgrave.pdf**.

### The 3 sources of edge (what you're building toward today)
1. **Risk premium**: you're paid to hold a risk others won't (equity risk, crash risk, illiquidity).
2. **Behavioural**: you profit from predictable mistakes (overreaction, underreaction, overconfidence, the disposition effect).
3. **Structural / informational / service**: you provide liquidity, process information better or faster, or take trades others are forced into or barred from.

Your job today: for each, one real example, and *why it hasn't been competed away*.

---

## The mentor's 3 rules for Day 1
1. **Predict before you run.** Write your guess in the log, then run the code. Grade the guess, not the output.
2. **Log every idea as a trial** from today (05_templates/trial-log.csv). We count how many things you try, because Bailey et al. (2014) show that trying enough variants makes noise look like skill. That paper is in 03_optional_deeper for Day 5.
3. **No trading today.** Not even "just a small one".

Send me the essay when it's done. I'll grade the reasoning, not the writing.
