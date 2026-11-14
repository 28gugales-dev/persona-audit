# Apart "AI x Epistemics" sprint: Track 3 research notes (researcher B)

Researched 2026-11-14. Every claim cites a URL that was opened (via WebFetch, which returns a model-condensed view of the page, so quoted phrases are as relayed by the fetch tool). Unreachable pages are listed at the bottom.

Main source (sprint page, Overview / Guidelines / Resources tabs):
https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15

## 1. Judging rubric (as published, Guidelines tab)

Three dimensions, each scored 1 to 5. Source: the sprint page above.

1. Impact Potential & Innovation. "How much would this matter for the field if it worked?" Also "is this actually new to the field, or replicating recent work?" for scores of 4-5.
   - 1 Negligible, 2 Limited ("generic or well-trodden approach"), 3 Moderate ("some novelty in framing or method"), 4 Significant ("identifies a neglected problem area"), 5 Exceptional ("opens a new research direction").
2. Execution Quality. "How sound are methodology, implementation, and findings?"
   - 1 Seriously flawed, 2 Weak ("missing validation, flawed experimental design"), 3 Competent ("Technically solid given the short duration", "limitations acknowledged"), 4 Strong ("convincing validation", "Immediately useful for future work"), 5 Exceptional ("unusually robust validation").
3. Presentation & Clarity. "How clearly are work, findings, and impact potential communicated?"
   - 1 Incomprehensible, 2 Hard to follow ("Key information buried"), 3 Clear enough ("problem, method, findings, limitations"), 4 Well presented ("Target audience would get it quickly"), 5 Exceptionally clear.

Prizes: $2,000 total ($1,000 / $500 / $300 / $100 / $100), plus fellowship fast-track and mentor introductions. Top teams are invited to apply to the Apart Fellowship. Same page.

## 2. What Track 3 judges want

Track 3, "Epistemic Products" (same page). Key questions the page poses:
- Does advice users act on lead to choices they later endorse?
- Do chatbots escalate or de-escalate disputes?
- Do decision briefings surface the considerations that matter, and how can you tell?
- Does surfacing inconsistencies and cruxes in group beliefs change decisions?

Framing: "angels-on-the-shoulder" designs (deep pre-decision briefings, reflection scaffolding, guardian agents). Key sentence (Overview tab, as relayed): "People may not adopt a tool solely because it improves their epistemics, so the epistemic benefits have to be accompanied by products people actually want." This sentence is in the track description, not in the rubric.

Listed example projects (Track 3):
- Dispute Escalation Benchmark: scenario tests of whether chatbots push toward repair or escalation, mediator-defined rubrics.
- Decision-Brief Rubric: expert-defined rubric plus harness for grading briefings.
- Crux Mapper: asynchronous AI interviews extracting claims and probabilities, then mapping shared ground, cruxes and inconsistencies.

Closest fits to Amphi: Crux Mapper (inconsistencies in beliefs, but group-level; Amphi is individual and longitudinal), the Dispute Escalation example (sycophancy affecting conflict), and the angels-on-the-shoulder "reflection scaffolding". Track 1 also lists "gaps between implied and defended positions", which is adjacent.

Implication for the paper (my inference, not from the page): the rubric rewards a validated claim (Execution), a clearly new angle (Innovation), and a readable limitations section. A product demo alone has no explicit rubric credit; evidence that people want and endorse the output does.

## 3. Submission requirements

All from the sprint page (Guidelines tab):
- Research report as PDF in the official template (Google Doc, copy link): https://docs.google.com/document/d/17b3JWki-ZkaqdmqGI5d0gof-HwlGuWU9Mc1_klNZXKs/copy?usp=sharing (link as listed on the page; I did not open the doc itself).
- Max 8 pages, not counting references and appendices.
- Title and abstract of 150 to 250 words; author names and affiliations.
- Required appendix: "Limitations and Dual-Use / Ethical Considerations".
- Optional: public GitHub repo; 3 to 5 minute video demo.
- Suggested structure: Introduction, Related Work, Methodology, Results, Discussion, Limitations and Dual-Use/Ethical Considerations, References.
- AI tools allowed but teams are responsible for content; made-up results or references can disqualify (as relayed by the fetch tool).
- Pre-existing work must be disclosed in README and report. (Relevant: Amphi/Persona predates the sprint.)
- Resubmission with the same title before deadline replaces the old version.
- Deadline: Sunday Nov 15, 2026, 11:59 PM AoE (Mon Nov 16, 11:59 AM UTC). Teams of 1-5; max two projects per person.
- Contact: sprints@apartresearch.com.

## 4. Resources list (Track 3 and sprint-wide), with what each argues

Only items I opened are summarised. "Not opened" means the fetch failed or I did not try.

Track 3 tab:
- Design Sketches: Angels-on-the-Shoulder, https://www.forethought.org/research/design-sketches-angels-on-the-shoulder. Near-term AI could help people decide as they would on reflection by closing gaps in information, situational awareness and access to their own values. Five sketches: aligned recommenders, personalised learning, deep decision briefings, reflection coaching, guardian-angel nudges. The reflection coach uses a private psychological map built over time to separate "what I want" from "what I think I should want". Does not discuss belief consistency.
- Guardian Angels (Gwern), https://gwern.net/guardian-angel. Personalised LLM twins trained on one user's data to emulate their values and judgment, with the user setting goals and making hard calls; ideas include online updating, active learning (asking the user targeted questions), and an append-only log.
- Sycophancy in GPT-4o (OpenAI), https://openai.com/index/sycophancy-in-gpt-4o/. Not opened (HTTP 403).
- Sycophantic AI Decreases Prosocial Intentions (Science 2025), https://www.science.org/doi/10.1126/science.aec8352. Science page returned 403. The arXiv preprint (Cheng et al., https://arxiv.org/abs/2510.01395) was opened: across 11 models, AI affirmed users about 50% more than humans; two preregistered experiments (n=1,604) show sycophancy made people less willing to repair conflicts and more convinced they were right, yet they rated it higher quality and wanted to reuse it. I assume the Science paper is the published version; I did not verify that.
- AI Can Help Humans Find Common Ground (Science 2024), https://www.science.org/doi/10.1126/science.adq2852. Science page returned 403. A search result summary (not the paper) says it is Tessler et al., the "Habermas Machine", an LLM mediator that produced group statements and left UK small groups less divided; commentary criticised it as a consensus optimiser. Summary source: https://comdig.cssociety.org/2024/10/27/ai-can-help-humans-find-common-ground-in-democratic-deliberation/ (listed in search results, not opened).

Sprint-wide and Track 1 items I opened:
- State of the Field: AI for Epistemics and Coordination, https://www.lesswrong.com/posts/uw8RQ8yjKexnhTw6E/state-of-the-field-ai-for-epistemics-and-coordination. Prototypes are easy; adoption in real workflows is the bottleneck. Recommends deployment pilots and decision-quality benchmarks. Names no tool for belief tracking or consistency checking (per the fetch).
- Design Sketches for a More Sensible World, https://www.forethought.org/research/design-sketches-for-a-more-sensible-world. Four clusters (collective epistemics, angels-on-the-shoulder, strategic awareness, coordination tech). No tool that tracks a person's own beliefs over time or flags contradictions; closest is "Reflection scaffolding", a "Socratic coach". Reliability tracking covers sources, not an individual's beliefs. This is the gap Amphi can claim, with the caveat that the check was done by a fetch summariser.
- SycEval, https://arxiv.org/abs/2502.08177. Stanford; about 58% of responses sycophantic across ChatGPT-4o, Claude-Sonnet, Gemini-1.5-Pro on math and medical advice; behaviour highly persistent.
- ELEPHANT, https://arxiv.org/abs/2505.13995. Defines "social sycophancy" (protecting a user's self-image); across 11 models, when given opposing sides of a moral conflict, models affirmed both sides about 48% of the time.
- DarkBench, https://arxiv.org/abs/2503.10728. 660-prompt benchmark of dark patterns in LLMs, sycophancy among six categories.
- Not opened (listed on the page, fetch of the list only): What's Important in AI for Epistemics, AI Impacts on Epistemics, Project Ideas: Epistemics, 80,000 Hours intro, Full Epistemic Stack, Multi-Agent Risks, Collective Epistemics sketches, MASK, Why Language Models Hallucinate, ForecastBench, Petri, Bloom, and all Track 2 and Track 4 items. URLs are on the sprint page.

## 5. Prior work a judge may compare Amphi with

All opened.

Sycophancy and "agreed with both sides":
- Sharma et al., Towards Understanding Sycophancy in Language Models, https://arxiv.org/abs/2310.13548. Five assistants agree with users even when wrong; human preference data partly drives it. Amphi's AI-agreed-with-both-sides flag measures a per-user, in-the-wild consequence of this.
- ELEPHANT (above), https://arxiv.org/abs/2505.13995. Closest eval: 48% both-sides affirmation on constructed moral dilemmas. Difference: Amphi detects it in a person's real chat history, not a benchmark. Must be cited and distinguished.
- SycEval, https://arxiv.org/abs/2502.08177; Cheng et al., https://arxiv.org/abs/2510.01395 (sycophancy raises certainty and lowers repair intent, and users prefer it, which supports the "tools must be wanted" point from the opposite side); DarkBench, https://arxiv.org/abs/2503.10728.

Belief consistency tools:
- BeliefBank (Kassner et al.), https://arxiv.org/abs/2109.14723. Symbolic memory plus MaxSAT keeps an LLM's own answers consistent. It models the model's beliefs; Amphi models the human's.
- Vasileiou et al., How Do People Revise Inconsistent Beliefs?, https://arxiv.org/abs/2506.09977. Three user studies: people prefer explanation-guided, often non-minimal revisions. Supports presenting a conflict with an explanation and separating a change of mind from a live tension.
- Wu et al., How AI Responses Shape User Beliefs, https://arxiv.org/abs/2511.09667. 304-person experiment with "belief switch" and "belief shift" measures; useful measure vocabulary for belief change.

Reflective endorsement and decision-support:
- Angels-on-the-Shoulder and Gwern (section 4) are the conceptual home; Amphi is a concrete reflection-scaffold built from the user's own record.
- Guided Reflection in AI-Assisted Decision-Making (ACM, https://dl.acm.org/doi/10.1145/3772318.3790632) appeared in a search result: reflection prompts reduced AI over-reliance. Page returned 403; claim is from the search snippet only, so verify before citing.

Deliberation tools:
- Habermas Machine (Science 2024, see above); Crux Mapper (sprint example) is the group analogue of Amphi's individual contradiction finder.

I did not find, in the searches run, a published tool that mines a person's own writing and AI chats for contradictions over time and separates change of mind from tension. This is an absence in a few searches and a few fetch summaries, not proof of novelty. Say "we found no" rather than "there is no".

## Unreachable or unverified
- 403: openai.com sycophancy post, both Science DOIs, dl.acm.org guided-reflection paper.
- Template Google Doc not opened.
- Luma talk pages and the Notion/Doc links not opened. The earlier Manifund/Elicit "AI for Epistemics Hackathon" (2025) appeared in search but is a different event and was not opened.
- No message from agent "winners" had arrived when this file was written.

## Addendum: message from researcher A ("winners"), relayed, not independently verified by me
Source of their evidence: paper/research/winners.md (I have not read it; check it before citing anything below).
- Numbers-first abstracts (finding plus hard numbers) are common among winners but not required; correction from A: LidaSim won 1st with an abstract that has no numbers.
- Narrow scope with one claim is praised as "tightly scoped, reproducible".
- Reviewers repeatedly fault: a single LLM judge with no human validation, no significance tests, small n, one seed. Closing these in advance (human raters, CIs, stated n) is the winning move.
- Prototype/product entries get praised for the build and docked for validation (e.g. LidaSim: needs ground truth). For Persona, that means user-endorsed flags and held-out changes of mind, not only a working tool.
- Honest negatives and preregistration are rewarded. Every winning PDF they read has a Limitations/Dual-Use appendix.
- They found no past winner that is an epistemic product with real users, and no "wanted by people" criterion in any sprint page they read; so a user study would be unusual.
