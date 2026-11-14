# PLAN (v1, 2026-11-14, Stage 2)

## Main question

Does Persona's belief mapping help people notice where their own views conflict or have changed, in ways they would later agree with?

We cannot run a consented user study this weekend (no written consent in hand), so the paper answers the parts of the question that have an answer key:

- **Q1 (finds what the person later endorsed).** When a person's record contains a change of mind that they themselves later endorsed in print, does Persona find it, and file it as a change of mind rather than a live contradiction?
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
