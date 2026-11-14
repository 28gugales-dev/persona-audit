# Novelty review (critic-novelty)

Method: 11 web searches, 6 pages opened (WebFetch returns a condensed view, so "the paper does not say" below means "the summary did not say"; check full text before asserting absence in the paper). Searches used wording close to each candidate finding.

## Top 3 strongest (most novel)

1. **Explicit revision cue switches off detection (Q1).** 9/10 plain vs 2/10 with "I've changed my mind", 7-0 discordant, McNemar p=0.016, one-line fix gives 10/10. We found no study of this in 3 searches. The closest are BeliefShift (separates contradiction from evidence-driven revision, but its summary reports no result on revision-framed statements) and FactTrack (validity intervals so change is not flagged, a design choice, not a measured LLM failure). Honest limits: n=10, Haiku named the author in 9/10, and the production prompt itself says "do not count more careful wording", so this is partly a prompt-rule finding. Claim it as an audited failure of a shipped prompt; say it needs a second prompt/model to generalise.
2. **Pipeline-loss audit before the model (Q3).** Theme grouping keeps 30/46 positives together; the 20-excerpt window covers 44% of pairs at 30 entries and 1% at 200. Retrieval-then-LLM losses are known in general (the Obsidian Contradiction Finder states its own limits: first 1500 characters, pairwise only, cosine threshold 0.80), but we found no measurement on a personal-record pipeline with a planted key. Engineering-grade novelty. Do not lean on naive vs pipeline: p=0.125.
3. **Neutrality of the generated question (Q4).** 116/120 neutral with a validated judge (kappa 0.94, 12/12 planted leans). We found no study measuring lean in LLM-written reflective prompts in 1 search (a Socratic question-generation paper scores clarity and depth with an LLM judge, not neutrality). A neglected axis, but the result is a near-ceiling null.

## Top 3 weakest

1. **Sycophancy / "AI agreed both times" (Q5).** ELEPHANT already reports 48% both-sides affirmation (https://arxiv.org/abs/2505.13995). Ours is a 60-pair pilot at 1.7-5%, a different measurement, and the on-device reader has kappa 0.02. Cut to one limitations sentence, or one line separating it from ELEPHANT. The two numbers invite a bad comparison.
2. **"Models find planted conflicts" (Q2: 36/36 unsignalled, decoys 0/80).** ContraDoc and BeliefShift already show LLMs detect contradictions; ceiling on synthetic text discriminates nothing. Shrink to a testbed-validity row. Report the dead on-device (0/46) and overlap (2/46) arms in one line as floors, not findings.
3. **"Later endorse" framing of the reversals.** It is a proxy (public self-reports, contamination 9/10, n=10). The 365-day "change of mind" label is mechanism only. Reframe as "detection of publicly self-reported reversals" and drop "endorsement" from claims.

## Closest prior work, and the gap

BeliefShift (agent-user dialogue, 2,400 trajectories, 60% LLM-generated, real logs listed as future work) is the nearest benchmark. We differ on personal writing archives, decoys that look like conflicts, and the product pipeline. Nothing found that audits a deployed personal-record tool.

## Best honest one-sentence framing

"We audit a shipped reflection tool that mines a person's own record for changes of mind, and find its failures sit around the model, not in its judgment: an explicit 'I changed my mind' cue switched detection off in the production prompt (9/10 to 2/10, exact p=0.016), grouping and windowing dropped a third or more of conflicts before the model saw them, and the questions it wrote stayed neutral (97%)."

## Agreements with other critics
- critic-methods: strongest = marker contrast (paired within case, so contamination does not confound it), Q3 losses, Q4 neutrality. Same three as mine. Weakest = the "fix" (held-out P3 n=4, H2 regresses 6/6 to 4/6, sarcasm 1/5, never run end to end, freeze not checkable from git), reversal recall as proxy, naive vs pipeline (p=0.125). Agree on two of three; I add the fix point: present the fix as a pointer, not a validated result. My extra weak items (sycophancy vs ELEPHANT, ceiling data) are novelty points they did not list.
- critic-judge: marker effect and staged loss strongest; ceiling data and endorsement proxy weakest. Agree. Their naive-flood point is a product argument for grouping, not a precision gap.

## References (opened unless marked)
- BeliefShift, Myakala et al., https://arxiv.org/abs/2603.23848
- ContraDoc, Li, Raheja, Kumar, NAACL 2024, https://arxiv.org/abs/2311.09182
- CONFLICTS / DRAGged into Conflicts, Cattan et al., https://arxiv.org/abs/2506.08500 (taxonomy types not confirmed)
- ELEPHANT, Cheng et al., https://arxiv.org/abs/2505.13995
- FactTrack, Lyu et al., https://arxiv.org/abs/2407.16347
- Obsidian Contradiction Finder, https://www.obsidianstats.com/plugins/contradiction-finder
- Search-snippet only, not opened: RAG contradiction detection https://arxiv.org/abs/2504.00180; evolveQA https://arxiv.org/abs/2510.19172; Socratic question generation https://arxiv.org/abs/2601.14798; TempoFormer https://arxiv.org/abs/2408.15689
