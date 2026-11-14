# Judge critique (Track 3, skeptical)

## Scores

- **Impact & Innovation: 3.** It audits a shipped reflection tool and finds a real flaw: the production prompt suppresses stated changes of mind, which the "change of mind" card depends on. Track 3's own question, whether users later endorse what it flags, goes unmeasured.
- **Execution: 4.** Rigorous for a weekend: a cross-family test set, blind labels (kappa 0.986), a validated judge, exact paired tests and a frozen fix. But n is small and several arms sit at ceiling.
- **Presentation (potential): 3.** Five questions plus a sycophancy pilot read as a tour. Told as "one flaw, its cause, one fix, plus where the pipeline loses conflicts", it scores 4.

## Spot-checks

Four numbers match RESULTS.md: McNemar p 0.0156, 9/10 [0.596, 0.982], 116/120, +0.19 [0, 0.45]. The ledger omits two things: pipeline P3 is 4/6 vs oracle 2/6, and naive emits 213 flags at 312 posts.

## What I attack first

The endorsement proxy and contamination: n = 10 famous philosophers, 9 of whom Haiku names. Only the paired contrast survives this, because the same case flips, and the unrecognised Nozick case flips too. Absolute recall (9/10) does not survive it.

## Top 3 strongest

1. **The marker effect.** 9/10 plain vs 2/10 with "I've changed my mind" (7-0, p = 0.016). Oracle P3 confirms it (2/10).
2. **Staged loss in shipped code.** Theme grouping keeps 30/46 positives together. The window covers 44% of pairs at 30 entries and 11% at 60. The 60-character filter drops posts. All of this is deterministic.
3. **Validation scaffolding.** A cross-family writer, blind relabels, a judge checked on planted leans.

## Top 3 weakest, and what to do

1. **No endorsement data.** *Strengthen.*
   - Run the PLAN v2 #10 self-study (about 2 hours, only with the user's explicit OK). Write the known changes down first, then rate each flag: want it shown? Is it fair?
   - Otherwise rename Q1 "recovery of publicly self-reported reversals" and drop "endorse" from the claims.
2. **The fix, and the ceiling data.** *Rerun* (about 3 hours).
   - The fix: held-out P3 is n = 4, H2 drops 6/6 to 4/6, sarcasm rises from 0/6 to 1/5, and it was never run in pipeline mode. Run it end to end on t12-t23.
   - The ceiling: decoys score 0/80 and Local scores 0 everywhere. Add 20 harder hand-made decoys (partial concessions, quoting one's own earlier view).
   - Report flags per history for every system.
   - *Shrink* Local and naive vs pipeline (p = 0.125) to one line each.
3. **Q5 and Q4 are padding.**
   - *Cut* Q5: its stance reader is at kappa 0.02, and ELEPHANT's 48% invites a bad comparison.
   - *Shrink* Q4 to one line, and promote the kind-label nudge instead: 17/53 no-cue pairs are framed as growth by elapsed time alone.

## Agreements with the other critics

All three of us agree: the marker effect and the staged loss are strongest; the ceiling and the endorsement proxy are weakest.

- **critic-novelty:** the prompt's "do not count more careful wording" rule makes the marker effect partly self-inflicted. Claim it as a failure of a shipped prompt, not of the model. The nearest prior work is BeliefShift (arXiv 2603.23848). Cut Q5.
- **critic-methods:**
  - Suppression is shown in the oracle setting, not end to end, because one pipeline P3 hit is joined to filler only.
  - "Frozen before runs" rests on minutes: variant.ts was committed at 01:12 and outputs are timestamped 01:15. State that without overclaiming.
  - Report the four-label kappa of 0.69 (before key correction) as primary.
