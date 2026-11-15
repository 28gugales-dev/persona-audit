# Reflection log

Main question: does Amphi's belief-mapping feature (Persona conflicts) help people notice where their views conflict or change, in ways they later agree with?

## Stage 1 → 2 (2026-11-14, ~00:50)

- Still answering the main question? Yes, but the sycophancy pilot pulled toward a "sycophancy rate" paper. The user flagged it twice and the rubric's novelty check plus ELEPHANT (48% both-sides) say the same: another sycophancy rate is replication. Sycophancy becomes Q5, small.
- What a Track 3 judge rewards: ground truth for a product's output (LidaSim was docked for none), a validated judge, CIs. No past winner measured user endorsement, so an *external* endorsement answer key (people who later said in print they changed their minds) is the most distinctive move available without a user study.
- Stop doing: Persona UI theming. Nothing visual until the paper is drafted.
- Risk: everything is synthetic or historical; the honest gap is a consented user study. Say so up front.
- Practical: no API keys; Claude CLI login expired. Model runs go through Claude Code subagents (Haiku = the production model) and opencode (DeepSeek, cross-family); Codex (GPT) for the judge.

## Stage 2 check (2026-11-14, ~01:15)

Planner and skeptic both flagged: decoys mirror the detector's own rules (so a blind, other-family test set), kind is fixed by date/regex (so don't score it there), theme misses confound model misses (so staged recall), the reversal set needs a frozen rule, hard controls and a contamination probe, and Q1 is only a proxy for endorsement. All folded into PLAN v2. The plan now answers a narrower but honest version of the main question, and the endorsement gap is stated, not hidden. The new framing-nudge measure (skeptic #10) is the most original piece; watch that it stays in.

## Stage 3, early (2026-11-14 ~01:40)

- Results so far:
  - Local finds 0/46 test positives and 0/20 dev positives, with 0 false flags. It needs verdict words ("real", "myth") and the posts state philosophical positions as propositions.
  - Theme grouping puts only 30/46 (65%) of test positives in one theme, so about a third never reach the model.
  - Window coverage drops fast past 20 entries per theme.
  - Blind labels agree with the answer key on 149/150 (kappa 0.986).
- GLM (cross-family): free and Go quotas were both exhausted after 36 calls. No paid spend without the user, so cross-family is cut to GPT on the non-GPT-written sets only (adversarial, reversals), if time allows.
- Still on the main question? Yes. The strongest emerging story is about where a belief-mapping pipeline loses conflicts before any model sees them (grouping, window, short-post filter), plus whether the model, once it sees a pair, separates real flips from look-alikes. That is a product-design finding a Track 3 judge can use.
- Watch: the short-post filter (excerpts under 60 chars are never sent) dropped 10/30 adversarial oracle requests. It's a real product behaviour; report it, don't hide it.

## Stage 3, mid (2026-11-14 ~02:30), two-hour check

- Haiku with the production prompt, once it sees a pair:
  - finds 22/26 test positives (oracle, t00-t11) and 18/18 hand-written positives;
  - flags 0/34 decoys and 0/12 hand-written decoys, sarcasm included;
  - is stable on repeats (20/20 same decision).
- Its one consistent miss is the case the main question cares about most: when the later post SAYS the person changed their mind, it returns no conflict (4/6 missed). The prompt's "cannot both stand" reads a stated change as resolved. Yet Persona's "change of mind" card depends on the model finding exactly those pairs. That is the most interesting finding so far.
- The deployed pipeline loses about a third of conflicts before the model sees them (theme grouping 65%, the 60-character filter, the 20-excerpt window). A naive "where do I contradict myself?" prompt over the whole history finds 96% on short histories, but falls to about 62% at 312 posts. So grouping is needed for scale, and the grouping is where recall goes.
- The on-device detector finds 0 conflicts stated as propositions, including 0/10 philosopher reversals, with no false flags.
- Am I answering the main question? Partly. "Notice" is answered (does it surface them), and "later endorse" through the reversals. Real-user endorsement is still missing and will be stated.
- Is this what a Track 3 judge rewards? Yes: concrete, validated failure modes of a shipped epistemic product, plus a held-out fix. The prompt fix is frozen in commit b7478374 before its held-out runs.
- Stop doing: adding more arms. After the reversals and held-out runs, stop building and go to Stage 4.

## Stage 4 (2026-11-14 ~01:20)

- Three critics, working independently and messaging each other, agree. The strongest parts are the marker effect and the staged pipeline losses. The weakest are the endorsement proxy, the contamination, the planted-conflict ceiling and the thin fix. Sycophancy is padding.
- Decision in PLAN v3. The paper is now about one failure mode and its cause, which directly answers Track 3's question: a reflection tool that hides the changes of mind people endorse, with a cheap fix that has measured costs.
- Am I still answering the main question? Yes, more directly than before. "Does it help people notice changes of mind they'd endorse?" Partly: it notices silent reversals but suppresses the ones people narrate.
- Stop: no new arms after these reruns. Next is writing.

## Stage 5 (2026-11-14, draft written)

- The draft leads with the marker effect (Figure 1), then the pipeline losses (Figures 2-3), then the fix and its costs. Main point in one sentence: a shipped reflection tool hides exactly the changes of mind people narrate, because its anti-nagging prompt reads "I've changed my mind" as settled; one frozen prompt line fixes it on held-out data at a small cost.
- The Apart template (a Google Doc, read via plain-text export) recommends 4 pages. My first render was bullet-heavy and filled the 8-page cap. A rewrite into prose plus a label table brought the main text to about 5.7 pages.
- A claim check before judging caught two unsourced figures: "about 800 calls" (now 742 saved replies, counted) and "11 searches" (now attributed to the novelty reviewer, who logged them). The abstract was 267 words; it is now 241.
- Am I still answering the main question? Yes, as narrowed in Stage 4. Real-user endorsement is stated as not measured, in the abstract's framing, the Limitations and Appendix A.
- The template asks that the final version be primarily written by the team. Flag this to the user: they should rewrite it in their own words before submitting.

## Stage 6, round 1 (2026-11-14)

- Mock judges (Sonnet, three lenses) scored Impact 3 / 3 / 3.5, Execution 3 / 3 / 3.5 and Presentation 4 / ~3 / 3.5. That is below the bar of 4.
- All three caught the same arithmetic error: I had written 0/102 decoys, but the test set has 74 GPT decoys, so the total is 96. RESULTS.md had folded 6 hand-written sarcasm items into the held-out count. The ledger did not catch my own error; independent readers did. Lesson: aggregate numbers need a script that prints them, not hand sums.
- The most-cited substantive fix was the mechanism: is the drop caused by the change cue or by any prefix, and which prompt clause causes it? I preregistered the reruns (8bebec36) and ran 334.
  - The neutral prefix leaves recall at 36/36, so the cue causes the drop.
  - My main prediction failed. Removing the "Do not count" list recovers only 15/36. Removing the "empty list is the right answer" default recovers 29/36.
  - So the story changed: the cause is the prompt's definition of a conflict (two views held at once), not over-generalised anti-nagging rules. I had written the opposite in the draft's Discussion and would have shipped a wrong causal claim. Reporting the failed prediction is itself a strength, as with Zhu and Anchored.
- Clustering critique answered: the history-cluster bootstrap gives a 0.69 drop, CI [0.55, 0.84]. On held-out histories alone it is 16/16 → 4/16 (p = 0.0005).
- Honest weak spot that remains: the end-to-end held-out gain from the fix is 3-0 (p = 0.25), now stated as not significant.
- Still answering the main question? Yes. The finding is sharper now and more general: any reflection tool that defines its target as inconsistency inherits it.

## Stage 6, round 2 (2026-11-14)

- Round-2 judges: Impact 3.5 / 3 / 3, Execution 4 / 3 / 3, Presentation 3.5 / 4 / 4. Better, but not 4 across the board.
- Most-cited: no arm tested the definition story directly; the fix names the cue, so it is partly instruction-following; harness doubts; the 18/40 interval treated four phrasings as independent. Two small factual slips: the 36 items span 18 histories, not 24, and all 8 oracle misses were P3, not "all but one".
- I preregistered the reruns (d080008d) and ran 264.
  - The rewritten definition alone, with no change-of-mind wording, gave 27/36 and 8/10, with 1/40 decoys. Prediction held.
  - Adding the empty-list deletion gave 35/36 and 0/40.
  - The harness check with a different wrapper and production's effort reproduced the contrast (36 vs 15). Item-level agreement is only 20/36, so borderline items are noisy.
- So the mechanism claim now rests on a confirmed preregistered prediction, after an earlier failed one. Both are reported. The paper also has a cue-free fix to recommend, which answers the "fix is tautological" critique.
- Hashes and times moved out of the body into Appendix C.
- Still on the main question? Yes. If anything the result is now more general: a definition-of-target problem any inconsistency-finding reflection tool inherits.

## Stage 6, round 3 (2026-11-14)

- Round-3 judges: Impact 3 / 3 / 3.5, Execution 4 / 4 / 3.3, Presentation 3.5 / 3 / 3.8. Execution is now around 4. Impact is stuck because the result read as "one product's prompt bug". Presentation fell as the paper got denser.
- I tested generality, with each arm committed and predicted first (c1768442, 27e2a576).
  - Three generic contradiction prompts keep every marked reversal (36/36), so the failure is not a property of contradiction prompts in general. But they flag 15-23% of held-out decoys, almost all doubt and questions.
  - The marker pasted onto decoys gives 0/40 under production and both repairs.
- This turned the paper's centre into a clean trade-off. The exclusion list buys precision; the "asserts both" definition costs narrated changes; a time-anchored definition keeps both. That is a transferable design lesson rather than a bug report, so I hope it lifts Impact.
- Ops: the disk filled (ENOSPC) mid-run, and 22 replies failed to save. I freed about 560 MB from uv caches I had filled this session and re-ran exactly those 22. The disk is still nearly full (about 260 MB); tell the user.
- Presentation: the whole body was rewritten around the trade-off figure. Reversal cases, variant texts and judge details moved to Appendix E. The main text now ends on page 8.
- Honesty edits:
  - "committed before running (same author, minutes apart)" instead of "preregistered";
  - the held-out 16/16 is stated;
  - 11-15/36 is given across the two wrappers;
  - Holm adjustment is applied;
  - 17/36 for the date-only label.

## Stage 6, round 4 (2026-11-14)

- Round-4 judges asked for the rewrite on unseen items, its costs, run-to-run variance, and a direct test that the exclusion list buys precision. Design and predictions were committed first (PLAN v7, eb441c20).
- Fresh items (Codex-written, blind Sonnet labels 40/40):
  - Narrated reversals: production 14/20, fix 20/20, rewrite 18/20, generic A 20/20.
  - Narrated look-alikes flagged: 0/20 for production, fix and rewrite; generic A 6/20, all six doubts.
  - Failed prediction: production was meant to be ≤10/20. The fresh items in varied wording hurt it less than the fixed marker did. Reported.
- genX (generic A plus the exclusion list): 36/36 marked, 0/40 decoys. The exclusion list buys precision at no recall cost. Prediction held.
- Rewrite costs: hedged reversals 12/16, decoys 0/22, end to end 12/20 positives and 0/40 decoys (vs production 9/20, gained 3, lost 0, p = 0.25).
- Variance, same wrapper: production 11, 9, 17 of 36 (14/36 items stable); rewrite 35, 35, 32 of 36 (31/36 stable).
- Presentation: Figure 3 and the full limitations list moved to the appendices; the body now ends on page 8.
- Still on the main question? Yes. The rewrite is now a confirmed, not development-only, result.

## Stage 6, round 5 (2026-11-14)

- Round-5 judges: Impact 3/3/3, Execution 3.5/3.5/3, Presentation 3.5/3.5/4. A number audit found no mismatches, but found 8 overstated phrasings, now fixed (e.g. "every narrated reversal" for generics that only ran on the 36 marked items; "16/18" read as a share of flags).
- Asks: a placebo for the definition claim; all runs in the stats; a second model; precision beyond planted decoys.
- PLAN v8 (bae1e53d), 584 runs, every prediction held:
  - The placebo rewording (same meaning, rewrite's length) gave 10.0/36 (runs 8, 7, 15), inside production's range.
  - The 2x2 at three runs per cell: each edit helps in both settings, and every history-cluster CI excludes 0.
  - Sonnet 5.5: 36 unmarked and 36 neutral, but 14 marked (p = 5e-7); the rewrite gave 35; 0/40 decoys under both.
- An honest new cost: the rewrite's 28 end-to-end cards include 4 cross-topic pairs, all blind-labelled "not a conflict"; production had none. Reported in 4.5.
- Cross-family was blocked: opencode free and Go are at their limits. Paid usage was not authorised, so I didn't use it.
- Still on the main question? Yes. The causal claim now rests on a placebo-controlled, preregistered 2x2 and replicates on a second model.

## Stage 6, round 6 (2026-11-14)

- Round-6 judges: Impact 3/3/3, Execution 4/4/3.5, Presentation 3/4/3.5.
- Asks: show this isn't one prompt's quirk; run genX on unseen sets (it looked as good as the repair); a table of every arm and its prediction; a clearer story about what was held out.
- PLAN v9 (b51afc32), 436 runs:
  - **A prediction failed, and it changed the paper's claim.** Three strict prompts that Codex (GPT) wrote from a product brief showed no marker drop (36→32, 30→35, 31→31), and flagged 0/40 decoys each. Their misses were buried and reworded claims.
  - So the narrated-change blind spot belongs to Persona's wording (the "asserts both" definition plus the empty-list default), not to precision-seeking prompts. The general lesson moved from "strict prompts define away change" to "every prompt has its own blind spot, none shows in false-alarm rates, and cue-ablated keys plus independently written baselines find them".
  - genX held every prediction (fresh 19/20, 0/20 look-alikes; hedged 12/16; hand-written decoys 0/22; marked philosophers 9/10). The paper now names genX as the simplest option that works, and the rewrite as the minimal patch.
- Added Appendix F (every arm, prediction and outcome) and real example cards in Appendix E. The example cards raised a design point: a narrated change gets a "which do you hold?" question the person has already answered.
- Still on the main question? Yes, and more honest: the product finding stands, and the generalisation is now about auditing method rather than about strict prompts.

## Stage 6, round 7 (2026-11-14)

- Round-7 judges: Impact 3/3/3, Execution 4/4/3.5, Presentation 3/3/4. No number errors. Asks: intervals on the unseen set; one table decoding every arm; a simpler abstract; fixes for two wording slips.
- PLAN v10 (acd69f6f): two more runs on the fresh 40.
  - Production 14, 10, 8 of 20: my prediction (11-17 per run) failed on the low side, so the run-1 figure had understated the failure.
  - Rewrite 18, 19, 19; genX 19, 20, 20; no look-alike flagged in any run. Gains: +8.0 [4.7, 11.3] and +9.0 [6.0, 12.0].
- This removes the worry that the marker sentence was an artefact. Natural narrated changes lose 30-60% under production too.
- Presentation:
  - Table 3 now lists every prompt with marked, decoy and fresh columns; Figure 2 moved to the appendix.
  - The abstract leads with the fresh-set loss.
  - "Each committed with a prediction" no longer covers the Stage 4 design.
  - The Table 4 caption is accurate about what is unseen.
  - Decoys on types the list doesn't name: 0/31.
- Impact has stayed at 3 for five rounds. Every judge gives the same reason: one product, no users. Only a consented user study (or the author's own history, with their OK) can move it.

## Stage 6, rounds 8-9, and Stage 7 (2026-11-14)

- Round 8: Impact 3/3/3, Execution 4/4/4, Presentation 3/3/3. One judge found four factual slips: a stale reply count, an "every prompt 36/36 unmarked" caption, genX's base having seen the fresh set, and "no look-alike"/"no drop" overstated in the abstract. All four fixed. I retitled to scope the claim and turned 4.1 into prose.
- Round 9: Impact 3/3/3, Execution 4/4/3.5, Presentation 3/3/3.5. No factual problems.
- Stage 7 number audit (about 190 claims): no mismatches, 11 overstatements, all fixed. For example: "both beat the fix line" (the fix line found 20/20 fresh); "no prompt flagged a look-alike" (generic A flagged 6); "zero false alarms on every prompt"; "Table 3 lists every prompt".
- Done-criterion status: Execution ≈ 4. Presentation ≈ 3.2. Impact stuck at 3 for six rounds, for a reason every judge repeats: one product, one model family, no users. More arms won't fix that. A consented user study, or the author's own history with their OK, is the remaining lever, and that is the user's call.
- Ops: the disk filled again (127 MB free). Other sessions' temp folders are the main users (infra-311 about 1 GB, TSA-vr about 460 MB). I cleaned only my own regenerable caches.

## Round 10: real text (2026-11-14 afternoon)

- The user asked to test on philosophers' own words, as the paper's stand-in for user data. That answers the one critique no experiment so far could touch: every positive was our construction.
- The sourcing agent's passages are verbatim, but three of the seven "announced" passages retract without stating the new view (Hume, Kant, Nietzsche-comfort), and several source files contain other people's text (editors' introductions, other journal articles). Both were fixed in the v11 addendum before any run: the coding splits A1, and fixed line spans keep only the philosopher's own words in Test B.
- Before any model call, B1 already failed hard: on real writing the theme sort put the early passage and the later reversal in the same theme in 0 of 6 histories (predicted at most 70%; planted data gave 65%). Only 23-77% of paragraphs land in any theme, and 3 of 6 early passages land in none. Authors don't reuse the same words across decades, so a word-overlap grouping can't pair a reversal. This is a pipeline finding no prompt can fix, and it may be the stronger result.
- After the runs: the real-text result is a clean negative for the paper's own repairs. Shown just the two passages, every prompt mostly missed documented reversals (genX 5/21, controls 0/21). The constructed items were easier than real writing: real authors describe their old view abstractly ("a theory which I formerly held myself"), and genX's own exclusion list reads that as someone else's view. That is the most useful thing the sprint has found about the product, and the paper must lead with it rather than bury it.
- Model grouping fixed planted data (held-out 18/20 together, end to end 18/20 vs 9/20) but not real text at first (1/10): the merge kept 50-90 tiny groups. v2 groups by issue (dev 4/10, 96% coverage).
- Protocol: the 7 v11 cases became the dev set, the real-prose prompt (realX) was frozen after one dev run, and a second, independently sourced set is the held-out test (PLAN v13, committed before its passages were read). Precision is checked on 102 unseen look-alikes before trusting realX.
- Efficiency: each subagent call carries about 80K tokens of harness overhead, so the plan cuts calls (merge only for multi-batch histories; 2 runs instead of 3 on held-out; no production arm in end-to-end real runs).

## Round 10-13 close (2026-11-14 afternoon)

- Held-out real text gave a clearer picture than development: production 2/12, genX 8/12, realX 9/12, no control flagged. genX failing on development (5/21) but working on held-out (8/12) shows how much the case set moves the number: 6-7 cases is small, and the paper says so.
- Model grouping is the bigger product result: on planted data it doubles end-to-end recall, and on real text it is the only thing that surfaces any reversal at all (3/9). Its real-text cards were mostly genuine (15-18/25) and found changes of mind outside our key, which is the first direct evidence that the repaired tool shows people something true about a real record.
- Card labels: a cheap Haiku rater agreed with the author's labels at kappa 0.34, Sonnet at 0.46. Only the aggregate (15-18 of 25) is stable across raters, so only the aggregate is claimed.
- Still not answering "do people want this?". The real-text work moves Impact's evidence from constructed to real records, not to users.

## Rounds 14-15: the baseline that beat my repair (2026-11-14 afternoon)

- The judges' request for a whole-history baseline was the most useful thing in the loop. The naive single call beat grouping v2 + realX on real text (7/19 vs grouping's 3/9 held-out), and I had predicted it would not (<= 4). Kept as a failed prediction.
- Swapping in realX for the single call gave the best arm of the whole paper: 10/19 (held-out 6/9), no controls, 23-25 of 27 cards judged genuine. The product lesson changes: for a history that fits in one context window, the theme split is the bug; grouping is only for longer records, and our long-record evidence is planted-only.
- Run 3 of held-out Test A moved genX down (2 vs 4 mean), so three runs and case-level counts were worth the 45 calls; realX held steady.
- Author probe: 26/27. Contamination is near total; the paper now says so plainly.
- Cost discipline: 12 + 2 calls for v15, Haiku except one Sonnet label call.

## Round 16 and judging rounds 11-12

- Rerunning the whole-history arms was the right call: run 1 of realX (10/19) was its best; three runs give 10, 7, 5 and a majority of 8/19, against naive 6/19 (p = 0.5). The "largest gain from the prompt" story did not survive; "put both ends in one request" did. I nearly shipped a single lucky run as the headline.
- The judges keep finding bookkeeping, not numbers: the prediction tally needed a stated rule. Every number they spot-checked matched the ledger.
- Plateau: Impact 3 for twelve rounds. Stopping the arm loop here; the remaining levers need the user.

## Round 17: what the failures say, and what changes (belief -> evidence -> change)

1. **Belief:** co-location is the main lever ("not splitting" was my headline). **Evidence:** the shipped prompt on the whole history finds 0/19 and returns almost nothing (10 pairs in 36 history-runs); naive 6, realX 8. Prediction (2-6) failed. **Change:** the claim becomes "both are needed: the split hides the pair, and the shipped prompt's definition and empty-list default suppress it even when it is visible". Rule from now on: before stating "X matters most", list the factorial cells that claim needs (here grouping x prompt, 2x3) and run the missing ones first; the judges found my missing cell, I should have.
2. **Belief:** Haiku knows these texts, so contamination inflates the repairs. **Evidence:** closed-book it recalled 7 of 13 changes; half the pairs realX surfaces are in cases it could not recall. Prediction (>= 9) failed. **Change:** report the closed-book result as the contamination control, drop the hand-waving; and test priors about what a model "knows" directly and early, since mine were overconfident twice (author probe framing, this).
3. **Belief (last round):** realX's 10/19 was the result. **Evidence:** it was the best of three runs. **Change:** no single-run headline, ever; the cluster bootstrap over histories is now the headline unit.
4. **Process:** constructive judges (critique must carry a fix) produced ranked, runnable work in one round, where twelve rounds of score-only judging repeated "no users". Keep that format.

Next round, from these: rewrite the abstract and 4.3 around "both the split and the prompt", put the closed-book control in 4.1, add the production whole-history row, then judge again.

## Constructive round 3 (after v17): belief -> evidence -> change

- **Belief:** the v17 additions (production-on-whole-history, closed-book control, real-text figure) would lift Impact or Presentation. **Evidence:** Impact 3/3/3, Execution 3.5/4/4, Presentation 3/3/3; same as before. New critiques are new angles (strawman: the shipped prompt targets live conflicts; no embedding-retrieval baseline; untested grouping+production cell), not unresolved old ones. **Change:** the run-more-arms loop has hit diminishing returns per token. Stop adding arms. The levers left are the user's: ship the fix in Persona, a consented/own-history check, a public code link, and a presentation pass that cuts the paper to one claim. Fixed the slips the judges found (table numbering, rank wording, label date, reply count, an overclaim).

## Deploy + public repo round (after constructive round 4)

- **Belief:** deploying the fix and publishing the repo would move Impact. **Evidence:** Impact 3/3/3.5, Execution 4/3.5/3.5, Presentation 3/3/3.5; small rise, no mismatches. Judges now ask for third-party-style prompts on the same histories, a related-work comparison table, and an honest downgrade of realX vs naive (2-0, p = 0.5). **Change:** the paper's limit is now n and the absence of users, not missing analyses. Remaining budget is better spent on readability than on more arms.

## Round 18: the scorer was the weakest part (belief -> evidence -> change)

1. **Belief:** realX "finds 8 of 19" and the tool is still weak. **Evidence:** the 19-pair score credited only the keyed later passage; blind thesis labels (key 102/110 yes, decoys 6/102) show most off-key pairings are the same change of mind. Case-level, realX found 11 of 12 dev cases. **Change:** score by change of mind (case), cross-era, blind-labelled; keep the strict pair count beside it.
2. **Belief (mid-round):** "the gain is the second sample, not the new wording". **Evidence:** that came from the early-anchored scorer; cross-era, the changes prompt alone found 12/12 dev including Hume. **Change:** withdrawn within the round. Lesson: re-run a conclusion under every scorer before writing it into the plan.
3. **Belief:** new authors behave like the dev set. **Evidence:** fresh1 single realX 2/6 early-anchored; the misses were a scorer artefact (Franklin) and a product cut (Godwin, James: key words after character 400). **Change:** longer excerpts, which only the fresh failures revealed; a second fresh set sourced before choosing, so the final number is untuned.
4. **Process:** subagents declined 12 eval calls and the runner counted their prose as "ok" (it matched /ok/ inside other words). Now the runner requires a bare "ok" and every round checks files exist.
5. **Result:** deployed configuration 6/6 on fresh2 (18/18 looks, no control flags) vs shipped 1/6. The fresh2 cases (geology, religion) mostly announce the new view, so they may be easier than fresh1; both fresh sets are reported.
6. **Framing change (with the user):** the paper is an audit method that found and fixed a hidden failure, with Persona as the case; not a claim that the tool is good.

## Constructive judging after the audit reframe (round 18)

- **Scores:** Impact 3/3/3, Execution 3/4/3.5, Presentation 3/3/3. The reframe did not move them; every judge's top ask is the same: run naive and realX alone on fresh set 2 (the deployed two-prompt design is not shown necessary there), then a prior-art-style prompt (ContraDoc/BeliefShift-like) on all 24 histories, then a human check of the Claude labellers.
- **Facts fixed:** prediction tally (38 numeric, 16 failed; the old 35 was one too many), merged-look controls now in the scores file, 7-9 (not 7-10) non-genuine cards, 0.0-0.3 is a mean, looks not runs, Lyell counted once (5/5 vs 1/5), and the marker cliff stated as specific to the shipped prompt.
- **Belief -> change:** I thought the untouched 6/6 would carry Impact. Judges read it as unproven necessity without the simple arms beside it. The cheap next step is those arms on fresh set 2 (about 36 Haiku calls plus labels); held for the user's call because they asked to stop polishing the full paper.

## After round 19

- **Belief:** fresh set 2 (6/6, frozen and deployed first) was evidence that the two-prompt, long-excerpt repair works on unseen records. **Evidence:** realX alone and changes alone at 400 characters also find 6/6 there, naive 5/6. **Change:** the paper now says that set confirms the shipped prompt's failure, not that each part of the repair is needed; the case for longer excerpts and the second prompt rests on Godwin, James and Hume in the tuning sets. A discriminating test set would need retraction-only and late-sentence cases, chosen blind.
- **Belief:** the strict-definition cliff might be our prompt's wording. **Evidence:** a "cannot both be true" prompt in ContraDoc's framing found 7/24, near the shipped prompt. **Change:** contribution 2 and 4.3 now say the strict framing, not the wording, fails.
- **Failed prediction:** a stance-over-time prompt (BeliefShift framing) was predicted ≥ realX on dev; it got 10 vs 11, but 21/24 overall and Godwin at 400 characters, where realX and changes failed. Next: if another round runs, test it at longer excerpts as a replacement for the changes prompt, on a new blind set.
