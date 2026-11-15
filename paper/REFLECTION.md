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

## After the round-19 mock judges (I 3/3/3, E 4/3/3, P 3/3/3)

- **Belief:** fresh set 2 was blind to our design. **Evidence:** rereading its sourcing brief (judge 3 flagged the abstract's "never saw our prompts"), it asked the agent to prefer passages inside the first 400 characters because the shipped tool read only that much. **Change:** disclosed in 3.2, 4.3 and Appendix A; this, with 5 of 6 announced cases, explains why simple prompts score 5-6/6 there. A hard held-out set must be sourced with no hint about the tool's reading window.
- **Fixed facts:** "every prompt missed both at 400 characters" is now realX and changes only (the stance prompt found Godwin); deployed vs realX-400 over 24 cases is 23 vs 21, exact McNemar p = 0.5, now stated; Table 4's "development" marked as the earlier-round set.
- **Judges' top asks not yet done** (all need new runs): card cost and genuine share for the deployed configuration on all 24; a hard held-out set (retraction-only or late-sentence cases, sourced with no hint); a real-text definition 2x2; name-masked reruns.

## After round 20 (card cost)

- **Belief:** the deployed configuration's extra recall might come with a flood of weak cards. **Evidence:** it shows 5.0 cards per history against realX's 2.5, with the same genuine share (80% vs 83%); non-genuine cards go from 0.4 to 1.0 per history. **Change:** the abstract and 4.3 now give the cost; the repair buys its two extra cases with about one more non-genuine card per history.
- **Failed prediction:** control + announcement anchors were called real 5/24 (predicted ≤ 3). The generic "real tension" label is lenient, and some controls sit in the very work the author disowns, so the genuine shares are upper-ish. Next: a stricter label with the case's question, or control passages drawn from a third, unrelated work.

## After round 21 (fresh set 3)

- **Belief:** the second prompt and longer excerpts are what fixed retraction-only cases (from Godwin, James, Hume). **Evidence:** on six unseen, mostly retraction-only cases sourced with no hint about the reading window, realX alone, changes alone, the stance prompt and the deployed pair each found 4; the pair added nothing. **Change:** the abstract, contribution 3, 4.3 and the conclusion now say the definition repair is what generalises; the extra call and length help only on tuning cases. Product consequence: the deployed second call doubles cost for no shown held-out gain; keep it only if the card cost (round 20) and Godwin-like late sentences justify it.
- **What none of the prompts can do:** Coleridge (early view embedded in a political address) and Wordsworth (a retraction that names nothing) were missed by every arm in every run. Next: these need the early view to be found by topic, not by a contradiction cue; test whether giving the model the later retraction and asking "what earlier view is this disowning?" finds them.

## After round 22

- **Belief:** cause 2 (the definition and the empty-list default) explains most of the shipped prompt's loss, as on planted items. **Evidence:** on real text the two edits take it from 3 to 6 and 11 of 30; realX reaches 25. **Change:** 4.2 now says the definition and default explain part of the loss; the rest is realX's other wording (generic base, the retraction paragraph). "What generalises" is now "the rewritten prompt", not "the definition fix". Next, if worth it: shipped prompt + realX's retraction paragraph alone, to split the remaining gap.
- **Belief:** retraction-only misses are a linking failure. **Evidence:** told which passage retracts, Haiku finds the disowned view for 11 of 14, including Wordsworth; so mostly they are a noticing failure. Hume, Kant and Coleridge fail even with the retraction pointed out. **Change:** cause 4 now says so. Product idea (not built): a pass that first finds retraction-like passages ("my former opinions"), then asks what each disowns.
- **Decision (user delegated all decisions):** removed the second prompt from Persona (c9a32b4c, deployed). The paper now names the two-call setup "deployed Nov 14-15" and the live one realX with longer excerpts.
- **Mistake caught:** a rerun job used guessed request ids (v18_3_prod) instead of the real ones (prod3, prod4); stopped before it wrote anything, relaunched with checked ids. Always take ids from the request files.

## After round 23

- **Belief:** the shipped prompt's failure on real text might be our wording; independent strict prompts, which kept planted reversals, would do better. **Evidence:** GPT's three strict prompts found 1, 6 and 1 of 30 on real text (shipped 3). **Change:** contribution 2, cause 2 and lesson (2) now say strict prompts as a class lose real changes of mind; the planted-item marker cliff is our prompt's own, the real-text failure is not. This is the paper's most general finding.
- **Belief:** longer excerpts are free. **Evidence:** what ships returns 3.4 cards per history at 73% genuine (0.9 non-genuine), against realX at 400 characters 2.5 at 83% (0.4). **Change:** abstract now gives the shipped configuration's cost. Product: longer excerpts buy Godwin-like cases (late decisive sentences) at about half a non-genuine card more per history; kept, since a card is dismissable and missing a change is silent.
- **Process:** importing a builder re-ran it and nearly overwrote round-20 inputs (set-order nondeterminism); restored from git, new builders do not import old ones.

## Round 24

- Belief: the shipped definition ("asserts both as their own view") would still block most changes even with the retraction paragraph added (≤ 12 of 30). Evidence: 19 of 30, with the definition untouched. Change: the paper's cause 2 now says the definition matters less on real text than one paragraph telling the model a retraction counts; the paragraph adds 10-16 cases whichever base it sits on, and the base adds 2-6 once it is there. "Most of the gain is one paragraph" is now a measured claim (three bases × with/without), not an inference from realX vs genX alone.
- Belief: what ships would hold up as itself on unseen sets. Evidence: its own three runs gave the same 10 of 12 the borrowed first calls gave, 8-0 over the shipped prompt. Change: the abstract and §4.3 now cite its own runs with an interval and a paired test; the borrowed-first-call caveat is gone from Table 3.
- Labeller drift check: the same 51 key pairs got 48, 44, 47 both-yes across three rounds; decoys 0/30 this time. Stable enough to keep pooling.
- Next: the failed prediction says I still over-weight the definition. The open question is what in the paragraph does the work: the "rarely restate" sentence or the "rejects, abandons or corrects" instruction. That is cheap to split, but it only refines a product prompt already shipped; a name-anonymised rerun on the 12 unseen cases tests the paper's biggest validity threat (the model knowing these authors) and comes first.

## Round 25

- Belief: the rewrite's unseen result might lean on Haiku recognising famous authors. Evidence: with names, own-work titles and dates masked it found the same 10 cases. Change: the abstract states this; contamination now rests on recognisable prose only, which masking cannot remove.
- Belief: the rewrite clearly beats a naive prompt (predicted p < 0.05). Evidence: 25 vs 20, 5-0, p = 0.06. Change: the paper now says most of the shipped failure is over-constraint, which a one-line prompt avoids, and the rewrite's own gain is the retraction cases. This weakens the "our prompt is the fix" story and strengthens the "strict prompts collapse" story, which is the more general finding anyway.
- New: half the rewrite's finds rest on the announcing passage (25 → 14 without it), and the retraction paragraph's gain on the shipped prompt almost entirely (19 → 6). The retraction paragraph teaches the model to notice announcements; it does not make it see unannounced drift. This is the honest ceiling for the Track 3 use case (drift people miss), and is now in the paper.
- Process error: I relaunched a saved label script whose ids were hard-coded, not read from args, which would have overwritten round 24's labels. Stopped it before any write (checked with git). Rule: before reusing a saved workflow script with new args, check it reads args.
- Next: the judges' remaining no-user items are a hard-negative labeller calibration (same-author, same-topic non-keyed pairs) and the Track 3 angle from existing data (the "change of mind" vs "live" label against the case keys). The calibration matters more: every case-level number rests on it.

## Round 26

- Belief: credit from off-key pairs might be labeller leniency. Evidence: a stricter judge with a verbatim-quote requirement confirmed 91% of those pairs, and hard negatives drew 3/51 from the usual pair. Change: the scorer's reliability is now stated with a hard-negative rate and a third judge, not just random decoys.
- Belief: Opus would accept nearly all keys (≥ 45/51). Evidence: 42; it rejected mostly unannounced passages at 1,000 characters, which state the new view without addressing the old. Change: none to scoring (keys are verified by sources, not labellers), but it shows a strict judge reads "rejects the earlier view" narrowly, so Opus agreement is a conservative bound.
- The rewrite's advantage over the naive prompt is fragile: 5-0 under two labellers, 3-0 under three, never significant. The paper's claim should be that over-constraint caused the failure and that the rewrite is at least as good as a naive prompt with the shipped exclusions and output rules, not that the rewrite is a better detector. Next: make that the explicit framing in §4.3 and the conclusion, then a fresh judge look.

## Round 27

- Belief: the shipped prompt might be a deliberate precision trade-off. Evidence: with the retraction paragraph it keeps the same 0.13 non-genuine cards per history and finds 19 cases, not 3; a GPT strict prompt finds 6 with none. Change: the paper now says the shipped prompt is dominated, so the miss was a design error, not a trade-off.
- Belief: the naive prompt was held back by the 400-character cut (predicted ≥ 22 with longer excerpts). Evidence: 20, and more non-genuine cards (1.7 per history). Change: the rewrite's value over the naive prompt is now stated as precision (79% vs 47% genuine at 400 characters), which is the reason it, not the naive prompt, should ship.
- New: longer excerpts double the rewrite's non-genuine cards (0.5 → 1.0 per history) for one more case (25 → 26). That is a product question the paper should state rather than hide: the 400-character rewrite may be the better operating point. Not changing the product now; flagged in the paper's numbers.
- Memory: Haiku could not state 10 of the 18 later changes from author, years and question, and what ships found 8 of those 10. Together with masking, memory does not explain the finds.
- Next: a fresh judge look, then decide whether the remaining asks (a modern non-canonical set; Sonnet as the system under test) are worth the cost before the deadline.

## Round 28

- Belief: a plain prompt would flood writing with no change with cards (naive ≥ 1.5 per history). Evidence: 0.93, but almost all non-genuine; the one-liner 0.7. Change: the false-alarm comparison is now measured on writing with no documented change, not only inferred from labels on change-histories.
- Surprise: what ships (realX deployed text, longer excerpts) raised the most false cards of any prompt on no-change writing, 1.10 per history, against 0.27 for realX at 400 characters. Together with round 27 (non-genuine 1.0 vs 0.5 on real histories) the longer excerpts cost about 2-4 times the false alarms for one case (Godwin). Belief now: the 400-character rewrite is the better product operating point. Because the deployed text differs from the tested realX text (it adds the shipped output rules), the next round tests the exact candidate (deployed text, 400 characters) with a decision rule written first, before changing the product.
- A one-line change-of-mind prompt matches the rewrite's recall (25). The rewrite's case rests on precision, with a bootstrap interval that excludes zero, and that is now how the paper argues for it.

## Round 29

- Belief: the longer excerpts caused most of what ships' false alarms, so 400 characters would fix them. Evidence: the deployed text at 400 still raised 0.67 non-genuine cards per history on no-change writing (tested text 0.27) and 0.90 on real histories. Change: the decision rule kept the product as it is, and the paper now attributes the false alarms mainly to the deployed wording's output rules, not to excerpt length. My prediction ("so switch") failed; the rule stopped a product change the data did not support.
- The cheap next hypothesis: "Return at most 8 pairs, the sharpest first" invites the model to fill the quota. Persona already caps cards at 8 in code, so the line is redundant. Test: the deployed text without that line, at the product's longer excerpts, on the 30 real and 30 no-change histories, with a decision rule written first.

## Round 30

- Belief: the quota line ("at most 8 pairs, the sharpest first") made the model fill the quota. Evidence: removing only that line kept recall at 26 of 30 and cut non-genuine cards from 1.0 to 0.3 per history on real histories and from 1.1 to 0.4 on no-change writing. Change: shipped to Persona under a rule written before the run.
- This is the paper's cleanest product lesson and it mirrors the first one: a line meant to bound output (an empty-list default, then a pair quota) changed what the model looks for. One made it find almost nothing; the other made it find too much. Neither shows in a demo.
- Round-29's rule mattered: without it I would have switched to 400 characters, which the round-30 result shows was the wrong fix.
- Next: one more judge look on the final draft; then the remaining asks are human labels (needs the user) and a non-canonical, modern set, which needs new sourcing. Before the deadline, presentation and consistency matter more than another arm.

## After judge look 4

Belief: the headline numbers were tied to the configuration Persona runs. Evidence: the judges found the abstract's precision figure (79%) and "half its finds" both came from realX at 400 characters, a configuration we rejected, and that "same 26" hid a swap of cases. Change: every headline number now names its configuration; the next test should be run on the final configuration itself, not inherited from a sibling. Next: the no-announcement check has only been run on realX at 400 and the shipped prompt, so run it on what Persona now runs (depNoCap) on all 30, with predictions committed first.

## After round 31

Belief: "half the finds rest on the announcing passage" (post-hoc) measured how much Persona depends on a person saying they changed their mind. Evidence: deleting that post from the input gave 16 of 30 and 5 of 12 unseen, against 12 and 1 of 12 from the post-hoc cut; the cut counted pairs the model would have returned if the announcement were not drawing its attention. Prediction "within 2" failed by 2. Change: post-hoc ablations of inputs are lower bounds here; report the input deletion as the number. Caveat: this round's decoy rate was 17% (5 of 30), so the 16 leans generous; a second labelling of x18 decoys or Opus on the 8 credited returned pairs would tighten it. Next: the remaining large gap is unseen sets without announcement (5 of 12); fresh set 3 (retraction-only, 2 of 6) is where Persona is weakest, which is the case a real user most resembles.

## After round 32

Belief: the precision lead might be an artefact of batch drift or of Haiku labelling its own outputs. Evidence: in one shuffled batch labelled only by Sonnet and Opus, every number moved by at most 0.06 per history and the ordering held exactly as predicted (shipped 0.07 ≤ Persona now 0.27 < realX 0.47 < one-liner 0.93 < naive 1.17). Credit at one pair per run barely moved (Persona now 26 → 24, naive 20 → 18), so recall is not bought with extra pairs. Change: the precision claim now rests on the single batch; Table 4 uses it. What remains open is not labeller choice but who the cases are: famous authors and a model that half-knows them. Next: stratify recall by the closed-book probe (cases Haiku can state from memory vs not) for Persona now and naive, from existing files.

## After round 33

Belief: no prompt leans on memory (predicted every gap within 20 points). Evidence: Persona now finds 88% of the changes Haiku cannot state and 86% of those it can; the naive prompt drops from 79% to 56%. Prediction failed for naive only. Change: memory is a weak explanation for Persona's finds but a plausible one for part of the naive prompt's, which strengthens the case that the rewrite reads the text. Caveat: "stated" is Haiku's free recall with a hand-judged direction, and 16 cases is small (one case = 6 points). Next: the remaining open judge points are presentation (plain arm names, a shorter Table 4) and a harness canary for the shipped 3 of 30.

## After round 34

Belief: the shipped prompt's 3 of 30 is the prompt, not the agent harness reading a long file. Evidence: the same prompt, harness and histories return a plain planted reversal in 29 of 30 while finding 1 documented change; it never pairs the planted posts with real ones. Held as predicted. Change: the harness objection is answered in §4.1 in one sentence. Next: presentation only (plain arm names, shorter Table 4), then a final judge look.

## After round 35

Belief: the gap is about the prompt, not Haiku. Evidence: Sonnet reproduces it on the unseen sets (11 vs 1 of 12; Haiku: 10 vs 2), and the stronger model does not rescue the shipped prompt. Held as predicted. Change: "one model" narrows to "one model family". New risk noted: Sonnet's classifier blocks some reads of historical text on slavery and religion (4 of 72 runs), which a product on Sonnet would have to handle. Next: the open judge items are framing (endorsement proxy) and a cross-family replication we cannot run here; the paper's measured claims are now as checked as this sprint allows.

## After round 36

Belief: Persona's low false-card rate (0.27 per history) would hold on writing without a clear change. Evidence: on two-work histories with the documented change removed it rose to 0.60 (naive 1.17), while still finding about one genuine undocumented change per history. Failed by 0.1. Change: the paper now reports this as a cost: with no obvious change to report, the prompt reaches for weaker pairs. Product implication (not acted on; no rule was written): a confidence threshold or a "nothing found" path would be the next thing to test.

## After round 38

Belief: demanding evidence (a verbatim quote) would drop weak cards without costing recall. Evidence: it dropped some (0.63 → 0.47 on two-work writing) but also dropped real finds (James, Miller: 26 → 24) and its real-history cards got worse, not better (0.30 vs 0.17 in the same batch). The quotes themselves were verbatim 96% of the time, so the model can quote; requiring it changes which pairs it picks. Change: no product change; the paper reports a tested fix that did not pass its rule. The batch drift (0.27 vs 0.17 for the same cards) is a reminder that comparisons are only fair within one batch, which is how both product decisions were made.

## After round 37

Belief: the repair generalises to cases chosen with no knowledge of it. Evidence: a fourth set sourced after the current prompt shipped, with no constraints that favour either prompt, gave 6 of 7 against 1, as predicted. Change: the paper now has one fully clean test of what Persona runs, reported apart. It is small (7) and its p-value alone is 0.06, so the claim rests on the pattern across four independently sourced sets, not on any one.

## After judge look 7 and round 39

Belief: "Persona now runs it" described the product. Evidence: the product's 120-post gate would have routed 29 of our 37 test histories to the word-theme fallback that the audit shows fails. Change: the gate is now 124 (the largest tested), shipped; and the paper says plainly that longer records still take the failing path, which is now the most important open product problem. Second belief: the labellers might be producing the shipped-vs-rewrite gap. Evidence: with no labeller at all, exact key pairs give 2 vs 15, and any pair touching a keyed passage 4 vs 25. The gap is not a labeller artefact.

## After round 40

Belief: the whole-history call keeps its quality at twice the length if excerpts stay long. Evidence: recall held (longBig 28 of 30 against 26 short), but false cards tripled (0.20 → 0.67 per history), with 2.8 pairs per history instead of 2.2: more text gives the prompt more weak pairs to reach for, the same drift round 36 showed on writing without a clear change. Prediction failed on cost, held on recall. Change: the gate stays at 124. Second belief, about the rule itself: it compared long records with short ones, not with what long records get now (the word-theme path, which found 0 of 19 keyed pairs). That is the product question, and it was not asked. Next (round 41, written after this result and said so): run the theme path on the same 30 long histories and decide against it, with both arms' cards in one fresh label batch.

## After round 41

Belief: the theme path is quiet on long records, so whole-history's extra false cards are a real cost against it. Evidence: the theme path is not quiet: 0.87 non-genuine cards per history, 24% genuine, while finding 2 of 30; sending the record whole finds 28 at 0.67 and 75% genuine. It sends under half of each record and the earlier passage of the documented change in only 9 of 30, so it cannot find most changes at any prompt. Change: the gate is 244 posts in the product. Lesson for the method: a decision rule needs the status quo as its comparator, not an ideal; round 40's absolute bar would have kept users on the worse path. The rule for round 41 was written after seeing round 40, which the paper states. Next: records over 244 posts (still the theme path), and the 0.67 false-card rate on long records, which is now the largest cost Persona's users see.
