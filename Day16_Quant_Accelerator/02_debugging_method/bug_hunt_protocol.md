# Bug-hunt protocol (scientific debugging, after Zeller's *Why Programs Fail* ch. 6 and MIT 6.031 Reading 13)

**Rule 0: don't diff against Day 15** until your report is in. In real life there's no clean copy to diff against.

## Loop (write every step in `bug-hunt-log.md`)
1. **Observe**: run the suite and the demo. Write down every failure AND anything that merely looks odd (trade counts, interest, targets).
2. **Hypothesise**: one specific, falsifiable claim: "the sizer reads bar t+1".
3. **Predict**: "if true, changing ONLY price t+1 changes the weight at t".
4. **Experiment**: the smallest test that can prove you wrong. Change one thing at a time.
5. **Conclude**: confirmed → write the failing test FIRST, then fix, then see it go green. Refuted → new hypothesis.

## Where bugs hide in a backtester (hunt in this order)
| Class | Ask | Instrument |
|---|---|---|
| Look-ahead | Can any line reach data after t? Check every slice, every `_df`, every `shift`, `bfill`, `resample` | perturb ONLY bar t+1, with the strategy IN the market |
| Order of operations | What happens first each bar: interest, fill, mark, decide? Does it match the timeline in real life? | a one-trade scenario where you compute the answer by hand |
| Risk limits | Is the limit enforced on the TARGET or only on what happened to fill? | assert on `targets`, not just `weights` |
| Accounting | Does cash + units × price add up? Are costs on the right side? | ledger identity, hand-computed round trip |
| Silent masking | Is one rule hiding another rule's failure? | turn the masking rule off and re-test |

## Tools
- `git bisect` when you have a good and a bad commit (not today: today it's reasoning)
- `python -m pdb` / `breakpoint()` at the bar where behaviour changes
- `04_mutation_lab/mutate.py` to measure what your suite is blind to
