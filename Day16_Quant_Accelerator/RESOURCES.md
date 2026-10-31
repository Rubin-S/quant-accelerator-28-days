# Day 16 resources (checked 31 Oct 2026). ✅ = in this ZIP

## Papers (01_papers)
- ✅ Just, Jalali, Inozemtseva, Ernst, Holmes & Fraser (2014), "Are Mutants a Valid Substitute for Real Faults in Software Testing?" FSE (ACM SIGSOFT Distinguished Paper): 357 real faults; mutant detection correlates with real-fault detection, independent of coverage.
- ✅ Jia & Harman (2011), "An Analysis and Survey of the Development of Mutation Testing," IEEE TSE 37(5): the mutation operators `mutate.py` uses.
- ✅ Papadakis, Kintis, Zhang, Jia, Le Traon & Harman (2019), "Mutation Testing Advances: An Analysis and Survey," *Advances in Computers* 112 (accepted version, UCL): reference only, skim sec. on equivalent mutants.

## Free book and course readings
- Andreas Zeller, *The Debugging Book* (free online): https://www.debuggingbook.org/. Start with "Introduction to Debugging": https://www.debuggingbook.org/html/Intro_Debugging.html · Delta debugging: https://www.debuggingbook.org/html/DeltaDebugger.html
- MIT 6.031, Reading 13: Debugging (reproduce, localise, scientific method): https://web.mit.edu/6.031/www/fa21/classes/13-debugging
- Stuart Halloway, "Debugging with the Scientific Method" (Clojure/conj 2015), transcript: https://github.com/matthiasn/talk-transcripts/blob/master/Halloway_Stuart/DebuggingWithTheScientificMethod.md · video: https://www.youtube.com/watch?v=FihU5JxmnBg

## Tools
- mutmut (industrial Python mutation testing): https://github.com/boxed/mutmut
- cosmic-ray: https://github.com/sixty-north/cosmic-ray
- git bisect docs: https://git-scm.com/docs/git-bisect
- Hypothesis: https://hypothesis.readthedocs.io

## Earlier kits, not repeated
- Day 14: look-ahead papers, the perturbation test. Day 15: engine design, QuantStart series, vol-targeting papers.

## Build-along
- `03_bug_hunt/engine.py` (v2.1, 3 planted bugs) + `test_engine.py` (Day 15 suite) + `nse_costs.py`
- `04_mutation_lab/mutate.py`: 80-line mutation tester, tested here; baseline 57% on the clean Day 15 engine
- `SEALED_answer_key.zip`: answer key + 3 reference tests (password after your report)
