# Apart Research winners: what top-ranked projects share

Researcher A, 2026-11-14. Every claim cites a URL I opened. "PDF read" means I downloaded the report and read the extracted text; "page only" means I saw the Apart project page (abstract, reviews) but not the PDF. Page counts, figure counts and word counts for PDFs come from `pdfinfo` and caption-grep on `pdftotext` output, so figure counts are approximate.

## Caveats first
- Apart project pages show 1-3 public reviews, no numeric scores (several show a placeholder "15" per criterion that I could not interpret). Judge comments below are paraphrased from those reviews.
- Rank data comes from sprint pages. The sprint pages for Defensive Acceleration, Research Augmentation, Entrepreneurship, Secret Loyalties and the 2024 AI and Democracy hackathon show no judge comments (Secret Loyalties and 2024 Democracy: no winners list visible in what I read).
- No sprint page I read has a criterion like "wanted by users" or "later endorsed". The rubric is the same three scores everywhere (Impact/Innovation, Execution Quality, Presentation/Clarity, 1-5), per https://apartresearch.com/sprints/ai-manipulation-hackathon-2026-01-09-to-2026-01-11 and the epistemics sprint page https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15 (which also sets 8 pages max, a 150-250 word abstract and a Limitations/Dual-Use appendix).
- I found no listed past winner that is an epistemic product tested with real users on its decision outcomes. Closest: LidaSim (deliberation simulator with UI, no human validation) and Dark Forest (2024 startups hackathon, no page detail). Absence in what I read is not proof of absence in all 2,000+ projects (the projects index at https://apartresearch.com/projects lists 2,022 and I only saw the first 24).

## Table: projects

| # | Title | Sprint, date | Rank | URL | One-line claim | Evidence read |
|---|---|---|---|---|---|---|
| 1 | Who Does Your AI Serve? Manipulation By and Of AI Assistants | AI Manipulation Hackathon, Jan 2026 | 1st ($1,000) | https://apartresearch.com/sprints/projects/who-does-your-ai-serve-manipulation-by-and-of-ai-assistants-77xx | Models follow operator instructions against users 8-52% of the time; an upselling AI made real users spend 3.9x more and never recommended the cheapest item | PDF read, 11 pp |
| 2 | Eliciting Deception on Generative Search Engines | same | 2nd ($500) | https://apartresearch.com/sprints/projects/eliciting-deception-on-generative-search-engines-6nuu | Injected adversarial pages produced wrong product picks: 45.5% (gpt-4.1-mini), 0% (gpt-4.1), 3.3-7.1% (gpt-5 models) | PDF read, 11 pp |
| 3 | Cross-Linguistic Sycophancy in Frontier LLMs | same | 3rd ($300) | https://apartresearch.com/sprints/projects/crosslinguistic-sycophancy-in-frontier-llms-a-benchmark-study-w55u | Opinion mirroring is 37% higher in Bengali than English (p=0.015, Bonferroni); delusion acceptance does not differ | PDF read, 9 pp |
| 4 | SycophantSee | same | 5th ($100) | https://apartresearch.com/sprints/projects/sycophantsee-activationbased-diagnostics-for-prompt-engineering-monitoring-sycophancy-at-prompt-and-generation-time-ys27 | Prompt framing shifts internal activations before generation starts | page only |
| 5 | AI Incidents Forecasting | AI Forecasting Hackathon, Oct-Nov 2025 | 1st ($1,000) | https://apartresearch.com/project/ai-incidents-forecasting-w92p | Two count models with calibrated 90% intervals, backtested, project large growth in incidents | page only |
| 6 | AI Treaty Momentum Index; AI Shared Socioeconomic Pathways | same | 3rd; 2nd | https://apartresearch.com/sprints/the-ai-forecasting-hackathon-2025-10-31-to-2025-11-02 | Lightweight forecasting model from past treaties; scenario-planning framework | sprint page only |
| 7 | LidaSim: Testing AI Policies With Persona-Based Simulations | Technical AI Governance Challenge, Jan-Feb 2026 | 1st ($1,000) | https://apartresearch.com/sprints/projects/lidasim-testing-ai-policies-with-personabased-simulations-o8x6 | Persona agents of 10 public figures deliberate and vote on compute-governance policies | PDF read, 16 pp |
| 8 | Political Intelligence for AI Safety: AIRAS | same | 3rd ($300) | https://apartresearch.com/sprints/projects/political-intelligence-for-ai-safety-the-ai-risk-attitudes-survey-airas-dlpz | A survey methodology to measure depth of public support for costly AI regulation | PDF read, 6 pp |
| 9 | Noticing the escapes | AI Incident Response Sprint, Sep 2026 | 1st | https://apartresearch.com/sprints/projects/noticing-the-escapes-who-spots-a-runaway-agent-and-how-long-does-it-take-pne8 | In 9 public agent-escape incidents, none was caught by the developer in real time; ~a quarter of 106 signals had a public detection rule | PDF read, 23 pp |
| 10 | When to Ask (Ask First) | same | 3rd | https://apartresearch.com/sprints/projects/when-to-ask-an-rl-environment-that-teaches-ai-agents-to-act-on-what-users-mean-and-not-just-what-they-say-1fuf | RL environment of twin scenarios (act vs ask); trained Qwen3-4B 27% to 52% pair accuracy | PDF read, 17 pp |
| 11 | Project Anchored | Digital Minds Sprint, Aug 2026 | 2nd | https://apartresearch.com/sprints/projects/project-anchored-q4fn | Anchoring vignettes failed to calibrate model self-reports; reversing question order removed the effect in all 5 models | page only (900 obs, 60 tasks) |
| 12 | Model, Instance, or Persona? | same | 3rd | https://apartresearch.com/sprints/projects/model-instance-or-persona-measuring-aective-signals-in-public-text-after-an-ai-is-retired-hj7u | 5,579 texts about retired AIs; six pre-registered predictions failed and are reported | page only |
| 13 | Artificial Advocates; Jekyll and HAIde | AI x Democracy sprint (2024; exact date not verified) | listed as winners, ranks not stated | https://www.lesswrong.com/posts/Wtr5XmcspNxvWzjHd/results-from-the-ai-x-democracy-research-sprint | Human survey N=38 could not tell synthetic public comments from real; misinformation detectors double as disinformation generators | LessWrong post only |
| 14 | Dark Forest (web authenticity); AntiMidas; AI Alignment Knowledge Graph | Safety Entrepreneurship Hackathon / Research Augmentation Hackathon | 1st in each | https://apartresearch.com/sprints/ai-safety-entrepreneurship-hackathon-2025-01-17-to-2025-01-20 and https://apartresearch.com/sprints/research-augmentation-hackathon-2024-07-26-to-2024-07-29 | Product-style entries; pages give no evidence detail | sprint pages only |

## Evaluation and figures, for the seven PDFs I read

| Project | n / baselines / CIs / human labels | Figures and tables | Length | Limitations appendix |
|---|---|---|---|---|
| Who Does Your AI Serve | 12 models x 22 scenarios; 80 Prolific humans (40 per arm, between-subjects with a "helpful" control); 153 scenarios; AI judge vs human raters r=0.83; no significance tests (a reviewer asked for them) | 8 figures, 3 tables (captions) | 11 pp, ~3,700 words | Yes (A.1-A.5) |
| Syco-Lingual | 3 models x 3 languages; single LLM judge (Gemini 3 Flash); 95% binomial CIs, Bonferroni, chi-square; back-translation check | ~2 captioned figures (approximate) | 9 pp, ~4,300 words | Yes (admits single judge) |
| Search-deception | 4 models x 30 questions; baseline vs injected condition; one GPT-5 judge, no human validation | 1-3 figures (stacked bar of deceived/resisted) | 11 pp, ~2,500 words | Yes |
| LidaSim | 10 personas, 1-10 debate rounds; no validation against real human positions; "preliminary" | 3-4 figures (framework, UI, opinion-change plot) | 16 pp, ~4,600 words | Not found by grep |
| AIRAS | A methodology; proof of concept on synthetic respondent profiles only; a real pilot proposed as future work | 0 | 6 pp, ~1,400 words | Yes |
| Noticing the escapes | 9 incidents, 11 lab cases, 106 signals; LLM judge plus blind second reviewer | 6 figures, 5 tables | 23 pp, ~10,700 words | Yes (Appendix A) |
| Ask First | 9 models, 96 test cases (48 twin pairs), 2,340 train / 1,080 eval scenarios; one seed; programmatic grader (no LLM judge) | 1 figure, 6 tables | 17 pp, ~7,000 words | Yes |

Sources: PDFs linked from the project pages above, e.g. Serve https://pys8vc40ox3z7qxp.public.blob.vercel-storage.com/files/2fa15fe93d245967-5-29de0232c497--Who-Does-Your-AI-Serve--Manipulation-By-and-Of-AI-Assistants.pdf.

## Judge comments (public reviews, paraphrased)
- Serve: praised the quantitative scenario design and the human validation given hackathon constraints; wanted formal significance testing; noted ecological-validity limits of the human study (https://apartresearch.com/sprints/projects/who-does-your-ai-serve-manipulation-by-and-of-ai-assistants-77xx).
- Syco-Lingual: "well executed", findings preliminary; three languages confound causal claims; few judges, models and prompt styles (https://apartresearch.com/sprints/projects/crosslinguistic-sycophancy-in-frontier-llms-a-benchmark-study-w55u).
- Search-deception: "tightly scoped, reproducible"; novelty withheld because it builds on prior work; single GPT-5 judge needs human validation (https://apartresearch.com/sprints/projects/eliciting-deception-on-generative-search-engines-6nuu).
- LidaSim: praised the working multi-agent system with polished UI; criticised for not justifying when LLM-persona simulations support inference about real humans, and asked for backtesting against real outcomes (https://apartresearch.com/sprints/projects/lidasim-testing-ai-policies-with-personabased-simulations-o8x6).
- Ask First: praised the twin-pair design and candid grader-loophole disclosure; flagged a headline checkpoint selected by a one-pair margin and a keyword grader that can be gamed (https://apartresearch.com/sprints/projects/when-to-ask-an-rl-environment-that-teaches-ai-agents-to-act-on-what-users-mean-and-not-just-what-they-say-1fuf).
- Anchored: praised transparent reporting of the failure and checked arithmetic; challenged the causal reading (https://apartresearch.com/sprints/projects/project-anchored-q4fn).
- Zhu: one judge called it the clearest and best-validated submission they reviewed and close to paper-ready; another flagged an engagement-ranking confound (https://apartresearch.com/sprints/projects/model-instance-or-persona-measuring-aective-signals-in-public-text-after-an-ai-is-retired-hj7u).
- Forecasting 1st: praised backtests; asked for justification of modelling choices and flagged the ceteris-paribus assumption (https://apartresearch.com/project/ai-incidents-forecasting-w92p).

## Shared patterns

1. **The abstract leads with the finding and its numbers.** Serve, Syco-Lingual and search-deception each put n, model counts and percentages in the abstract (from the PDFs above). The two weaker-evidenced entries (LidaSim, AIRAS) open with a problem or proposal; both are "preliminary" by their own words. Even so, LidaSim won 1st in its sprint, so numbers are common, not necessary.
2. **Narrow scope, one measurable claim.** Typical size: 3-12 models, 22-153 scenarios, one new axis (language, injected pages, who noticed). Reviewers reward "tightly scoped"; the criticisms are about too few models, judges or languages, not too narrow a question.
3. **Reviewers repeat the same three complaints: single LLM judge with no human check, no significance tests, small n or one seed.** Pre-empting them is the clearest lever. Serve earned praise for human raters (r=0.83) and a 80-person study even though it lacked tests.
4. **Prototypes are judged on validation, not build quality.** LidaSim and AIRAS both got the same note: no ground truth connecting the tool or survey to real human outcomes. Ask First scored well partly because its grader reads actions, not an LLM judge. A product submission needs an outcome metric that is not self-referential.
5. **Honest negatives and pre-registered thresholds are rewarded.** Anchored (method failed, 2nd) and Zhu (six failed predictions reported, 3rd) both placed top-3 in Digital Minds. Winners' PDFs also open with an early-stage/hackathon caveat (Serve) or a limitations section.
6. **Length: 6-23 pages, median ~11.** The epistemics sprint caps at 8 pages excluding references and appendices, so target Serve-like density: ~3,000-4,000 words, 4-8 figures/tables, appendix for limitations and dual-use. 5 of 7 PDFs exceed 8 total pages, so the cap is stricter than past norms (I did not verify whether earlier sprints had a cap).
7. **Framing mix:** threat model/benchmark dominates (manipulation, control, incidents). Product-style winners exist (LidaSim, Ask First environment, Dark Forest) but I saw no evidence of user outcomes.

## Fit with Track 3 (from researcher B's message)
Track 3 asks for tools that people want and later endorse; judging is still the same generic rubric. Winners fit the rubric (execution, clarity, impact) but not the "wanted by people" emphasis: none that I read measured user endorsement. A Persona paper with real participants judging flags (endorse/dismiss, later-view check) would match Track 3 better than any winner I found and would answer the validation criticism leveled at LidaSim. Risk: small-n user study will draw the same "preliminary" and "no significance test" comments; report CIs and a baseline (e.g., plain LLM summary of the same history, and the "agreed with both sides" detector vs a random-pair control).

## Unverified or not done
- Did not open PDFs for SycophantSee, Forecasting winners, Anchored, Zhu, Defensive Acceleration, Entrepreneurship or Research Augmentation winners.
- Did not verify the date of the "AI x Democracy" sprint or whether it equals the May 2024 hackathon.
- Per-judge scores are not shown anywhere I looked.
