# Planner review of PLAN.md (feasibility and sequencing)

Verdict: the main question is still answered in part (Q1/Q2 give an answer key; "later endorsed" is only proxied). Doable in ~50h only if the model-call volume is cut about 4x and the generator is frozen early. Facts checked in code: sortLibrary makes themes (JOIN_AT/MERGE_AT thresholds, MIN_COMMON=8), conflictRequests spreads <=20 excerpts of <=400 chars per theme, found<=3, `evals/conflicts/src/probe.test.ts` already imports all four product modules (the harness works).

1. **Themes for synthetic histories are unspecified, and this is the build blocker.** Plan says "theme sort" but never says whether planted pairs share a theme. Fix: run the real `sortLibrary` on every synthetic history; record per planted pair `sharedTheme` (bool). Report "pairs that never reach the model" as its own Q3 number, separate from model recall (conditional recall = found / sharedTheme). First hour: smoke-test sortLibrary on a 30-entry history; with MIN_COMMON=8 and short entries it may give one giant theme or none. If degenerate, make each topic 6-10 entries with topic words repeated (and say so), not a hack in product code.

2. **Model-call budget is not stated and is too big.** 60 histories x ~4 themes = ~240 Haiku subagent calls, each a spawn, plus DeepSeek, plus naive. Fix: fix n now: 24 synthetic histories (about 90 requests), 12 reversal cases (about 20 requests, one theme each), naive baseline on 12 histories. Haiku subagents: one fresh subagent per batch of 6 requests with the instruction to treat each independently is leaky; use one request per subagent, 8 in parallel, request/response as JSON files in the scratchpad. Put the bulk (full set, cross-family) on opencode DeepSeek through a script, run in parallel; Haiku on reversals plus a 12-history subset. Say which numbers come from which model.

3. **Paraphrase and decoy label leakage.** Plan says "one paraphrase pass for P2" without blinding. Fix: the paraphraser sees only one claim and the instruction "restate in casual first person with different vocabulary", never the pair or label. Check overlap with a script (Jaccard < 0.2 on content words). Decoy verification: a different model family (Codex GPT) labels a shuffled 100-pair sample blind as conflict/not-conflict; report agreement; drop items it disagrees on. Hand check 40 stays. Drop D4 (refinement) and D6 if blind agreement < 0.8, since they are arguable.

4. **Circularity in Q1 kind and P3.** `conflictKind` is code: >=365 days apart or a regex ("used to", "no longer", "I now think"). We author the dates, so "filed as a change of mind" tests our dates. Fix: report kind only as a unit-level property (a small table of regex/gap cases), and for reversals vary the gap (6 months, 3 years) and phrase with and without markers; report that `shift` is determined by gap and wording by construction. Do not count P3 recall as a finding for the model (the regex fires by design); it is a sanity row.

5. **Reversals set is the riskiest item and is scheduled in the wrong place.** The research agent can fabricate dates or quotes (no made-up results can disqualify). Fix: build it first, in parallel with the generator; every case needs two URLs and the later-endorsement sentence verified by a second agent fetching the page; drop any case it cannot confirm. Plan for 10, not 14. Controls: write them with the same agent but require "does not conflict with either".

6. **Statistics oversize for n.** McNemar on 24 histories per decoy type is thin. Fix: pool decoys; bootstrap over histories; report effect sizes, no p-value claims for subgroup cells.

7. **Q4 and Q5 are over-scoped.** Q4 needs the model outputs from items 2 (free, reuse them); the judge (GPT) plus 40 hand labels is feasible but the 40 labels cost an hour of the person's time. Fix: hand label 30, second judge optional. Q5: keep as one paragraph citing the existing pilot; no new runs.

8. **Disk (1.1GB free).** Run no new node_modules installs; `evals/conflicts/node_modules` is empty, so imports resolve via the repo root. Keep outputs as JSONL, no large model caches, no Remotion, no browser downloads; delete the scratchpad after each stage.

## Order (hours from now)
0-3: smoke test sortLibrary; freeze generator spec and data schema; start reversals research agent. 3-9: generator + scripted label checks + Local run on all (deterministic). 9-14: blind decoy check + hand check; reversals verified. 14-26: model runs (DeepSeek bulk in the background; Haiku reversals + subset). 26-32: Q3 analytic + conditional recall; Q4 judge. 32-40: figures, tables, stats. 40-48: write (8 pages incl. disclosure table, abstract with numbers, limitations appendix). Last 2h: no new runs.

## Cut list (in order)
Prompt injection, Q5 extension, second judge, cross-family on all (keep reversals + 12 histories), random-pair baseline (analytic).

## Add
A "theme-reach" table (item 1) is the strongest cheap finding. Also a one-line limitation that "later endorsed" is proxied by self-published reversals and that no end-user study was run.

AGREED WITH SKEPTIC:
- Kind circularity (item 4): agreed; `conflictKind` is date/regex by construction.
- Decoy and paraphrase leakage (item 3): agreed, and it goes further. The decoys D1-D5 mirror the detector's own regexes (REPORTED, HEDGE, "?" skip, the "moral realism"/"moral luck" comment) and the prompt's "do not count" list, so templated decoys test the code against its own spec. Adopt its fix: decoys written blind to the code by another model family from label definitions only, plus a small hand-written adversarial set (reported view later adopted, hedge that is still a reversal, sarcasm, negated refinement); report template vs blind decoys separately.
- Theme-miss vs model-miss (item 1): agreed.
- Added from skeptic, which I accept: (a) freeze an inclusion rule for reversals before running (take every hit), strip names/era terms, run one arm with change markers stripped, add hard same-era same-topic compatible controls, and a "who wrote this?" contamination probe; (b) rename Q1 to "recovers self-endorsed revisions", since endorsement is of the change, not of the flag; report per-type rates, not pooled precision (the positive:decoy ratio is ours); (c) label Haiku "in agent harness" and log repeat-run agreement. Its tiny consented self-study (author's own history, labels written before seeing flags) is feasible in about 2h and is the only real-endorsement datapoint; I would add it, but only if the author consents in chat.
- Cost note: the blind decoy generation and contamination probe add roughly 30 more calls; pay for them by cutting the random-pair baseline and the second judge.
