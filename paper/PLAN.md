# PLAN (v2, 2026-11-14, after planner + skeptic review; v1 kept in research/PLAN-v1.md)

## Main question

Does Persona's belief mapping help people notice where their own views conflict or have changed, in ways they would later agree with?

We cannot run a consented user study this weekend (no written consent in hand), so the paper answers the parts of the question that have an answer key:

- **Q1 (recovers self-endorsed revisions; a proxy for "later endorsed").** When a person's record contains a change of mind that they themselves later endorsed in print, does Persona find it, and file it as a change of mind rather than a live contradiction?
- **Q2 (finds real conflicts, not look-alikes).** On histories with planted conflicts and planted look-alikes, how precise and complete are the on-device detector and the opt-in model step, against simple baselines?
- **Q3 (the deployed design's blind spots).** What does the shipped pipeline (theme grouping, then 20 excerpts per theme, 3 conflicts max) miss as a history grows?
- **Q4 (does it steer?).** The model writes the question shown above each conflict. Is it neutral, or does it lean toward one side, toward the philosophical majority, or toward the newer view? This is the fairness check: a reflection tool that steers is not producing views people later endorse, it is producing views it chose.
- **Q5 (small, secondary).** The sycophancy flag ("your AI agreed both times"): how often does an assistant agree with both sides of a contested question in separate chats, and does the on-device stance heuristic that powers the flag work? (Pilot exists.)

## What existed before the sprint vs built during it

| Before (commit, date) | During the sprint (Nov 13-15) |
|---|---|
| Persona import of writing and AI-chat history; theme sort; model conflict step with the production prompt (e2378d80, 2026-11-01); weekly allowance (1c3aa3ba, 11-01); on-device detector (c86449aa, 11-07) | Change-of-mind vs live-conflict split and the "AI agreed both times" flag (5609693d, 11-13); sycophancy harness + pilot (2b7caaf2, 2daaff2f, 11-13); everything in `evals/conflicts` and `paper/` (this evaluation) |

## Data (all real or constructed with a known answer key; no personal data)

1. **Reversals set (Q1).** 10-14 philosophers with a documented, self-endorsed change of mind (data/reversals.json, built by a research agent with URLs). Each case has an earlier claim, a later claim, and a same-era control claim that conflicts with neither. First-person paraphrases (copyright) plus short public-domain quotes where available. Each case becomes a small dated history; extra filler entries from the same period on unrelated topics are added so the detector has to search.
2. **Planted-conflict histories (Q2, Q3).** Synthetic users, each a dated history (20-60 entries over 2-4 years, 3-6 topics). Topics come from the 35 PhilPapers 2020 questions where the top two answers are both >= 25% and within 15 points (data/philpapers2020_contested.tsv), so neither side is a textbook fact. Statements come from the reviewed claim bank (`evals/argue/bank`, 124 phil+psych questions), rewritten as casual first-person posts.
   - Positives (should be flagged): P1 blunt reversal (same words, opposite verdict), P2 paraphrased reversal (little word overlap), P3 explicit change of mind ("I used to think...").
   - Decoys (should not be flagged): D1 someone else's view ("my professor says"), D2 doubt or hedge ("less sure now"), D3 a question, D4 a compatible refinement, D5 shared word, different subject ("moral realism" vs "moral luck"), D6 two bank options marked `compatible_with`.
   - Each history gets 2-4 positives and 3-6 decoys at random; the rest is filler. Generation is seeded and scripted (templates + one paraphrase pass for P2). Every generated item is checked for its label: a scripted check on all items, and a hand check of 40.
3. **PhilPapers 2020 aggregates** for topic choice and Q4's majority side (cited, CC BY-NC).
4. **Sycophancy pilot** (evals/sycophancy/results/subagent-pilot.md): 3 Claude models x 60 pairs, already run.

Cut: friends' Reddit histories (no written consent in hand) and LMU/Moorpark pilot data (Discuss classroom app, not belief mapping; no documented OK to use it in a paper). Both go in Limitations as the missing user study, with the protocol written out.

## Systems compared

- **Local**: on-device detector `findLocalConflicts` (unmodified, imported).
- **Model (production)**: `CONFLICTS_SYSTEM` + `conflictsPrompt` + `readConflicts` (unmodified, imported) on requests built by the real `sortLibrary` + `conflictRequests`. Production model is Claude Haiku 5.5; here it runs through Claude Code subagents with model "haiku", one request at a time, because no API key is available. Disclosed.
- **Model (cross-family)**: the same prompt on DeepSeek V4.1 Flash via opencode, to show the result is not one model's quirk.
- **Baselines**: (a) naive prompt, whole history, "list pairs of entries that contradict each other" (what a user gets by pasting history into a chatbot); (b) word-overlap baseline (same subject + opposite sentiment word, no decoy filtering); (c) random pairs at the same flag count.
- **Pipeline**: Local OR Model, as the app shows them together.

## Metrics

- Pair-level precision, recall, F1 against the answer key; recall per positive type and false-flag rate per decoy type.
- 95% bootstrap CIs over histories (1,000 resamples, fixed seed). Paired comparisons (Local vs Model, Model vs naive) with McNemar on positives and on decoys.
- Q1: reversals found (k/n, Wilson CI), controls wrongly flagged, kind assigned (`conflictKind`).
- Q3: share of planted pairs where both entries reach the model's request, by theme size (computed from the real code, no model needed), and end-to-end recall by history length.
- Q4: label per tension question: neutral / leans earlier / leans later / leans majority. Judge: GPT (Codex CLI), validated against 40 hand labels (Cohen's kappa reported); a second judge (Claude Sonnet subagent) on the same items. Lean rate with CI, and lean toward majority vs minority.
- Q5: as preregistered in evals/sycophancy/PREREG.md.

## What counts as success (written before running)

- S1: Model recall on P2 (paraphrased) >= 0.6 and false-flag rate on decoys <= 0.15. Local recall on P2 expected low (< 0.3); reported either way.
- S2: Model finds >= 70% of documented philosopher reversals and flags <= 20% of same-era controls.
- S3: Model beats the naive whole-history prompt on precision at similar recall (the product's prompt and grouping add value).
- S4: >= 90% of tension questions judged neutral, judge kappa vs hand labels >= 0.6.
- A miss on any of these is reported as a finding, not hidden.

## Figures planned

1. Pipeline diagram: history, theme sort, on-device detector, opt-in model, card with change-of-mind vs live split.
2. Recall by positive type and false-flag rate by decoy type, Local vs Model vs naive (grouped bars with CIs).
3. Reversals table: philosopher, found by Local / Model, kind assigned, control flagged.
4. Recall vs history length (the 20-excerpt window), with the analytic curve.
5. Q4 lean rates.

## Order of work and what gets cut if time runs short

1. Build generator + runner, run Local on everything (cheap, deterministic).
2. Model runs on reversals and a first 15 histories; then scale.
3. Q3 analytic computation.
4. Q4 judge + hand labels.
5. Cross-family model; naive baseline at full scale.
6. Q5 stays at the pilot; prompt-injection check (appendix) last.

Cut order if short: prompt injection, cross-family model, Q5 extension, naive baseline at full scale (keep a 15-history subset), second judge.

---

## v2 changes (fixes both reviewers flagged; see research/review-planner.md, research/review-skeptic.md)

These override anything above that conflicts with them.

1. **Blind test set vs template dev set.** The on-device detector and the production prompt already encode the decoy types (REPORTED/HEDGE regexes, the "moral realism vs moral luck" comment, the prompt's "do not count" list). So:
   - The template set is a *dev* set.
   - The *test* set is written by a model family that is not under test (GPT via Codex), from data/LABELS.md and the bank statements only. The writer never sees the code or the prompt.
   - Add about 30 hand-written adversarial items, written before any detector run (H1-H3 in LABELS.md, plus a "not" moved and a negated refinement).
   - Report dev and test side by side; the gap is a finding.
2. **Labels are checked blind.** A Claude Sonnet subagent labels a shuffled sample of test items (conflict / not) without seeing the intended label. Items it disagrees on are dropped and their count reported. Plus a 40-item hand check. Lexical overlap (content-word Jaccard) is stored per item, and recall is reported by overlap bin.
3. **Who writes, who detects.** Writer: GPT. Detectors:
   - Local.
   - Haiku 5.5 "in agent harness" (the production model): CONFLICTS_SYSTEM verbatim, no tools, raw text through the real `readConflicts`. 20 requests are run twice, and run-to-run agreement is reported.
   - GLM-5.3 via opencode as the cross-family model, neither writer nor checker.
4. **Staged recall.** End-to-end recall = P(both entries in one theme by `sortLibrary`) × P(both inside the 20-excerpt window) × P(model flags | seen). Each stage is reported, plus an oracle-theme run (the model gets the right theme directly).
5. **Kind (`conflictKind`) is not scored where the answer is fixed.** It is reported only on pairs under 365 days apart with no REVISED cue; elsewhere it is described as code behaviour. P3 (signalled change) is a sanity row.
6. **Reversals (Q1).**
   - Candidate list frozen before running, every checked case reported, two URLs each.
   - Hard controls: same era, same topic, compatible.
   - Names and coinages stripped; the change-marker phrasing goes in a separate arm.
   - A contamination probe asks the model "who most likely wrote these?" on each case, and recall is reported with and without recognised cases.
7. **No pooled precision as the headline.** Lead with per-type recall and per-decoy false-flag rate. Precision is reported at two stated prevalences (1:1 and 1:4 positive:decoy).
8. **Thresholds anchored to baselines** (replacing S1-S4):
   - Model P2 recall beats the word-overlap baseline by >= 20 points with a CI excluding 0.
   - The model's decoy false-flag rate is below the naive whole-history chatbot prompt's.
   - Reversals: model recall above the word-overlap baseline; hard-control flag rate reported.
   - Q4: lean rate with n >= 60 questions.
9. **Q4 widened** (skeptic #10). Two framing effects are scored:
   - the model's tension question (neutral or leaning), and
   - the card's own kind label ("change of mind" frames the newer view as growth).
   Where the person's later verdict is known (reversals, where the later view is the endorsed one), we ask whether the label agrees with it, and how often a live disagreement within a year would be framed as growth.
10. **Endorsement gap stated plainly.** Q1 is a proxy: the philosophers endorsed their change, not our flag. A consented self-study (author's own history, known changes written down before running, each flag rated "would I want this shown") is the only real-endorsement datapoint possible this weekend. It runs only if the author agrees in chat. Otherwise its protocol goes in Limitations.
11. **Budget.**
    - Test set: 24 histories.
    - Dev set: 12 histories (Local + GLM only).
    - Reversals: 10-12.
    - Haiku runs on reversals + 12 test histories + 20 repeats, one request per subagent.
    - GLM runs on everything through a script.
    - Naive baseline on the 12 Haiku histories.
    - Q5 stays at the existing pilot, one paragraph.
    - Statistics: bootstrap over histories, effect sizes, no p-values for small subgroup cells.
12. **Order.** Reversals agent (running) → generator + label checks → Local on all → GLM bulk (background) → Haiku subset → staged recall and Q3 → Q4 judge (GPT via Codex; 30 hand labels) → figures.

---

## v3: Stage 4 decision (2026-11-14 ~01:20, after research/critic-{judge,novelty,methods}.md)

**Main point (one sentence):** A shipped belief-mapping tool judges contradictions well once it sees them, but its design hides the changes of mind it exists to show. An explicit "I've changed my mind" turned detection of the same reversal off (9/10 to 2/10), and grouping and windowing dropped a third of planted conflicts before the model saw them.

- **Lead:** the marker effect, claimed as a property of the shipped prompt with Haiku in an agent harness, in the oracle setting. The evidence is a paired contrast, so author recognition cannot explain it.
- **Second:** deterministic losses in the shipped code (theme grouping, the 60-character filter, the 20-excerpt window).
- **Supporting:**
  - the one-line fix, claimed small and with its costs;
  - the questions stay neutral (one line);
  - the kind label frames change as growth by date alone (mechanism).
- **Shrunk to one line each:**
  - the planted-conflict ceiling, as a testbed-validity row;
  - Local and the overlap baseline, as floors;
  - naive vs pipeline (not significant). Flags per history are reported.
- **Cut:** Q5 sycophancy goes to one sentence in Related work and Limitations (ELEPHANT already covers it; our stance reader has kappa 0.02).
- **Reframed:** "endorse" becomes "publicly self-reported reversals" (a proxy). The real-user gap is stated up front. The self-study runs only with the author's explicit OK in chat, which has not been given.
- **Reruns** (design committed in 0806cd7e before any run):
  1. The marker added to all 36 unsignalled test positives, production vs fixed. This is a paired test at n=36 with no contamination possible.
  2. Three more marker phrasings on the reversals.
  3. 20 new hand-written items aimed at the fix's costs: hedged reversals, concessions, reaffirmations that use change words.
  4. The held-out pipeline end to end (t12-t23), production vs fixed.
- **Judge reporting:** the four-label kappa before the key correction (0.69) is primary; the binary 41/42 is the measure that matters.

## v4: Stage 6 mechanism reruns (written after mock judging round 1, before any run)

Why: all three mock judges asked whether the drop is caused by the change cue or by any prefix, and which line of the prompt causes it. They also caught a decoy-count error (test decoys are 74, so 96 in total with the hand-written ones, not 102).

Design (`evals/conflicts/src/mechanism.test.ts` → `paper/results/requests_mech.jsonl`, 334 requests, Haiku agent harness as before):
1. A neutral, non-revision prefix ("I was reading about this again today.") on post B of the 36 unsignalled positives and the 10 reversals, under the production prompt.
2. The change marker on the same items under three ablations of the production prompt:
   - noDNC: the whole "Do not count" list removed;
   - noDoubt: only its "questions, doubt, or being less sure than before" line removed;
   - noEmpty: the "Most themes have none, and an empty list is the right answer" line removed.
3. Natural narrated changes (P3, 10) and held-out decoys (t12-t23, 40) under each ablation, to price any recall gained.

Predictions, written before the runs:
- Neutral prefix: at least 33/36 and at least 8/10. If it drops like the marker does, the effect is about prefixes, not the change cue, and the headline must be reframed.
- noDNC: marked recall recovers to at least 30/36, and decoy flags rise above 0/40.
- noDoubt and noEmpty: partial recovery. I have no confident prediction about which is larger.

Analysis:
- Counts with Wilson intervals.
- Exact McNemar for neutral vs marker on the same items. This is the only new test.
- A history-cluster bootstrap for the headline 36→11 contrast, to answer the clustering critique.

## v5: Stage 6 round-2 reruns (written after mock judging round 2, before any run)

Why: two of three round-2 judges said no arm tests the "definition of a conflict" story directly. One asked for a fix that does not name the cue, and two asked for a harness check.

Design (`evals/conflicts/src/mechanism2.test.ts` → `paper/results/requests_mech2.jsonl`, 192 requests, plus 72 harness reruns):
1. **defOnly.** Replace only the definition sentence with "Count a pair only when each excerpt, at the time it was written, stated the person's own view, on the same point, and the two clash." It never mentions a change of mind.
2. **defNoEmpty.** defOnly with the "empty list is the right answer" line also removed.
3. Both run on the same items as v4: 36 marked planted, 10 marked reversals, 10 P3 and 40 held-out decoys. Same wrapper and effort ("low") as every earlier run.
4. **Harness check.** The 36 marked and 36 unmarked production oracle requests rerun as run 3, with a different wrapper (the content framed as an API call with a system prompt) and effort "medium", production's setting.

Predictions:
- If the definition drives the suppression, defOnly recovers at least 25/36 marked planted and at least 6/10 reversals, with decoys at most 2/40. If it does not, the paper must say the mechanism is the empty-list default plus something unidentified, and drop the definition claim.
- Harness: marked recall stays at or below 18/36 while unmarked stays at or above 33/36. If marked recall under run 3 is above 25/36, the headline is harness-dependent and must say so.

## v6: Stage 6 round-3 reruns (written after mock judging round 3, before any run)

Why: round-3 judges asked whether the effect generalises beyond the production prompt (impact), and whether the repairs flag decoys once a change sentence is present (the cost side of the recommendation).

Design (`evals/conflicts/src/mechanism3.test.ts` → `paper/results/requests_mech3.jsonl`, 336 requests, same wrapper and effort as runs 1-2):
1. **Three generic contradiction prompts** that nobody tuned for Persona:
   - genA: "find pairs that contradict each other";
   - genB: a consistency checker that ignores different-topic pairs;
   - genC: a one-line question.
   Each runs on the 36 planted positives, unmarked and marked (paired).
2. **Marked decoys.** The change marker is pasted onto post B of the 40 held-out decoys, under production, the fix line and the cue-free rewrite (no empty-list line).

Predictions:
- Generic prompts: no clear expectation. My guess is that marked recall stays at or above 30/36 under at least 2 of the 3, since the naive prompt found narrated changes 6/6.
  - If it holds, the paper says the failure is specific to definitions like the production one, not to contradiction prompts in general.
  - If at least 2 of 3 drop below 25/36, the paper says the failure is broader.
- Marked decoys: production at most 1/40; fix line at most 3/40; cue-free rewrite at most 3/40. If either repair exceeds 5/40, its false-flag cost is material and the recommendation must say so.

### v6b (written after seeing the generic prompts keep 36/36 when marked, before this run)

The three generic prompts also run on the 40 held-out decoys, unmarked (`requests_mech4.jsonl`, 120 requests). This measures what the production definition buys in precision.

Prediction: at least 2 of the 3 generic prompts flag 3/40 or more. If they flag about as few as production (0/40), the definition buys no measurable precision on these decoys, and the paper must say so.

## v7: round-4 confirmation (written after mock judging round 4, before any run)

Why: the cue-free rewrite was chosen after seeing the ablations on the same items, so its 35/36 is a development result. Judges asked for:
- confirmation on new items, including narrated look-alikes;
- its costs on the hand-written sets and end to end;
- run-to-run variance;
- a direct test of whether the exclusion list buys the precision.

Fresh items: `data/fresh_spec.md` → GPT (Codex) wrote `data/fresh_narrated.json`. A blind Sonnet labeller agreed with the intended labels on 40/40. The set has 20 narrated reversals in varied wording (3 use "changed my mind") and 20 narrated look-alikes: 7 refinements, 7 reaffirmations and 6 doubts.

Design (`evals/conflicts/src/mechanism5.test.ts` → `requests_mech5.jsonl`, 367 requests, plus 144 variance reruns, same wrapper and effort as runs 1-2):
1. Fresh items under production, the fix line, the rewrite without the empty-list default, and generic A.
2. The rewrite on all 50 hand-written items, and end to end on held-out histories t12-t23.
3. Generic A plus the production exclusion list ("genX") on the 36 marked positives and the 40 held-out decoys.
4. Variance: production marked requests re-run as r4 and r5, and rewrite marked requests as r2 and r3.

Predictions:
- Fresh narrated reversals: production at most 10/20; fix at least 16/20; rewrite at least 16/20; generic A at least 16/20.
- Fresh look-alikes flagged: production at most 1/20; fix at most 3/20; rewrite at most 3/20; generic A at least 4/20.
- Rewrite on hand-written items: hedged reversals at least 12/16; decoys at most 2/22.
- Rewrite end to end, held-out: positives at least 11/20; decoys at most 2/40.
- genX: marked recall at least 30/36 and decoys at most 2/40. If both hold, the exclusion list buys the precision without costing narrated changes.
- Variance: production marked between 8 and 18/36 on each rerun; rewrite marked at least 30/36 on each.

## Stage 7 status (2026-11-14)

- Body ends on page 8 (Conclusion on p8; references and appendices after).
- Abstract fixed to report the rewrite's 32-35/36 over three runs, matching how production's 9-17/36 is reported.
- Consent and anonymization: no personal data; reversal cases are published philosophers with public sources; the only email in the folder is Apart's public sprint address in research notes.
- Running: mock judging round 5 and an independent number-trace audit of paper.md.
- Left: apply audit fixes, re-check refs 12-15 links, public code link (TODO for the author), final PDF.

## v8: round-5 controls (written after mock judging round 5, before any run)

Round-5 judges (Impact 3/3/3, Execution 3.5/3.5/3, Presentation 3.5/3.5/4) asked for:
- a placebo for "the definition causes it", and a full 2x2 (definition x empty-list default) with several runs per cell;
- stats that use all runs, not run 1 as the baseline;
- a second model;
- precision beyond planted decoys: the rewrite returns more cards per history (1.42 to 2.33), and those extra cards have not been audited.

Cross-family is not possible this round: opencode free models and the Go plan are both at their limits. Paid usage was not authorised. The second model is Sonnet 5.5 in the same agent harness: same family, larger model.

Design (`evals/conflicts/gen/make_mech6.py` → `requests_mech6.jsonl`; all on the 36 marked planted items unless stated):
1. Placebo: the production definition reworded to the rewrite's length, keeping "the person asserts both as their own view":
   "Count a pair only when the person asserts both excerpts as their own view, about the very same point, and the two of them clash."
   Two arms: `placebo` (empty-list default kept) and `placeboNoEmpty` (removed). Three runs each.
2. 2x2 at three runs per cell:
   - production: runs 1, 4, 5 (have);
   - noEmpty and defOnly: runs 2 and 3 added;
   - defNoEmpty: runs 1, 2, 3 (have).
3. Sonnet, one run: production unmarked, neutral prefix and marked; rewrite (defNoEmpty) marked; the 40 held-out decoys under production and rewrite.
4. Extra-card audit (existing replies, no new model calls). All pairs flagged end to end on held-out histories t12-t23, by production and by the rewrite, that are not planted positives or planted decoys. They are pooled, shuffled, shown without arm or date-order hints, and labelled by a blind Sonnet labeller as "clash" (two of the person's own claims that cannot both stand, including a narrated change), "not a conflict", or "unsure". The author then checks every "clash".

Predictions:
- Placebo: mean marked recall within production's range (9-17/36), so the wording change alone does not repair it. placeboNoEmpty is within 5 of noEmpty's 3-run mean.
- 2x2: the definition rewrite raises the mean in both default conditions, and dropping the default raises it in both definition conditions. defNoEmpty has the highest cell mean, ≥ 30/36.
- Sonnet: unmarked ≥ 32/36. Marked ≤ 24/36 (a drop of at least 8). Neutral within 3 of unmarked. Rewrite marked ≥ 30/36. Decoys flagged ≤ 2/40 under each prompt.
- Extra cards: the share labelled "not a conflict" among the rewrite's non-planted flags is within 15 points of production's.

## v9: round-6 generality arms (written after mock judging round 6, before any run)

Round-6 judges: Impact 3/3/3, Execution 4/4/3.5, Presentation 3/4/3.5. Impact is held back by "one prompt's quirk; the model only obeyed its definition". Execution is held back by genX never being run on unseen sets.

Design (`evals/conflicts/gen/make_mech7.py` → `requests_mech7.jsonl`, 436 requests, Haiku, one run, same wrapper):
1. **Independent strict prompts.** GPT (Codex) wrote three system prompts from a product brief: show a person conflicts in their dated excerpts, and avoid false alarms on doubt, questions, others' views, jokes and refinements. The brief never mentions narrated changes, our hypothesis or Persona's prompt. The prompts are stored verbatim in `paper/data/strict_prompts_gpt.json`; two of them say a dated reversal "may" count. Each is run on the 36 planted items unmarked (gs*:plainpos), the same items marked (gs*:markerpos) and the 40 held-out decoys.
2. **genX on unseen sets.** Generic A plus the production exclusion list, on the fresh 40, the hand-written 50 (30 hw1 + 20 adv2), and the 10 marked reversals.

Predictions:
- Strict prompts: each finds ≥ 32/36 unmarked and flags ≤ 4/40 decoys. At least one of the three loses ≥ 8 items when marked (exact McNemar p < 0.05). This would show the failure arises in independently written precision-minded prompts, not only in ours. If none drops, the hazard is specific to wording like "asserts both", and we will say so.
- genX: fresh narrated reversals ≥ 18/20; fresh look-alikes flagged ≤ 2/20; hedged reversals ≥ 12/16; hand-written decoys flagged ≤ 2/22; marked reversals ≥ 8/10. If all hold, genX is at least as good as the rewrite, and we will recommend the simpler prompt.

## v10: fresh-set repeats (written after mock judging round 7, before any run)

Round-7 judges: Impact 3/3/3, Execution 4/4/3.5, Presentation 3/3/4. There were no number errors. They asked for:
- run-to-run intervals on the only fully unseen set;
- one table that decodes every arm;
- a simpler abstract;
- fixes for wording slips ("each committed with a prediction" also covered Stage 4, which had no numeric prediction; the Table 4 caption overstated unseen-ness).

An inline-prompt wrapper was considered and dropped: passing every request's text through the orchestrator would cost more than the check is worth. The run-3 harness check already varied the wrapper.

Design: production, the rewrite (defNoEmpty) and genX on the fresh 40, runs 2 and 3 (same wrapper as run 1): 240 Haiku calls. Report per-arm counts per run, items stable across runs, and a paired comparison against production that pools runs (item-level hit rates, bootstrap over items).

Predictions: production 11-17/20 narrated reversals on each run. Rewrite ≥ 16 and genX ≥ 17 on each run. Look-alikes flagged ≤ 2/20 for every arm on every run. The mean gain over production of each repair is above 0 with a 95% bootstrap interval excluding 0.

## Final status (2026-11-14, after round 9 and the Stage 7 audit)

- Body ends on page 8 (with Code and data and References); appendices A-F follow; the abstract is 250 words.
- Numbers: two independent full audits; every number traces to RESULTS.md and results/*.json.
- References 1-15 were verified by an agent earlier in Stage 6; no new references since.
- Consent and anonymization: no personal data (Stage 7 note above).
- Open items for the author:
  - the public code link (TODO in the Code and data section);
  - whether to run a consented study or a self-study (the only lever left for Impact);
  - the template asks that the final text be primarily written by the team.

## v11: real text (written 2026-11-14 after round 9, before the passages were collected or any run)

Why: every judge round gives Impact 3 because all positives so far are our own constructions (planted items, our paraphrases of philosophers, GPT-written fresh items). The user asked for a test on philosophers' own words. This asks whether the blind spot and the repairs hold on real writing, and how the shipped pipeline maps a real author's body of work.

Data: public-domain English texts only (pre-1930 publication or translation), fetched from Project Gutenberg, Wikisource or archive.org by a sourcing agent working from a fixed rule (paper/data/realtext_cases.json; rejects in realtext_dropped.json). Per case: an `early` passage stating the earlier view; an `announced` later passage stating the later view and saying the author changed their mind; an optional `unannounced` later passage stating the later view without saying so; a same-era `control` passage stating a different, compatible view. Verbatim only. Wittgenstein's Philosophical Investigations is still under copyright in the US, so his case can only appear through the paraphrase already in reversals.json.

Arms: production, the rewrite (defNoEmpty) and genX, exactly as in v7-v10. Haiku 5.5, same agent wrapper.

Test A (oracle pairs, 3 runs): two-excerpt requests, dated by real publication year, with the product's 400-character excerpt cut lifted (as for the hand-written set) so the whole passage is seen. Pairs: early+announced, early+unannounced (where present), early+control.
- A1: production flags early+announced in at most half of item-runs; the rewrite and genX in at least 80%.
- A2: where an unannounced passage exists, production flags early+unannounced at least 30 points more often than early+announced (the marker effect in real wording).
- A3: early+control is flagged in at most 10% of item-runs for every arm.
- Failure condition stated in advance: if the rewrite and genX both fall below 60% on early+announced, the repair does not transfer to real writing and the paper says so.

Test B (mapping a body of work, 1 run): one history per case: 60 paragraphs sampled (seed 20261114) from the early work and 60 from the later work (paragraphs of at least 200 characters), each dated in its publication year, plus the case's own passages as separate entries. Run unmodified through the shipped theme sort and request builder (20-excerpt window, 400-character cut, 60-character filter), then each arm.
- B1: the early and announced passages land in the same theme in at most 70% of cases (65% on planted data).
- B2: counts of cases where each arm surfaces the early+announced pair end to end; predicted production < genX and production < rewrite (too few cases for a test; reported as counts).
- B3: every card from every arm is labelled blind to arm (pair text only) as "a real tension or change in this author's own stated views" or "not". The labeller is a Sonnet subagent; Claude (Opus) hand-labels a random 20 for an agreement check. Reported as cards per history and share labelled real, per arm.

### v11 addendum (written after reading the sourced passages, before building or running any request)

- Cases: 7 with early + announced + control (Hume, Peirce, Nietzsche x2, Kant, Mill, Russell); 4 also have an unannounced passage (Nietzsche x2, Kant, Russell), each from the same later text as the announced one. Wittgenstein is early-only (Investigations not PD) and is not run.
- Coded before any run from the passage text alone (`announced_states_new_view`): the announced passage states the later view itself for Peirce, Nietzsche-Wagner, Mill and Russell. For Hume (confesses he cannot make his former opinions consistent), Kant ("dogmatic slumber", a new direction) and Nietzsche-comfort (regrets the Kantian and Schopenhauerian formulae) it announces a retraction without stating a view that clashes on the same point. A1's thresholds apply to the four that state the new view; the three retraction-only cases are reported apart, with no prediction.
- A2 compares unannounced and announced on the four cases that have both; since the unannounced passages are also the more direct statements of the later view in two cases (Nietzsche-comfort, Kant), A2 cannot separate the cue from directness there and is reported as descriptive.
- Dates are the original year of writing, not the translation year.
- Test B: 6 histories (Mill left out: Laughlin's abridgement mixes in the editor's own text). Each work is a fixed line span of its source file that leaves out editors' introductions, other authors' articles and licence text. Nietzsche's 1886 self-criticism has only 8 paragraphs of 200+ characters and Hume's Appendix 19, so those later works contribute fewer than 60.

## v12: model-based grouping (written after the dev run, before any held-out or real-text grouping run)

Why: on real writing the word-overlap theme sort never put a reversal's two ends in one theme (0 of 6 histories), so no prompt can surface them. Candidate fix: a cheap model pass that names, per excerpt, the one question it takes a position on (batches of 30, date order), then merges same-question wordings in one call when a history spans more than one batch. Themes are the merged groups; the shipped request builder (20-excerpt window, 400-char cut, 60-char filter) and conflict step are unchanged. Prompts frozen as v1 in evals/conflicts/gen/group_prompts.json. Model: Haiku 5.5 (cheapest; the user asked for the cheapest model that works).

Dev (t00-t11, the only tuning data, one run, v1 unchanged after it): positives in one group 26/26 (word sort 19/26); decoys in one group 21/34; 225/312 posts grouped. The merge pass never ran on dev (every dev history fits one batch), so it is untuned.

Predictions:
- G1 held-out planted (t12-t23): positives in one group >= 18/20 (word sort 11/20).
- G2 real text: early + later passage in one group for >= 6 of the 10 pairs (6 announced, 4 unannounced; word sort 0/10).
- G3 end to end, held-out planted, grouping + genX: >= 17/20 positives; <= 2/40 decoys flagged (word sort + production 9/20, + rewrite 12/20).
- G4 end to end, real text, grouping + genX: >= 5 of the 10 pairs surfaced (word sort: whatever the v11 batch gives, expected 0 since none share a theme).
- Grouping + production is also run, to separate the grouping gain from the prompt gain. Cards per history are reported for every arm and, on real text, blind-labelled as in v11 B3.
- Cost: model calls per history for grouping are reported next to the conflict calls.

## v13: a conflict prompt for real prose, and grouping v2 (written before any held-out run)

v11 showed every prompt mostly misses real reversals even when shown just the pair (genX 5/21). Failure analysis on the 7 v11 cases (now the DEV set): genX's exclusion list reads "a theory ... which I formerly held myself" as describing someone else's view, and authors rarely restate an old view in the same words.

- realX_v1 (evals/conflicts/gen/real_prompts.json) = genX + one paragraph: also count a pair when a later excerpt rejects, abandons or corrects a view an earlier excerpt states, even when it describes that view in general terms, refers back to the earlier writing, or calls it a view the writer formerly held; plus "(a view the writer says they once held is their own)" on the someone-else exclusion. One dev run (tuning data): announced 4/7 (4/4 where the announced passage states the new view; 0/3 retraction-only), unannounced 2/4, controls 0/7. Frozen after this single dev run.
- Grouping v2: v1's labels, with a merge prompt that groups questions by the issue a writer could change their mind on (aim 3-15 questions per group). Tuned on the 6 dev real-text histories only.
- HELD-OUT test set: realtext_cases2.json, sourced by an agent after v11/v12 ran, with the same rules and no thesis reused. None of its passages had been read when this was written.

Predictions:
- P1 (precision, sets realX never saw): flags <= 2/40 planted held-out decoys, <= 2/20 fresh look-alikes, <= 2/22 hand-written decoys; finds >= 18/20 fresh narrated reversals (one run).
- P2 (held-out real text, Test A, 2 runs): on cases whose announced passage states the new view, realX finds >= 60% of item-runs and genX <= 40%; controls flagged <= 10% for both.
- P3 (held-out real text, Test B): grouping v2 puts early + later in one group for >= 50% of pairs (word sort expected near 0); end to end with realX surfaces >= 40%.

### v13 addendum (after reading the held-out passages, before building or running any request)

- Held-out set: 6 cases (Darwin, Newman, Mill on socialism, Spencer, Huxley, Nietzsche on the saint), 6 announced, 3 unannounced, 6 controls; all passages script-checked verbatim inside their spans. Fewer than the 8-10 asked for.
- Coding of `announced_states_new_view` (Claude's, from the text; the agent's own coding kept as `announced_states_new_view_agent`): yes for Darwin, Spencer, Huxley; no for Newman ("utterly renounced" his view of Rome, states the old view), Mill ("cancelled ... a more advanced opinion") and Nietzsche ("Idealism is foreign to me", nothing on the saint or pity; the agent coded it yes). P2's thresholds apply to the 3 new-view cases (6 item-runs per arm), the rest reported apart.
- Arms and cost: Test A, production, genX and realX x 2 runs on 15 pairs (90 calls). Test B, word sort: same-theme counts only, no calls, since a pair in two themes cannot be surfaced; model grouping v2 (labels + merge, about 30 calls) then realX end to end (one run), so P3 measures grouping v2 + realX. genX end to end is dropped to save calls.

## Status after rounds 10-13 (2026-11-14 afternoon)

- The paper now leads with real writing: on 13 documented reversals the shipped tool surfaces none (word grouping 0/19 pairs; production prompt 5/33 tries shown the pair alone). The planted-item mechanism is compressed into one section; the repairs are reported only on items they were not chosen on (fresh planted, held-out real).
- Predictions in rounds 10-13: 12 tested, 6 failed (A1, A2, G2, genX <= 40%, grouping v2 >= 50%, end to end >= 40%), all reported in Appendix F.
- Next: mock judging round 10; then fix what it finds.

## v14: round-10 judge checks (written after mock judging round 10, before any run)

Judges: Impact 3/3/3, Execution 3.5/3/3.5, Presentation 3/3/3; no number mismatches. They asked for a field baseline on real text, a contamination probe, more runs and case-level reporting.

1. **Whole-history baseline on real text.** Each of the 12 real histories (6 development, 6 held-out) sent in one request, oldest first, 400-character excerpts, with the naive prompt ("Where does this person contradict themselves? ...") plus the standard JSON output line. 12 Haiku calls. Prediction: surfaces at most 4 of the 19 early+later pairs (on planted data a whole-history prompt fell to 16/26 at 312 posts), with more than 3 pairs returned per history.
2. **Contamination probe.** One Haiku call listing the 26 early and announced passages of the 13 cases, asking for author and work or "unknown". Prediction: correct author for at least 15 of 26.
3. **Held-out Test A, run 3** for production, genX and realX (45 calls). Prediction: each arm's run-3 count of announced pairs within 1 of its mean of runs 1-2; controls 0.

## v15: whole history with realX (written after the v14 baseline results, before any run)

v14 result: one naive call over each real history (72-124 excerpts) surfaced 7/19 pairs (held-out 4/9), 2.8 pairs per history, blind precision ~0.7 (Haiku 23/34, Sonnet 24/34): as good as grouping v2 + realX at this size. Question: is the product's best path for histories that fit in one call "whole history + realX" rather than grouping?

1. **Whole history + realX.** Same 12 requests as v14 (same user message, same excerpts), system prompt = realX_v1 verbatim. 12 Haiku calls, one run. Prediction: surfaces at least 7/19 (held-out at least 4/9); at most 2.8 pairs per history (the exclusion list is stricter than the naive prompt); controls flagged in at most 1 history.
2. **Blind card labels** for its cards, Haiku and Sonnet, same label prompt. Prediction: real share at least the naive baseline's (Haiku 23/34, Sonnet 24/34).
Failure reading: if it surfaces fewer than 7, the generic naive prompt is the better whole-history prompt and realX's value is limited to per-theme calls.

## v16: round-11 judge checks (written after mock judging round 11, before any run)

Judges: Impact 3/3/3, Execution 4/4/3, Presentation 3/3/3; no number mismatches. They asked for run-to-run ranges and pair-level tests on the whole-history headline, and noted that the v15 threshold (>= 7) was set after seeing the naive baseline.

1. **Runs 2 and 3** of whole history + naive and whole history + realX on the 12 real histories (48 Haiku calls, same inputs). Predictions: realX surfaces >= 8/19 in each of runs 2 and 3; its 3-run mean beats naive's 3-run mean by >= 1.5 pairs; realX flags a control in <= 1 history per run.
2. **Pair-level statistics** (no new calls): for each of the 19 pairs, found on a majority of the 3 runs; exact McNemar realX vs naive on that; Wilson intervals on 10/19-style counts; held-out shown separately.

## Status after mock judging rounds 11-12 (2026-11-14 ~14:30 ET)

Round 11: Impact 3/3/3, Execution 4/4/3, Presentation 3/3/3. Round 12: Impact 3/3/3.5, Execution 4/3/3.5, Presentation 3/3/3. No numeric mismatches; fixed: run-order slip, Table 4 notation, prediction tally rule, "zero false alarms" scope, harness read-depth check added. The >= 4 bar is not met. Impact has been at 3 for every round, for the reason every judge gives (one product, no users); more Haiku arms do not move it. Open levers, each the user's call: a consented user study or the author's own history; a public code link; a long-record test (300-600 excerpts) of whole history vs grouping.

## v17: constructive-judge checks (written after constructive mock judging, before any run)

1. **Production prompt on the whole history.** Same 12 requests as v14/v15, system prompt = shipped CONFLICTS_SYSTEM, 3 runs (36 Haiku calls). Separates co-location from prompt. Prediction: majority-of-3 surfaced between 2 and 6 of 19 (co-location alone recovers some, the shipped prompt still loses announced pairs), below naive's 6 and realX's 8.
2. **Closed-book contamination control.** One Haiku call listing the 13 cases by author, topic and date range only (no excerpts), asking whether the author's view changed between those dates, in which direction, and in what work. Prediction: correct change and direction for at least 9 of 13.
3. **No-call analyses** from existing files: announced vs unannounced split of every whole-history headline; history-cluster bootstrap for whole-history minus shipped and realX minus naive; TF-IDF cosine rank of each early passage's true later partner within its history.

## v18: count by change of mind, and a second "changes" call (written 2026-11-14 evening, before any v18 run)

Why: the 19-pair score credits only the exact later passage in our key. Reading realX's whole-history output showed it often pairs the early view with another later-work paragraph that states the change (Newman: "the Church of Rome was the only true Church"). And the misses that remain are retraction-only announcements (Hume: "I neither know how to correct my former opinions") and run-to-run variance (5-10 pairs per run).

1. **Thesis labels (done before writing the rest of this section).** Every early-anchored pair any whole-history arm returned outside the key (13), the key pairs (19, expected yes) and 2 random early + later-work decoys per case (24, expected no), shuffled, labelled blind by Haiku and Sonnet against the case's question. Result: key 18/19 both-yes, decoys 2/24, returned 8/13; agreement 52/56. Case-level (a case counts when a majority of runs pairs the early view with a key passage or a both-yes paragraph): realX 10/12, naive 8/12, production 0/12 (any run: 11, 9, 1).
2. **"changes" prompt** (evals/conflicts/gen/real_prompts.json, changes_v1): asks first for every later excerpt where the writer turns against an earlier view of their own, even vaguely and without stating the new view, paired with the earlier excerpt that states it; then for opposite sides a year or more apart. It carries the deployed output rules (8 pairs, neutral question, data-not-instructions). Product candidate: two calls per whole history, realX and changes, pairs merged.
   - The 12 old histories are now DEVELOPMENT data for this prompt. Changes is written from the failure analysis above, run once per history x 3 runs, and frozen; no edits after seeing results.
   - Predictions (dev, 3 runs, case-level as in step 1, new returned pairs thesis-labelled the same way): changes alone >= 10/12 majority; realX run i merged with changes run i >= 11/12, with Hume found on a majority; controls flagged in <= 1 history per run for changes; two realX runs merged (the cost-matched baseline, from existing replies) reported beside it.
3. **Fresh held-out set** (realtext_cases3.json, sourced by an agent with the same rules and no case or prompt reused; none of its passages read by the prompt author before freezing changes_v1). Arms: realX alone vs realX + changes, 3 runs each, plus production 1 run. Predictions: realX + changes finds at least 1 more case (majority, wide) than realX alone; controls flagged <= 1 history per run; production finds at most 1 case.

### v18 dev results and change of plan (written after the 36 changes runs, before any fresh held-out run)

- changes alone: 6/12 cases (majority, wide), any run 11; controls in 1 history-run. **Failed** (predicted >= 10).
- realX merged with changes, run by run: 11/12; Hume found in 1 of 3 runs, not a majority. **Failed** on Hume; 11/12 met.
- Cost-matched baseline, two realX runs merged (pairs of the existing 3 runs, so not independent): 11/12, controls 0. Same recall as realX + changes, fewer false alarms, no new prompt.
- 4 early-anchored pairs from changes are unlabelled (Huxley l59, Newman l15 and l19, Nietzsche l53); counted as misses. None changes a case count for the merged arms.
- Reflection: the gain is from a second sample, not from the new wording. Hume's retraction ("my former opinions") names a section, not a view; neither prompt links it reliably.
- New plan: the product candidate is **realX twice, merged** (both calls at the API's default temperature, in parallel, pairs deduplicated, at most 8). changes_v1 is dropped. On the fresh held-out set: 6 independent realX runs per history, scored as single runs (1-6) and as 3 disjoint merged pairs (1+2, 3+4, 5+6), plus production 1 run. Predictions: merged finds >= 1 more case (majority, wide) than single realX; controls flagged in <= 1 history per merged look; production <= 1 case.

### v18 fresh held-out results (6 new cases: Franklin, Romanes, Godwin, W. James, Freud, Gladstone)

- realX single run, majority of 6 runs: 2/6 cases (Romanes, Freud); two runs merged, 3 disjoint looks: 3/6 (+ Gladstone); production: 0/6. Prediction (merged >= single + 1; controls <= 1; production <= 1) held, but recall on new authors is far below the development set's 10-11/12.
- Failure analysis (this makes the fresh set development data for what follows): (a) Franklin: every run paired the announced retraction with OTHER paragraphs of the 1725 pamphlet (e12, e24, e17), which our early-anchored scorer does not credit; (b) Godwin and James: Persona sends only the first 400 characters of each post, and the key words fall after the cut (James's early passage stops at "do not agglomerate into a higher comp"). The product has the same cut (web conflicts.ts, excerptChars 400), so long posts are partly invisible to it.

## v18b: cross-era scoring and longer excerpts (written before any v18b run)

1. **Cross-era thesis labels.** Every returned pair with one side from the early work (early passage or e-paragraph) and the other from the later work (announced, unannounced or l-paragraph), not labelled before, blind-labelled by Haiku and Sonnet with the same prompt, with key pairs and 2 random e x l decoys per case as anchors. A case counts when a pair both labellers call "yes" (or a key pair) appears. Applied to every arm already run, dev and fresh.
2. **Longer excerpts.** Same 18 histories, realX_v1, each post cut to min(1000, 120000 // n) characters instead of 400 (967-1000 here; user message 62k-111k chars). 6 runs per history, scored single and as 3 disjoint merged looks (1+2, 3+4, 5+6). The runner lets the model read the file in several Read calls.
   - Predictions (cross-era scoring): merged long finds >= 5/6 fresh cases (majority of looks), including Godwin and James; >= 11/12 dev; controls flagged in <= 1 history per look; single long run beats single 400-char run on fresh by >= 1 case.
3. **Second fresh set** (realtext_cases4.json, being sourced by an agent; nothing from it read before freezing). The final configuration (prompt, merge, excerpt length) is tested once on it, with production as the comparison.

### v18b interim (cross-era labels done, long runs pending; written before any changes-long run)

- Cross-era labels: dev key 18/19 both-yes, decoys 0/24, returned 50/82; fresh key 10/11, decoys 2/12, returned 24/29 (1 card unlabelled by Haiku).
- Re-scored cross-era, single run, majority of runs: production dev 1/12, fresh 0/6; naive dev 10/12; realX dev 11/12 (misses Hume), fresh 4/6 (misses Godwin, James); **changes dev 12/12, Hume included** (it pairs the Appendix retraction with other Treatise paragraphs). The earlier v18 reading ("the gain is the second sample, not the wording") came from the early-anchored scorer and is withdrawn.
- Added arm: changes_v1 with long excerpts, same 18 histories, 4 runs (merged looks 1+2, 3+4). Choice of the final configuration (realX x2, changes x2, or realX + changes; all long) is made on dev + fresh1 by merged-look majority, ties to fewer controls, then cheaper; then frozen and run once on fresh2.

### v18b long results (labels: key 27/30 both-yes, decoys 1/18, returned 82/123)

Merged looks (two calls), majority, dev 12 + fresh1 6: realX-400 11 + 4; realX-long 11 + 5 (controls 0); changes-long 11 + 6; realX + changes long 11 + 6 (controls 0.25 dev, 0.75 fresh per look). Prediction "merged long >= 5/6 fresh with Godwin and James": held for changes-long and realX + changes; realX-long missed James. Prediction ">= 11/12 dev": held. Controls <= 1 per look: held. Single long beats single 400 on fresh by >= 1: held for realX (5 vs 4).
Missing cell before choosing: changes_v1 at 400 characters on fresh1 (4 runs), since it was 12/12 single on dev at 400 and the long limit costs about 2x the input. Rule unchanged.

### v18b decision (frozen before any fresh2 case is read)

changes_v1 at 400 characters on fresh1: 4/6 merged (misses Godwin, James), so the longer excerpts are what find those two. Totals (merged-look majority, dev 12 + fresh1 6): changes-400 16, realX-long 16, changes-long x2 17, realX + changes long 17. Tie broken by control flags per merged look: realX + changes 0.25 dev / 0.75 fresh, changes x2 0.5 / 1.0. (The flagged controls read as real changes on another question: Spencer on women's political rights, Romanes on theism; so the controls are not clean, and are reported as flags, not errors.)

**Final configuration:** per look, two calls in parallel, realX (deployed text) and changes_v1, pairs merged and deduplicated, at most 8; a history of up to 120 posts goes whole, each post cut to min(1000, (120000 - label) // n) characters. Persona gets exactly this (contract excerptChars 1000, totalChars 120000; web trims per history; API asks both prompts).

**Fresh2 test (one shot):** the final configuration and production, on realtext_cases4 histories; final 3 looks (6 calls) per history, production 1 run. Cross-era scoring with blind thesis labels as above (the text each model saw). Predictions: final finds >= 2/3 of fresh2 cases on a majority of looks; production finds <= 1 case; final flags a control in <= 1 history per look.

### v18c fresh2 run (written after the cases arrived, before any fresh2 request was built or run)

Fresh2 (realtext_cases4.json): Lyell on the antiquity of man, Besant on materialism and the soul, Darwin on Glen Roy, Buckland on the universal deluge, Sedgwick on diluvial theory, Lyell on the origin of species. Primary result: all 6. Sensitivity: 5, without lyell_species_origin (same two works as the other Lyell case). Darwin, Buckland and Sedgwick are OCR texts. Arms: final = the deployed realX text (CONFLICTS_SYSTEM, with output rules) and changes_v1, long excerpts, 3 runs each, look i = realX run i + changes run i; production (shipped Nov 1 prompt, 400 characters), 1 run. Predictions as above (final >= 4/6 majority of looks; production <= 1; controls <= 1 history per look).

### v18c fresh2 results

Final configuration: 6/6 cases on a majority of looks, and in all 3 looks of every history (18/18); controls flagged 0. Production: 1/6 (Buckland), controls 0. Strict key pairs: final 22/27 key-pair-looks; production 1/9. Labels: key 9/9 both-yes, decoys 0/6, returned 25/36. Sensitivity without lyell_species_origin: 5/5 vs 1/5. Applying the product's cap of 8 pairs per look (realX's pairs first, or interleaved) drops 2 pairs in 2 looks but no case (still 18/18 looks). All three predictions held.

## v19: simpler arms on the untouched set, and prior-art-style baselines (written before any v19 run)

Why (constructive judging after round 18): the fresh-set-2 test compared the deployed configuration only with the shipped prompt, so it does not show the two-prompt design is needed; and no prior-art-style method was run on our cases.

1. **Fresh set 2, simpler arms** (400-character excerpts, whole history, 3 runs each): naive, realX_v1, changes_v1. Existing replies already give realX (deployed text) and changes alone at longer excerpts (the two halves of the final configuration's looks). Fresh set 2 is no longer untouched after this; nothing is chosen on it.
   - Predictions (case level, majority of runs): realX-400 >= 4/6; changes-400 >= 4/6; naive >= 3/6; none beats the deployed configuration's 6/6; controls flagged in <= 1 history per run each.
2. **Prior-art-style prompts on all 24 histories** (400 characters, 3 runs): contradoc_style (a document self-contradiction prompt in the spirit of ContraDoc [5]) and beliefshift_style (a belief-tracking prompt in the spirit of BeliefShift [6]); our wording, same JSON output, not the papers' own code.
   - Predictions: contradoc_style finds fewer cases than realX on each set it shares with realX (dev 11, fresh1 4), because "cannot both be true" excludes announced revisions; beliefshift_style finds at least as many as realX on dev and fresh1. Neither flags controls in more than 1 history per run.
3. New early-by-later pairs labelled blind as before (Haiku and Sonnet, the case's question, the text each model saw), with key pairs and random decoys as anchors.

## v20: what the repair costs in cards (written before any v20 label exists)

Why (round-19 mock judges): recall gains were reported without the cards they cost or the share of those cards that are genuine.

Design: existing replies only, first run (or first look) per history, all 24 histories. Arms: shipped prompt (whole history, 400 characters), realX alone (400), deployed (realX + changes, longer excerpts, one look, merged and capped at 8 as Persona does). Every card (pair) is labelled blind to arm by the earlier card prompt ("a real change or tension in the author's own views": real / not), Haiku and Sonnet, shown the text the model saw. Anchors: per history the keyed early + announced pair (expect real) and the control + announced pair (expect not). Cards are shuffled across arms and split into files of about 50.
- Predictions: cards per history per look: shipped ≤ 0.5, realX 1.5-3, deployed 3-6; deployed cards hitting the 8 cap in ≤ 3 of 24 histories. Genuine share (both labellers "real"): realX ≥ 70%, deployed ≥ 60%, and deployed within 20 points of realX. Anchors: keys ≥ 20/24 real, control pairs ≤ 3/24 real.

## v21: a hard held-out set (fresh set 3), committed before any of its cases exist

Why (round-19/20 mock judges; REFLECTION after round 19): fresh set 2 could not separate the repaired configurations (simple prompts found 5-6/6), and its brief favoured passages inside the first 400 characters. The claim that the second prompt and longer excerpts matter rests on three tuning cases (Godwin, James, Hume).

Sourcing: one Sonnet agent, same method and schema as sets 1-2, not shown prompts, results or the paper. Its brief says nothing about how the tool reads text (no position or length hint). It asks for changes of mind of the kind the earlier sets show to be hard: at least 4 of 6 announced passages retract, disown or refer back to the old view without restating the new one ("my former opinion", "what I then wrote"). This aims the set at causes 3 and 4 and is disclosed as such. Target 6, stop at 8. Then nothing is chosen on it.

Arms (Haiku, whole history, 3 runs or looks each, case level by blind thesis labels as in v18b-v19): shipped prompt (400), naive (400), realX_v1 (400), changes_v1 (400), beliefshift_style (400), deployed configuration (realX_deployed + changes_v1, excerpts min(1000, 120000 / posts), merged look = run i of each).

Predictions:
- Shipped ≤ 1/6; naive ≤ 3/6; realX-400 ≤ 4/6; changes-400 ≥ realX-400.
- Deployed ≥ 4/6 and ≥ realX-400 + 1 case (the necessity test). If deployed ≤ realX-400, the paper says the second prompt and longer excerpts are not shown to help on unseen cases.
- beliefshift_style ≥ realX-400.
- Controls flagged in ≤ 1 history per run or look, every arm.

## v22: cause 2 on real text, and where retractions fail (committed before any v22 request exists)

Why: cause 2 (the shipped definition) was isolated only on planted items; judges asked for the real-text test. And every prompt misses Coleridge and Wordsworth, and realX misses Hume: we do not know whether the model fails to notice the retraction or fails to link it back.

1. **Definition swap on real text.** The shipped prompt with only the planted-item edits (same text as requests_mech2): defOnly ("each excerpt, at the time it was written, stated the person's own view"), defNoEmpty (that, and without "Most themes have none, and an empty list is the right answer then."). Whole history, 400 characters, 3 runs, all 30 histories; plus shipped runs 2-3 on fresh sets 1-2 so every history has 3 shipped runs. Case level, blind thesis labels.
   - Predictions: shipped ≤ 3/30; defOnly ≥ 8/30; defNoEmpty ≥ 14/30 and ≥ defOnly; both below realX-400's 25/30; controls ≤ 1 history per run each.
2. **Retraction-link probe** (oracle on the later end). For the 14 cases whose announced passage does not state the new view: the whole history at longer excerpts, and the instruction "Excerpt E<k> is a later passage in which the writer disowns or corrects a view of their own. Which earlier excerpts state the view it disowns? Up to 3, best first." 3 runs. Credit: the keyed early passage, or another early-work paragraph both thesis labellers call a match with the announcement.
   - Predictions: credited in top 3 on a majority of runs for ≥ 10/14; Hume credited; Coleridge and Wordsworth: at most one of the two credited (if linking fails too, those cases need a different approach than a better detection prompt).

## v23: do independently written strict prompts fail on real text too, and what does the shipped configuration cost? (committed before any v23 request)

Why (round-22 mock judges): the field-level claim ("a prompt tuned for few false alarms can return nothing") rests on our own shipped prompt; the three strict prompts GPT wrote from a brief asking for few false alarms were run only on planted items (they lost 0-4 of 36 when marked). And the paper's card cost is for the two-call configuration, which no longer ships.

1. **GPT strict prompts on real text.** gs1, gs2, gs3 (paper/data/strict_prompts_gpt.json, as run in requests_mech7), whole history, 400 characters, 3 runs, all 30 histories; case level by blind thesis labels.
   - Predictions: each finds more than the shipped prompt's 3; at least two of the three find ≤ 15/30 (below realX's 25 by ≥ 10), i.e. strict prompts in general lose real changes of mind even when they keep planted ones; controls ≤ 1 history per run.
   - If all three find ≥ 20/30, the paper says the shipped prompt was an outlier and drops the general claim.
2. **Card cost of what ships** (realX with longer excerpts, deployed text on fresh sets 2-3): existing first runs, 30 histories, blind real/not card labels as in v20 (Haiku + Sonnet), with keyed and control anchors per history.
   - Predictions: 2.5-5 cards per history; both labellers "real" on ≥ 75%; anchors: keys ≥ 26/30, controls ≤ 6/30.

## v24: what ships, tested as itself; and where the rest of the shipped prompt's loss sits (committed before any v24 request)

Why (round-23 mock judges): the shipped configuration's unseen numbers are first calls borrowed from two-call looks, with no interval or paired test; and after round 22, two edits explain 3 → 11 of 30 while realX reaches 25, so the remaining gap is unexplained.

1. **realX as shipped, its own runs**: the deployed realX text, longer excerpts (min(1000, 120000 / posts)), 3 new runs on the 12 unseen histories (fresh sets 2-3). Case level, blind labels. Wilson interval; exact McNemar against the shipped prompt (3 runs, majority).
   - Predictions: ≥ 9/12; McNemar p < 0.05 against the shipped prompt's 2/12; controls ≤ 1 history per run.
2. **Factorial cells on real text** (whole history, 400 characters, 3 runs, 30 histories): prodPara = shipped prompt + realX's retraction paragraph after its first line + "(a view the writer says they once held is their own)"; defNoEmptyPara = defNoEmpty + the same two additions; genX = realX without them.
   - Predictions: prodPara ≤ 12/30 (the "asserts both" definition still blocks); defNoEmptyPara ≥ 18/30; genX ≤ 15/30 (the paragraph, not the generic base, carries most of realX's gain); controls ≤ 1 history per run each.

## v25: does the unseen result survive masking, and does the rewrite beat a naive prompt on all 30? (committed before any v25 request or analysis output existed)

Why (round-24 mock judges, all three): the 10-of-12 unseen result may rest on Haiku recognising famous authors from names, titles and dates; the rewrite is compared with a naive prompt on only 24 cases; credit may scale with how many pairs an arm returns; headline cases mostly have an announced passage.

1. **Masked unseen histories** (fresh sets 2-3, 12 histories): in each excerpt the author's names and the titles of their own works are replaced ("the author", "my earlier book"/"an earlier work"), and dates are shifted so each history starts in 2001 with all gaps kept. Same ids, same blind labels (map x12 for new pairs, judged on the original text). Arms, 3 runs each: what ships (realX deployed text, longer excerpts) and the shipped prompt (400 characters).
   - Predictions: ships masked ≥ 8/12 and loses at most 2 of its 10 unmasked finds; shipped masked ≤ 3/12; exact McNemar ships vs shipped (masked) p < 0.05; controls ≤ 1 history per run.
2. **Naive prompt on fresh set 1** (400 characters, 3 runs), completing it on all 30.
   - Predictions: naive ≤ 4/6 on fresh set 1 and ≤ 21/30 overall; realX (400) 25/30 beats it with exact McNemar p < 0.05.
3. **From existing files, no new model calls**:
   - (a) Without the announcement: case-level credit only from pairs whose later side is not the keyed announced passage. Predictions: realX (400) 12-22 of 30; shipped prompt ≤ 2 of 30.
   - (b) Budget-matched credit: each run keeps only its first 2 returned pairs. Predictions: realX (400) ≥ 20 of 30; ships (unseen, own runs) ≥ 8 of 12.
   - (c) Harness leakage: grep every raw reply and request for answer_key, realtext_cases, "keyed", "announced" or a repository path. Prediction: 0 replies.

## v26: are the labellers right on hard negatives and on the off-key pairs that carry credit? (committed before any v26 card or label existed)

Why (round-24 judges, all three): every case-level number rests on two Claude labellers, calibrated only on keyed pairs and random decoys; credit beyond keyed pairs comes from 116 off-key early x later pairs (in realX, ships, realX_long, naive, prodPara, shipped and masked runs that had no keyed pair).

1. **Hard negatives**: each case's early-work control passage paired with its announced and (where it exists) unannounced passage (51 pairs; same author, same works, a later passage that explicitly changes view on the question, an early passage the sourcing agents coded as conflicting with neither). Haiku and Sonnet, the usual blind label prompt, mixed with the 51 keyed pairs.
   - Predictions: both-yes on hard negatives ≤ 6/51; keys ≥ 45/51.
2. **Third judge with evidence**: Opus 5.5 labels, blind and shuffled, the 116 credited off-key pairs, the 51 hard negatives and the 51 keyed pairs, with the same prompt plus: for each yes, copy the words of the later passage that reject or abandon the earlier view. A yes counts only if the quote appears verbatim. Passages are shown up to 1,000 characters.
   - Predictions: Opus yes on keys ≥ 45/51; on hard negatives ≤ 5/51; on the 116 credited pairs ≥ 80%.
   - Rescoring with Opus agreement also required on off-key pairs: realX (400) ≥ 23/30; ships unseen ≥ 9/12; shipped ≤ 3; naive ≥ 17/30.

## v27: what each prompt costs in non-genuine cards, the naive prompt at longer excerpts, and recall vs memory on the later sets (committed before any v27 request, card or label existed)

Why (round-26 mock judges): is the shipped prompt a design trade-off (on a recall vs false-card frontier) or dominated; is the rewrite better than a naive prompt on precision if not on recall; is naive held back only by the 400-character cut; do the later sets' finds rest on recall from memory.

1. **Naive prompt, longer excerpts** (min(1000, 120000 / posts)), 30 histories, 3 runs, case level, blind thesis labels for new pairs.
   - Predictions: ≥ 22/30; controls ≤ 1 history per run.
2. **Card cost, every main prompt, all 30 histories, first run, capped at 8 as Persona does**: shipped, naive (400), naive (longer), realX (400), shipped + paragraph (prodPara), GPT strict gs2, what ships. One fresh batch of the round-20 blind real/not label prompt (Haiku and Sonnet; a card counts as genuine when both say real), plus a keyed and a control anchor per history.
   - Predictions: non-genuine cards per history: shipped ≤ 0.1, naive (400) ≥ 0.6, prodPara ≤ 0.3; realX (400) has a genuine share at least 5 points above naive (400); what ships at least 5 points above naive (longer).
3. **Closed-book probe on the 17 later cases** (fresh sets 1-3; author, years, question; one Haiku call, the round-17 prompt).
   - Predictions: Haiku states the documented change and its direction for ≤ 9 of 17; what ships finds ≥ 70% of the later cases it could not state.
4. **Clustered test** (existing replies): the unseen comparison of what ships against the shipped prompt as a sign test over authors (Lyell's two cases counted once).
   - Prediction: p < 0.05.

## v28: false alarms on writing with no documented change; a one-line change-of-mind prompt; intervals on the precision gap (committed before any v28 request, card or label existed)

Why (round-27 mock judges): the only real-text false-alarm evidence is one control passage per history and Claude "genuine" labels on histories that do contain a change; the rewrite's precision lead over the naive prompt has no interval; the naive prompt asks for views that "cannot both be true", so a one-line prompt asking directly for changes of mind is the fairer simple baseline.

1. **No-change histories**: for each of the 30 cases, the early work's sampled paragraphs only (keyed early and control passages removed), in their original order, redated evenly across six years, so a reader sees an "early" and a "late" half with no documented change between them. One run each, as a user would see it: shipped, naive (400), realX (400), what ships (realX deployed text, longer excerpts), and the change-of-mind prompt below (400). Cards capped at 8, labelled with the round-27 real/not prompt (Haiku + Sonnet, one batch).
   - Predictions (cards per history): shipped ≤ 0.2; naive ≥ 1.5; realX (400) ≤ 1.0; what ships ≤ 1.5; realX (400) non-genuine cards per history at most half of naive's.
2. **Change-of-mind one-liner** ("Where has this person changed their mind? List every pair of posts in which a later post gives up, reverses or rejects a view stated in an earlier post", same output format), 30 real histories, 400 characters, 3 runs, case level, blind thesis labels; first-run cards labelled with the round-27 prompt.
   - Predictions: 22-28 of 30; non-genuine cards per history ≥ 0.8; controls ≤ 1 history per run.
3. **Bootstrap over histories** (10,000 resamples, round-27 cards): realX (400) minus naive (400) genuine share and non-genuine cards per history.
   - Prediction: both 95% intervals exclude 0.

## v29: should Persona go back to 400-character excerpts? A product decision with its rule written first (committed before any v29 request existed)

Why (round 28): with longer excerpts, what ships raised 1.10 non-genuine cards per history on writing with no documented change and 1.00 on real histories, against 0.27 and 0.50 for realX at 400 characters, for one case more (26 vs 25). But the 400-character arm used the tested realX text, not the deployed text (which adds the shipped output rules), so the exact candidate is untested.

Candidate: the deployed CONFLICTS_SYSTEM text (realX_deployed) with every excerpt cut to 400 characters, whole history in one call.
1. Real histories, 30, 3 runs, case level, blind thesis labels; first-run cards labelled with the round-27 real/not prompt.
2. No-change histories, 30, one run, cards labelled the same way.

Decision rule: switch Persona to 400-character excerpts if and only if the candidate (a) finds ≥ 24 of 30 cases and ≥ 9 of the 12 unseen, (b) raises ≤ 0.7 non-genuine cards per history on the real histories, and (c) raises ≤ 0.5 on the no-change histories. Otherwise keep what ships.
- Predictions: (a) 24-26 of 30 and 10 of 12 unseen; (b) 0.4-0.7; (c) 0.2-0.5; so the rule says switch.

## v30: does the "at most 8 pairs" line cause the deployed prompt's false alarms? A second product decision with its rule written first (committed before any v30 request existed)

Why (round 29): at 400 characters the deployed text raised 0.67 non-genuine cards per history on no-change writing against 0.27 for the tested text; the deployed text adds "Return at most 8 pairs, the sharpest first." (redundant: Persona already keeps at most 8 cards), the question format and an injection guard.

Candidate (depNoCap): the deployed text with only the line "Return at most 8 pairs, the sharpest first." removed, at the product's longer excerpts (min(1000, 120,000 / posts)), whole history in one call. Real histories 3 runs, case level, blind thesis labels; first-run cards and no-change histories (one run) labelled with the round-27 real/not prompt, one batch.

Decision rule: ship depNoCap if and only if (a) it finds ≥ 25 of 30 cases and ≥ 10 of the 12 unseen, (b) raises ≤ 0.8 non-genuine cards per history on the real histories, and (c) ≤ 0.6 on the no-change histories. Otherwise keep what ships.
- Predictions: (a) 25-27 and 10-11 unseen; (b) 0.5-0.8; (c) 0.3-0.6; so the rule says ship.

## v31: what Persona now runs, without the passage that announces the change (committed before any v31 request existed)

Why (judge look 4): the only evidence on how much finding rests on the announcing passage is post-hoc (credit not counting that passage) and on realX at 400 characters, not on what Persona runs; and a post-hoc cut leaves the passage in the model's input, where it may steer which other pairs it returns. A person's record usually holds no sentence saying "I was wrong".

1. **Post-hoc, existing runs**: depNoCap (round 30, 3 runs) credited without any pair that uses the announced passage.
   - Prediction: 12-16 of 30 (realX at 400: 14).
2. **Announcement removed from the input**: each of the 30 real histories with its announced post deleted (unannounced and later-work paragraphs kept), depNoCap at the product's longer excerpts, whole history in one call, 3 runs, case level; new cross-era pairs labelled blind (Haiku + Sonnet, thesis prompt, map x18).
   - Predictions: 12-17 of 30; 4-7 of the 12 unseen; within 2 cases of item 1's count; controls ≤ 1 history per run.
No product decision rides on this round.

## v32: one labelling batch for every main prompt, without Haiku; credit at a matched card budget (committed before any v32 label file existed)

Why (judge look 5): the genuine shares in Table 4 come from four labelling batches (rounds 27-30) whose anchors and decoy rates drift, so 87% (Persona now, round 30) against 47% (naive, round 27) is not like-for-like; and Haiku, the model under test, is one of the two labellers. Case credit may also favour prompts that return more pairs.

1. **Single relabel**: every first-run card (capped at 8) from shipped (400), shipped + paragraph, naive (400), realX (400), change-of-mind one-liner (400) and Persona now (depNoCap, longer) on the 30 real histories, plus their no-change cards (rounds 28 and 30), plus a key and a control anchor per history; one shuffled batch, the round-27 real/not prompt, labelled by Sonnet and by Opus. Genuine = both say real.
   - Predictions: Persona now genuine share ≥ naive's + 25 points; Persona now non-genuine per history ≤ 0.5 and naive ≥ 1.0 on real histories; the ordering of non-genuine cards per history on real histories is shipped ≤ Persona now < realX (400) < one-liner < naive; key anchors ≥ 25 of 30 real, control anchors ≤ 6 of 30.
2. **Matched budget**: case credit (existing runs and labels) counting only each run's first returned pair (k = 1) and first two (k = 2), for shipped, naive, one-liner, realX (400) and Persona now.
   - Predictions: at k = 1, Persona now ≥ 22 of 30 and naive ≤ 18; Persona now's lead over naive at k = 1 ≥ its lead with all pairs (6).
No product decision rides on this round.

## v33: recall split by what the model can state from memory (committed before the split was computed)

Why (judge look 5, round-32 reflection): the cases are famous authors; a prompt could find changes the model already knows about. The closed-book probes (rounds 17 and 27; author, years and question only) split the 30 cases into 14 whose change Haiku stated and 16 it did not (dev: stated Nietzsche x3, Kant, Mill socialism, Russell; later sets: Freud, Gladstone, Lyell antiquity, Besant, Darwin Glen Roy, Sedgwick, Newton, Coleridge).
- From existing runs and labels (case level, majority of runs), for shipped, naive (400), one-liner, realX (400) and Persona now: cases found among the 14 stated and among the 16 not stated.
- Predictions: Persona now ≥ 12 of 16 not stated; naive ≤ 10 of 16 not stated; for every prompt the found share among not-stated cases is within 20 points of its share among stated cases (memory is not what the prompts run on).

## v34: a planted canary inside each real history, shipped prompt, agent harness (committed before any v34 request existed)

Why (judge look 5): the shipped prompt's 3 of 30 could be an artefact of running it through an agent that reads a long file, not of the prompt. Positive control: into each of the 30 real histories insert one planted unsignalled reversal from the test set (P1, P2, P4 in order; the 36 that the shipped prompt found 36 of 36 when shown as a pair), post a dated at the 25th percentile of the history's dates and post b at the 75th; shipped prompt, 400-character excerpts, whole history in one call, 3 runs, same harness.
- Predictions: the canary pair is returned on a majority of runs in ≥ 26 of 30 histories; the shipped prompt still finds ≤ 4 of the 30 documented changes; ≤ 1 history per run returns a pair joining a canary post to a real post.

## v35: does the result hold on a second model? Sonnet on the 12 unseen cases (committed before any v35 request existed)

Why (judge look 6): every detection run used Haiku; the claim is about prompts, so it should survive a stronger model of the same family. Sonnet 5.5 through the same harness, the 12 unseen histories (fresh sets 2 and 3), shipped prompt (400 characters) and what Persona runs (longer excerpts), 3 runs each, case level; new cross-era pairs labelled blind (Haiku + Sonnet thesis prompt, map x19).
- Predictions: Persona now ≥ 9 of 12; shipped ≤ 4 of 12; Persona now finds at least 5 more than shipped; controls ≤ 1 history per run for each.

## v36: false cards on two-work histories with the documented change removed (committed before any v36 request existed)

Why (judge look 6): the no-change test (round 28) used one work redated across six years; a person's record spans works and years. Here each real history keeps both works but loses its keyed early, announced and unannounced passages (control kept), so no documented change remains, though the later work may hold other, undocumented changes. Persona now (longer excerpts) and naive (400), one run each, whole history; first-run cards (capped at 8) labelled by Sonnet and Opus with the round-27 real/not prompt in one batch, plus a control anchor per history paired with its first later-work paragraph.
- Predictions: Persona now ≤ 0.5 non-genuine cards per history, naive ≥ 1.0; Persona now's genuine share ≥ naive's + 20 points; Persona now ≥ 0.5 genuine cards per history (undocumented changes the later works do contain).

## v37: fresh set 4, sourced after Persona's current prompt shipped, run once (brief and predictions committed before any case exists)

Why (judge looks 5-6): only 12 cases were unseen when tested, one set easy. A fourth set is sourced by a new agent with no hint about how the tool reads text and no constraint on retraction type (brief: paper/data/fresh4_brief.txt), after main 2a5e359e. Run once: shipped prompt (400 characters) and what Persona runs (longer excerpts), whole history, 3 runs each, Haiku, case level; new cross-era pairs labelled blind (Haiku + Sonnet, thesis prompt). No prompt or configuration will change on this set.
- Predictions (n = cases kept, 6-10): Persona now finds ≥ 70% of n; shipped ≤ 25% of n; Persona now finds at least 3 more than shipped; controls ≤ 1 history per run for each.

## v38: require a verbatim quote for every card? A product decision with its rule written first (committed before any v38 request existed)

Why (round 36): with no clear change to report, Persona's prompt reaches for weaker pairs (0.60 non-genuine cards per history on two-work histories without the documented change). Asking for evidence may drop the weak ones. Candidate (depQuote): Persona's current prompt plus one field, "quote": the words of the later excerpt that reject, abandon or clash with the earlier view, copied exactly, and "If you cannot quote such words, leave the pair out." Longer excerpts, whole history. Real histories (30, 3 runs, case level, blind thesis labels, map x20) and the round-36 two-work histories (30, one run). First-run cards of depQuote and of Persona's current prompt on both, labelled together in one shuffled Sonnet + Opus batch (round-27 real/not prompt).

Decision rule: ship depQuote if and only if (a) it finds ≥ 25 of 30 and ≥ 10 of the 12 unseen; (b) its non-genuine cards per history on the two-work histories are ≤ 0.45 and lower than the current prompt's in the same batch; (c) on real histories ≤ 0.30. Otherwise keep the current prompt.
- Predictions: (a) 24-26 and 10 of 12; (b) 0.30-0.45; (c) 0.15-0.30; so the rule says ship. Also: ≥ 90% of returned quotes appear verbatim in the later excerpt.

## v39: Persona's whole-history gate, a product decision (committed before the product change)

Why (judge look 7): Persona sends a history in one call only up to LIMITS.excerpts = 120 posts; past that it falls back to word themes, which joined 0 of 19 keyed pairs. 29 of the 37 test histories have 123-124 posts, so in the product they would have taken the fallback, not the evaluated path. Rule (no new runs): raise the gate to 124, the largest history every result here was measured on, because the per-call cost bound (totalChars, 120,000) is unchanged and per-post excerpts shrink with history size exactly as evaluated (min(1000, 120,000 / posts)). Do not go higher: nothing above 124 posts was tested. The paper states plainly that records longer than the gate still take the word-theme path.
