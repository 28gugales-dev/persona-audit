# How to win Track 3 (merged from research/track3.md and research/winners.md)

Sources are the two research files; every line below names the URL it rests on. Where a source was only a fetch summary or not opened, it says so.

Sprint page (rubric, track text, requirements): https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15

## 1. Rubric (each 1-5, published on the sprint page, Guidelines tab)

| Criterion | What a 3 looks like | What a 4-5 needs |
|---|---|---|
| Impact Potential & Innovation | "some novelty in framing or method" | 4: "identifies a neglected problem area"; 5: "opens a new research direction"; and the check "is this actually new to the field, or replicating recent work?" |
| Execution Quality | "Technically solid given the short duration", limitations acknowledged | 4: "convincing validation", "immediately useful for future work"; 5: "unusually robust validation" |
| Presentation & Clarity | problem, method, findings, limitations all present | 4: "target audience would get it quickly" |

Hard requirements (same page): Apart template (Google Doc), at most 8 pages excluding references and appendices, abstract 150-250 words, appendix titled "Limitations and Dual-Use / Ethical Considerations", disclose pre-existing work, no made-up results or references (can disqualify). Deadline Sun Nov 15 2026 23:59 AoE.

Track 3 text (sprint page, Overview): judges ask whether tools lead to "choices they later endorse", and say "epistemic benefits have to be accompanied by products people actually want". Listed examples: Crux Mapper (inconsistencies and cruxes in group beliefs), Dispute Escalation Benchmark, Decision-Brief Rubric. Framing resources: Angels-on-the-Shoulder (https://www.forethought.org/research/design-sketches-angels-on-the-shoulder), Guardian Angels (https://gwern.net/guardian-angel).

## 2. What winners share (research/winners.md, 14 projects, 7 PDFs read)

1. Abstract leads with the finding and its numbers (Serve, Syco-Lingual, search-deception PDFs). Common, not required: LidaSim won 1st without numbers (https://apartresearch.com/sprints/projects/lidasim-testing-ai-policies-with-personabased-simulations-o8x6).
2. Narrow scope, one measurable claim, one new axis; reviewers praise "tightly scoped, reproducible" (https://apartresearch.com/sprints/projects/eliciting-deception-on-generative-search-engines-6nuu).
3. The same three reviewer complaints recur: one LLM judge with no human check, no significance tests, small n / one seed (Serve, Syco-Lingual, search-deception review pages). Serve was praised for checking its AI judge against human raters (r=0.83) (https://apartresearch.com/sprints/projects/who-does-your-ai-serve-manipulation-by-and-of-ai-assistants-77xx).
4. Prototypes are judged on validation against ground truth, not build quality. LidaSim and AIRAS were both docked for no link to real outcomes (LidaSim page; https://apartresearch.com/sprints/projects/political-intelligence-for-ai-safety-the-ai-risk-attitudes-survey-airas-dlpz). Ask First did well with a programmatic grader and twin-pair design (https://apartresearch.com/sprints/projects/when-to-ask-an-rl-environment-that-teaches-ai-agents-to-act-on-what-users-mean-and-not-just-what-they-say-1fuf).
5. Honest negatives and preregistered predictions place well: Project Anchored 2nd (https://apartresearch.com/sprints/projects/project-anchored-q4fn), Zhu 3rd with six failed predictions reported (https://apartresearch.com/sprints/projects/model-instance-or-persona-measuring-aective-signals-in-public-text-after-an-ai-is-retired-hj7u).
6. Dense: ~3,000-4,000 words, 4-8 figures/tables, limitations appendix in every winning PDF read. The 8-page cap is tighter than 5 of 7 past winners.
7. No past winner found that measured user endorsement of a product's output (absence in what was read, not proof).

Structure to borrow: twin/paired design with a programmatic answer key (Ask First), a judge validated against human labels with a reported agreement number (Serve), preregistration and reported negatives (Anchored, Zhu), numbers in the abstract (Serve).

## 3. Closest prior work a judge will compare with (research/track3.md)

- ELEPHANT, social sycophancy; models affirm both sides of a moral conflict ~48% of the time (https://arxiv.org/abs/2505.13995). Any "AI agreed both times" result must be distinguished from this.
- Sharma et al. 2023, sycophancy (https://arxiv.org/abs/2310.13548); SycEval (https://arxiv.org/abs/2502.08177); Cheng et al. 2025, sycophancy lowers repair intent and users prefer it (https://arxiv.org/abs/2510.01395).
- BeliefBank, consistency of a model's own beliefs (https://arxiv.org/abs/2109.14723); Vasileiou et al. 2025, how people revise inconsistent beliefs (https://arxiv.org/abs/2506.09977).
- We found no published tool that mines a person's own writing for contradictions over time and separates a change of mind from a live tension (a few searches; say "we found no").

## 4. The five critiques a judge is most likely to make about Amphi

1. **"No evidence anyone later endorses what it flags."** Track 3's own question; LidaSim was docked for no ground truth. Answer: an external, self-published endorsement answer key (philosophers who said in print they changed their minds), planted conflicts with known truth, and an honest statement that a consented user study is not done.
2. **"The LLM judge is unvalidated."** Recurring complaint (pattern 3). Answer: keep the main metrics programmatic (planted answer key); where a judge is needed, report agreement against hand labels and a second judge from another model family.
3. **"Synthetic data, small n, no significance tests."** Answer: bootstrap CIs on every rate, paired comparisons with exact/McNemar tests, n stated, synthetic sets built from PhilPapers-contested questions (not toy facts), and decoys that look like conflicts but are not.
4. **"Not new: sycophancy is well studied."** Rubric novelty check; ELEPHANT. Answer: the contribution is the product question (does a reflection tool built on a person's own record find real changes of mind without nudging), not another sycophancy rate; sycophancy appears only as one small check.
5. **"A pre-existing app with a demo, not research; and is it something people want?"** Requirements demand disclosure; Track 3 wants products people actually want. Answer: a clear before/during-sprint table, the paper's contribution is the evaluation, and an on-device mode that works with nothing leaving the browser (the privacy reason people would use it). No usage numbers are claimed unless sourced.
