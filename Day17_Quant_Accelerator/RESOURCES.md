# Day 17 resources (checked 31 Oct 2026). ✅ = in this ZIP

## Papers (01_papers)
- ✅ Ledoit & Wolf (2008), "Robust Performance Hypothesis Testing with the Sharpe Ratio," *Journal of Empirical Finance* 15(5) (author-hosted). Why textbook Sharpe tests fail with fat tails and autocorrelation; studentized time-series bootstrap instead.
- Politis & Romano (1994), "The Stationary Bootstrap," *JASA* 89(428), DOI 10.1080/01621459.1994.10476870 (paywalled; read the arch docs below for the method; `is_report.py` implements it in 10 lines)
- Politis & White (2004), "Automatic Block-Length Selection for the Dependent Bootstrap," *Econometric Reviews* 23(1) (the rule behind `optimal_block_length`)
- Magdon-Ismail & Atiya (2004), "Maximum Drawdown," *Risk* 17(10): how expected max DD scales with years and Sharpe. SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=874069

## Already in earlier kits (re-read, not repeated)
- Lo (2002), "The Statistics of Sharpe Ratios": Day 2 / Day 11 kit. Re-read the serial-correlation section.
- Bailey & López de Prado: PSR (2012) and Deflated Sharpe (2014): Day 5 kit. Today you produce DSR's inputs (N, Sharpe variance).
- Faber (2007) and the Chan ch. 1 replication: Day 9. Pre-registration: Day 12.

## Videos
- StatQuest, *Bootstrapping Main Ideas!!!* (~10 min): https://www.youtube.com/watch?v=Xz0x-8-cgaQ
- StatQuest, *The Standard Error, Clearly Explained!!!*: https://www.youtube.com/watch?v=XNgt7F6FqDU
- StatQuest, *Using Bootstrapping to Calculate p-values!!!*: https://www.youtube.com/watch?v=N4ZQQqyIf6k

## Docs, code, courses
- Kevin Sheppard's `arch` package, bootstrap examples (Sharpe ratio CI with the stationary bootstrap): https://bashtage.github.io/arch/bootstrap/bootstrap_examples.html · confidence-interval methods: https://bashtage.github.io/arch/bootstrap/confidence-intervals.html · GitHub: https://github.com/bashtage/arch
- OECD SDMX data API (the cash series): https://sdmx.oecd.org · RBI DBIE (the series to switch to): https://data.rbi.org.in

## Build-along (03_build_along), all run and tested here
- `is_report.py`: hash-checked pre-reg → aligned runs of the full grid → bootstrap bands → years/regimes → trial accounting → `IS_report.md` + charts + manifest. ~10 s.
- `test_is_report.py`: 6 tests (bootstrap indices, effective N, hand-checked DD, warm-up alignment, gate, and the shared-state bug).
- `crosscheck_arch.py`: my bootstrap vs `arch`, same 90% band (−0.32 to +0.64).
- `is_out/`: the demo report generated on the index stand-in.
