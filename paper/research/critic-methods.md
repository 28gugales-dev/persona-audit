# Methods review (critic-methods, 2026-11-14)

## Re-derived numbers (python3 over paper/results/)
All of these match RESULTS.md. No mismatches.
- Reversals, production prompt: 9/10 plain, 2/10 marker. Wilson intervals [0.596, 0.982] and [0.057, 0.510]. Discordant pairs 7-0, exact McNemar p = 0.0156.
- Fixed prompt: 10/10 on both arms. Controls flagged: 0/7 same-era, 0/9 hard. Probe recognised 9/10 (Nozick not recognised).
- Oracle, t00-t11: positives 22/26, bootstrap [0.76, 0.95]; P3 2/6; decoys 0/34. Pipeline: 20/26. Naive: 25/26, with 1/34 decoys flagged.
- Held-out, production prompt: P3 0/4, decoys 0/46. Fixed prompt: P3 4/4. Hand-written H2 falls from 6/6 to 4/6 and H3 (sarcasm) rises from 0/6 to 1/5.
- Staged: 30/46 test positives land in one theme (41/74 decoys); 11/18 hand-written positives. On-device detector 0/46; word overlap 2/46.
- Item-hit definition: in the oracle runs, all 22 hits join B to A itself. In the pipeline runs, 3 of 20 hits join B to a filler only (2 P2, 1 P3). The definition does not inflate the oracle numbers. It does matter for the pipeline numbers, which rely on fillers being label-checked, and only A-B pairs were checked.

## Cross-cutting issues
- **Harness fidelity.** The production system prompt goes in as user text inside a Claude Code subagent (`=== SYSTEM PROMPT ===` in haiku_in/), on top of that subagent's own system prompt. Effort is not set and there is no API `system` field. Call it "Haiku 5.5 in an agent harness", not "production".
- **Freeze provenance.** variant.ts was committed in b7478374 at 01:12:02. Outputs were committed in d09355d6 at 01:15. The haiku_raw mtimes (01:12:3x) are copy times. So "frozen before held-out runs" is attested by the author but cannot be checked from git. Say so.
- **Circularity.** The fix line was written from the t00-t11 P3 misses. The held-out tests (t12-t23 P3, n=4; reversals; hand-written) were not used to write it, so they are clean as a design. They are tiny, though.
- **Contamination.** It cannot explain the marker effect: each case is paired with itself across arms, and the one unrecognised case (Nozick) flips too. It does undermine 9/10 as absolute recall.
- **Prompt confound** (agree with critic-novelty). The production prompt says "do not count ... being less sure than before". The naive prompt, which has no such rule, finds P3 6/6. The suppression is therefore a property of this prompt with Haiku, not shown to be a general model trait.
- **Judge.** The binary lean-vs-neutral agreement (41/42) does not depend on the 4-key correction. Make the uncorrected four-label kappa (0.69) primary and the corrected one (0.90) secondary, since correcting the key after seeing the judge disagree drifts the key toward the judge.
- **Multiple comparisons.** Only two tests were run, and the marker arm was planned (PLAN v2 #6). p = 0.016 survives Bonferroni at 2 tests. Every other cell is descriptive; keep it that way.
- **Unexplained gap.** P3 is 4/6 in the pipeline but 2/6 in the oracle. The repeats (20/20 same decision) argue against noise, so the theme context changes the outcome. Suppression is shown at the oracle level, not end to end.

## TOP 3 STRONGEST
1. **Marker suppression, paired contrast.** The evidence is 7-0 discordant (p = 0.016), backed up independently by the GPT-written P3 items (2/10). Wording: "With the production prompt, prefixing the same later view with a change-of-mind sentence cut Haiku's detection from 9/10 to 2/10 (paired, p = 0.016). GPT-written signalled changes were found 2/10."
2. **Q3 deterministic losses** from the shipped code: 30/46 positives in one theme, window coverage, the 60-character filter. Wording: as stated, for these synthetic texts.
3. **Q4 neutrality: 116/120** (Wilson [0.917, 0.987]), binary judge agreement 41/42. Agrees with both other critics.

## TOP 3 WEAKEST
1. **The fix.** Held-out P3 is n=4, the reversals are recognised, it costs H2 recall (4/6) and adds a sarcasm false flag (1/5), and it was never run end to end. Shrink the claim to: "one added line recovered signalled changes in a small held-out check (P3 4/4; reversal marker 10/10), at a cost of 2/6 hedged reversals and 1/5 sarcasm false flags". Rerun (about 3 h, about 170 Haiku subagents):
   - the fixed prompt on t00-t11 oracle and pipeline requests (around 70);
   - 3 new marker phrasings × 10 reversals × 2 prompts (60);
   - 20 new hand-written P3 + H2 + sarcasm items written before running (40).
2. **Reversal recall as evidence of finding self-endorsed change.** 9/10 cases are recognised, n=10, and endorsement is only a proxy. Drop "recovers 90% of reversals" as a capability claim and keep only the paired contrast. Rerun: 10 swapped-author or fictionalised versions (the same claims with field-shifted wording, so the probe fails), both arms; 20 calls plus a probe.
3. **Naive vs pipeline, and decoy precision.** Decoys are at ceiling (0/80 unsignalled-set decoys; 36/36 unsignalled positives). The gap is +0.19 with CI [0.00, 0.45] and p = 0.125, so it is not significant. Shrink to: "no measurable precision difference at 26 posts; the pipeline lost recall mainly to grouping". Report flags per history for every system (naive: 6.4 at 26 posts, 45 at 78, 213 at 312; agreeing with critic-judge). Cheap add: run naive on t12-t23 (12 calls) to double the n.

## Agreements
- All three critics rank the marker effect and the Q3 losses as strong.
- critic-novelty also ranks Q4 neutrality strong. critic-judge ranks the blind test set and judge validation strong instead.
- All three rank the endorsement proxy and contamination as weak, and two of us rank the ceiling as weak.
- Only I rank the fix as weakest. critic-judge raised its H2 and sarcasm cost independently.
- critic-novelty would also cut Q5 (prior work: ELEPHANT). I have no objection: n=60 and a stance-reader kappa of 0.02.
