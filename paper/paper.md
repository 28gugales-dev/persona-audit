---
title: "A belief-mapping tool misses the changes of mind people announce: an audit on planted items and philosophers' own writing"
author: "Soham Gugale (Amphi)"
note: "Research conducted at the AI x Epistemics Research Sprint (Apart Research), November 2026"
---


# Abstract
Persona, our shipped tool, shows people where their own views conflict or have changed. We audited it on answer keys it cannot grade itself on, chiefly the public-domain writing of ten authors with 13 documented changes of mind (19 early-to-later passage pairs), split into development and later-sourced held-out sets.

The shipped tool surfaced none of the 19 pairs, for two separate reasons. Its word-overlap theme sort never put the two ends together: by word overlap, a passage's true later partner ranked a median 59% of the way down its history, and 8 of 19 shared no content word with it. And its prompt suppresses the pair even when both ends are present: given the whole history in one call, it still found none, while a naive prompt found 6 and our real-prose variant (realX) 8 (majority of three runs; 5-10 per run). On planted items the same prompt flagged no look-alikes, but one "I've changed my mind" cut detection from 36/36 to 9-17/36 (Claude Haiku 5.5); ablations trace this to its definition (two views the person "asserts") and a default that most themes have none.

Without the text, Haiku recalled only 7 of the 13 changes, and half the pairs realX found were among the other six. Changes the author never announced stayed hard (2 of 7). Ten of 18 real-text predictions failed. We did not measure what users want.

# 1. Introduction

Track 3 asks whether AI tools lead people to decisions they later endorse. One candidate reads what a person has written over the years, finds where their views conflict or have changed, and asks where they stand now: the "reflection scaffolding" of Forethought's angels-on-the-shoulder sketches [1]. Done well, it surfaces drift people miss, including views picked up from an assistant that agreed with them [2, 3, 4]. Done badly, it nags about refinements, or drops the changes people would most want on record.

We audit one such tool that is already shipped. **Persona**, part of Amphi (amphi-forum.org), imports a person's posts, notes and AI-chat exports, sorts them into themes, and sends up to 20 excerpts per theme to Claude Haiku 5.5 with a fixed prompt. Each pair it returns becomes a card with one neutral question, labelled "change of mind" or "live conflict", which the person settles. The product predates this sprint (Table 1); the sprint's work is the evaluation and the repairs. Contributions:

1. **On real writing, the shipped tool finds none of the documented changes of mind.** On 12 histories built from 13 documented reversals by ten authors, its theme sort never put the two ends of any of 19 pairs in one theme, and its prompt found none of them even when given each whole history. Shown each pair alone, it found 6 of 39 tries.
2. **The cause in the prompt, isolated on planted items.** One "I've changed my mind" cut detection from 36/36 to 9-17/36 on Haiku and to 14/36 on Sonnet; a neutral sentence left it at 36/36. Crossed ablations with a placebo trace the loss to the definition "asserts both as their own view" and the empty-list default; three strict prompts GPT wrote from the same brief did not share it.
3. **Repairs, each checked on items it was not chosen on.** Prompts: on 40 later-written items (18-20/20 vs 8-14) and held-out real pairs (realX 14/18 vs 3/18 over three runs). Pipeline: for histories that fit in one call, sending the whole history surfaced 8 of 19 pairs with realX and 6 with a naive prompt (majority of three runs), and 0 with the shipped prompt; beyond one call, a cheap model pass grouping posts by question (held-out planted 18/20 vs 9/20 end to end; held-out real 3 of 9 vs 0).
4. **A record of every arm and prediction**, committed before its outputs existed. Of 35 numeric predictions (one per row of Appendix F), 14 failed and are kept: 4 of 17 on planted items and 10 of 18 on real text, one because a baseline did better than we predicted (Appendix F).

**Table 1. Built before the sprint vs during it (Nov 13-15, 2026).**

| Before the sprint (shipped Nov 1) | During the sprint |
|---|---|
| Import of posts and AI chats; word-overlap theme sort; on-device detector; opt-in model step and its prompt (Haiku 5.5); conflict cards with verdicts | "Change of mind" vs live label; this whole evaluation (test sets, real-text sets, harness, runs, prompt variants, model grouping: `evals/conflicts`, `paper/`). On Nov 14 we deployed one repair: whole history in one call when it fits (up to 120 excerpts, 50,000 characters), with realX. |

# 2. Related work

**Sycophancy and belief drift.** Assistants agree with users' stated views [2], affirm both sides of a moral conflict about 48% of the time [3], and leave people surer they are right while being preferred [4]. 

**Contradiction and belief change.** Unlike these benchmarks, we test a shipped tool end to end on real authors' documented reversals, and separate the grouping step from the judgment step. ContraDoc studies self-contradiction inside long documents [5]; BeliefShift benchmarks how assistants track a user's changing beliefs, separating contradiction detection from revision [6]; FactTrack gives facts validity intervals so change over time is not mistaken for error [7]; BeliefBank keeps a model's own beliefs consistent [8]; people prefer explanation-guided revision [9]; stance datasets follow opinion shifts on social media [15]. These treat revision as something to model. We show that a deployed prompt's wording, and a deployed grouping step, can put revision out of reach, and measure it on real authors' own writing.

**Prompt and cue sensitivity.** Outputs shift with meaning-preserving formatting [12]; models often fall back on internal knowledge rather than supplied label definitions [13]; they mishandle negation [14]. Here the model followed its definition; the definition was the problem.

**Epistemic products.** Track 3's examples include a Crux Mapper for inconsistencies in group beliefs; Persona is the individual, longitudinal analogue. Reviewers of a winning Apart entry (LidaSim) asked for validation against real outcomes [11]. Our nearest substitute is writing by real people whose changes of mind are documented in their own words.

# 3. Methods

## 3.1 System under test

1. **Theme sort** (on device). TF-IDF terms per entry, grouped into themes by shared words.
2. **Model step** (opt-in). Per theme, up to 20 excerpts spread over time, each 60-400 characters, go to Haiku with the production prompt (Appendix B). It has a **definition** ("Count a pair only when the person asserts both as their own view, on the same point, and they clash"), an **exclusion list** ("Do not count: ... questions, doubt ...; describing, quoting or answering someone else's view; ..."), an **empty-list default** ("Most themes have none, and an empty list is the right answer then") and output rules.
3. **Card**, labelled (from Nov 13, during the sprint) "change of mind" if the posts are a year apart or the newer one uses revision words, else "live". An on-device lexical detector also exists; it found none of the planted conflicts (Appendix D).

## 3.2 Answer keys

**Planted items (Table 2).** 24 synthetic histories of 26 posts, one per topic on five of the 35 PhilPapers 2020 questions with no majority answer [10]; GPT (via Codex) wrote every post from label definitions only, never seeing the prompt. Plus 50 hand-written items, 10 philosophers' reversals paraphrased in the first person, and 40 items GPT wrote after the prompt repairs were chosen ("fresh"). Blind Sonnet labellers agreed with the intended labels on 149/150 and 40/40 items.

**Real writing.** Two sets of documented changes of mind in public-domain English texts (Gutenberg, Wikisource, archive.org), each with a secondary source, every passage checked by script to appear verbatim:
- *Development* (7 cases, sourced first): Hume (personal identity), Peirce (the untested diamond), Nietzsche (metaphysical comfort; Wagner), Kant (1770 vs 1783), Mill (the wages fund), Russell (consciousness).
- *Held-out* (6 cases, sourced by a separate agent after the development runs, none of its passages read when the held-out predictions were committed): Darwin (useless structures), Newman (Rome), Mill (socialism), Spencer (the divine basis of rights), Huxley (progressive development), Nietzsche (the saint and pity).

Each case has an **early** passage stating the earlier view, a later **announced** passage saying the author changed his mind, a later **unannounced** passage where one exists, and a same-era **control** that conflicts with neither. Before any run we coded whether each announced passage states the new view itself (7 of 13) or only retracts ("I neither know how to correct my former opinions"). For end to end, each case becomes a history: up to 60 paragraphs sampled from the early work and 60 from the later one (the author's own text only), dated by year of writing, plus the passages. The development Mill case has no history (its edition mixes the editor's text with Mill's), so the 12 histories hold 19 early-to-later pairs (6 + 4 development, 6 + 3 held-out).

**Table 2. What counts.** Positives should be flagged; decoys and controls should not.

| Set | Positives | Decoys / controls |
|---|---|---|
| Planted, GPT-written (120) | plain (12), reworded (14), narrated change (10), buried (10) | someone else's view, doubt, question, refinement, shared word, hypothetical, restatement (74) |
| Hand-written (50) | reported view later adopted, hedged reversal, double negation (28) | sarcasm, negated refinement, concession, reaffirmation with change words (22) |
| Fresh, GPT-written (40) | narrated reversals in varied wording (20) | narrated refinements, reaffirmations, doubts (20) |
| Real writing (13 cases) | early + announced (13), early + unannounced (7) | early + same-era control (13) |

## 3.3 Runs and measures

**Settings.** *Oracle*: a pair or an item's posts sent as one theme, isolating the model. *End to end*: the shipped theme sort and request builder, unmodified, then the model. *Marker*: "I used to see this differently, but I've changed my mind." placed before post B; *neutral sentence*: "I was reading about this again today." in the same place.

**Model and harness.** Haiku 5.5 through Claude Code subagents, one fresh agent per request (about 4,900 saved replies, all Haiku except about 230 Sonnet). The production prompt is passed verbatim and replies parsed by the production parser. There was no API key, so this is "Haiku in an agent harness"; temperature cannot be set, so key arms were run two or three times.

**Prompts compared.** *Production*: the shipped prompt. *Rewrite*: production with a time-anchored definition and no empty-list default. *genX*: a generic "find contradictions" prompt plus production's exclusion list. *realX*: genX plus one paragraph saying a view the writer formerly held counts. *Naive*: "Where does this person contradict themselves?", no exclusions. Full texts in Appendices B and E.

**Model grouping** (built in the sprint). Pass 1: for each excerpt, Haiku names the one question it takes a position on, 30 excerpts per call. Pass 2, only when a history needs more than one call: one call merges same-issue questions into groups. Groups replace the word themes; the request builder and model step are unchanged. Version 1 was tuned on planted development histories; version 2 changed only the merge prompt, tuned on the real development set.

**Process.** Each design was committed before its outputs existed, with a numeric prediction for all but two arms (Appendices C, F). The real-prose prompt variant was frozen after one development run and checked on 82 unseen look-alikes and 20 unseen reversals before any held-out run. Subagents had file tools; across the runs they averaged 2.0 tool calls each (one Read, one Write), so they did not browse other requests or keys. Commit order shows ordering, not independence. In the whole-history calls, 59 of 70 replies that cited any excerpt cited one in the last third of the request, so the harness read deep into these requests, though this does not prove every excerpt was read.

**Statistics.** Wilson intervals, exact McNemar tests for paired contrasts, percentile bootstraps over histories or items (Holm-adjusted ablations, Appendix D). Real-text cards were labelled for "a real change or tension in the author's own views" by Haiku and Sonnet blind (one call each, same prompt) and by the author's model (Claude Opus), not blind to the run.

# 4. Results

## 4.1 On real writing, the shipped tool surfaces none of the reversals

![**Figure 1.** Real early-to-later pairs surfaced end to end (Haiku; majority of 3 runs, Wilson 95% intervals). Word-overlap themes score 0 by construction: no pair shares a theme.](figures/fig0_real.svg)

**Grouping.** The word-overlap theme sort put the early and later passage in one theme for 0 of 10 development pairs and 0 of 9 held-out pairs. Only 32-77% of real paragraphs landed in any theme. Authors do not reuse their words across decades ("acquainted" in Russell's 1912 view, "widely held" in his 1921 retraction): ranked by TF-IDF similarity to the early passage, the true later partner came a median 59% of the way down its history's list, in the top 5 for only 2 of 19, and shared no content word with the early passage for 8.

**The prompt, even with both ends present** (Figure 1, Table 3). Given each whole history in one call, the production prompt surfaced 0 of 19 pairs in each of three runs; it returned 10 pairs in all over 36 history-runs, keeping to its default that most themes have none. Shown each pair alone, it found 3 of 21 development tries (Mill's "the doctrine hitherto taught by all or most economists (including myself) ... must be thrown aside" in 2 of 3) and 3 of 18 held-out tries, all on Darwin's "one of the greatest oversights as yet detected in my work". No control was flagged in 39 tries.

**Memory does not explain what is found.** Haiku named the author of 26 of 27 passages, but asked from memory alone (author, years and question, no text), it stated the documented change for only 7 of the 13 cases. Of the 8 pairs realX surfaces, 4 are in cases it could not recall (Darwin, Huxley, Peirce, Spencer), and it missed two it could (Nietzsche on Wagner and on pity).

## 4.2 The cause, isolated on planted items

![**Figure 2.** Reversals found by the production prompt on planted items (oracle, Wilson 95% intervals; philosophers' paraphrases pool four phrasings). Grey: plain; light grey: neutral sentence; orange: change-of-mind sentence; blue: with the one-line fix.](figures/fig1_marker.svg)

With the production prompt Haiku found every unsignalled planted reversal (36/36). The marker cut this to 11/36 (25 lost, 0 gained, exact McNemar p = 6×10⁻⁸; history-cluster bootstrap of the drop 0.69 [0.55, 0.84]); three runs gave 11, 9 and 17. The neutral sentence left it at 36/36, so the cue causes the drop, not the edit. Sonnet 5.5: 36/36 unmarked, 14/36 marked (p = 5×10⁻⁷). On the ten paraphrased philosophers' reversals: 9/10 plain, 8/10 neutral, 2/10 marked (p = 0.016).

**What each clause does.** Removing the exclusion list did not restore recall (15/36; Holm p = 0.48), and adding it to a generic prompt took that prompt's false flags from 9/40 to 0/40 with every reversal kept: the list buys precision. Crossing the definition with the empty-list default (three runs per cell, items of 36): a time-anchored definition ("each excerpt, at the time it was written, stated the person's own view") adds 16.7 [11.6, 21.9] with the default and 7.7 [5.2, 10.6] without; dropping the default adds 14.0 [10.5, 17.7] and 5.0 [1.9, 8.4]; a placebo rewording of the same length and meaning adds −2.3 [−5.8, 1.3]. Three strict prompts that GPT wrote from a brief asking for few false alarms went 36→32, 30→35 and 31→31 when marked, with no decoy flags: strictness alone does not cause the loss.

**Table 3. Prompts, shown items directly** (Haiku; ranges over runs). *Marked*: 36 planted reversals with the marker. *Decoys*: 40 held-out planted decoys. *Fresh*: 40 items written after the repairs were chosen. *Real*: early + announced pairs, development (7 cases × 3 runs) and held-out (6 × 3); controls were never flagged (production and genX 0 of 39 tries, rewrite 0 of 21, realX 0 of 25). – = not run. Placebo (7-15 marked), GPT's strict prompts, ablations and Sonnet in Section 4.2 and Appendices D-F.

| Prompt | Marked /36 | Decoys /40 | Fresh narrated /20 | Fresh look-alikes /20 | Real dev /21 | Real held-out /18 |
|---|---|---|---|---|---|---|
| **Production** (shipped) | 9-17 | 0 | 8-14 | 0 | 3 | 3 |
| **Rewrite**: time-anchored definition, no default | 32-35 | 0 | 18-19 | 0 | 4 | – |
| Generic A: "find contradictions" | 36 | 9 | 20 | 6 | – | – |
| **genX**: generic A + production exclusion list | 36 | 0 | 19-20 | 0 | 5 | 10 |
| **realX**: genX + "a view the writer formerly held counts" | – | 0 | 20 | 0 | 4 of 7 (tuning) | 14 |

## 4.3 Repairs, on items they were not chosen on

**The prompt.** On the 40 fresh items, over three runs, the rewrite and genX found 8.0 [4.7, 11.3] and 9.0 [6.0, 12.0] more of the 20 narrated reversals than production and flagged no narrated look-alike. On real development pairs, though, every prompt stayed low (genX 5/21): real authors describe their old view abstractly ("a theory which I formerly held myself"), and genX's own exclusion of "describing someone else's view" catches it. realX adds one paragraph saying a view the writer formerly held counts. Frozen after one development run, it flagged 1 of 82 unseen look-alikes and found 20/20 fresh reversals. On the held-out real set, over three runs, realX found 14/18 and genX 10/18, against production's 3/18; counted by case (found on a majority of runs), 5, 4 and 1 of 6. Unannounced real reversals stayed hard for every prompt (held-out 1-3 of 9).

**The grouping** (Table 6, Appendix D). Model grouping kept 18 of 20 held-out planted conflicts in one group (word sort 11) and, end to end, raised recall from 9/20 to 16/20 with the production prompt (8 gained, 1 lost, p = 0.039) and 18/20 with genX (10-1, p = 0.012), flagging no decoy; every card sat on a planted reversal (53 cards for 18 reversals with genX, because a reversal also pairs with the posts restating its earlier view). On real text the first version failed (1 of 10 development pairs together): it left 46-92 groups per history, mostly of one to three posts. Version 2 groups by the issue a writer could change their mind on; tuned on the development set (4/10), it put 4 of 9 held-out pairs together and, with realX, surfaced 3 of 9 held-out reversals end to end (Darwin, Spencer, Nietzsche on pity), where word grouping surfaces none. It costs about one Haiku call per 30 posts.

**Table 4. Each announced reversal** (runs that surfaced the early + announced pair; the shipped pipeline surfaced none). *New view*: the announced passage states the new view. Development realX: its one tuning run.

| Case (* held-out) | New view | Alone: prod. | Alone: realX | Whole: naive | Whole: realX | Group v2 + realX |
|---|---|---|---|---|---|---|
| Hume | no | 0/3 | 0/1 | 0/3 | 0/3 | – |
| Peirce | yes | 1/3 | 1/1 | 3/3 | 3/3 | – |
| Nietzsche (comfort) | no | 0/3 | 0/1 | 0/3 | 0/3 | – |
| Nietzsche (Wagner) | yes | 0/3 | 1/1 | 0/3 | 0/3 | – |
| Kant | no | 0/3 | 0/1 | 0/3 | 0/3 | – |
| Mill (wages) | yes | 2/3 | 1/1 | – | – | – |
| Russell | yes | 0/3 | 1/1 | 2/3 | 2/3 | – |
| Darwin* | yes | 3/3 | 3/3 | 3/3 | 3/3 | 1/1 |
| Newman* | no | 0/3 | 2/3 | 0/3 | 1/3 | 0/1 |
| Mill (socialism)* | no | 0/3 | 3/3 | 2/3 | 3/3 | 0/1 |
| Spencer* | yes | 0/3 | 3/3 | 2/3 | 2/3 | 1/1 |
| Huxley* | yes | 0/3 | 3/3 | 0/3 | 2/3 | 0/1 |
| Nietzsche (pity)* | no | 0/3 | 0/3 | 0/3 | 0/3 | 0/1 |

**Both fixes are needed.** Our real histories fit in one call (72-124 excerpts, under 56,000 characters), so we sent each whole, three runs per prompt. Production surfaced 0 of 19, naive 7, 4 and 4, and realX 10, 7 and 5; naive flagged a control in 2 of 36 history-runs, realX in none. On a majority of runs, naive found 6/19 [0.15, 0.54] and realX 8/19 [0.23, 0.64] (held-out 3/9 and 4/9). Resampling histories, realX found 7.3 pairs per run [5.0, 9.7] and naive 5.0 [2.3, 7.7]; realX minus naive 2.3 [0.3, 4.7], although at the pair level realX gained 2 and lost 0 (exact p = 0.5). Gains were mostly on announced changes (realX 6/12 announced, 2/7 unannounced; naive 5, 1). So the split hides the pair, and the shipped prompt suppresses it even when visible; neither fix alone found anything in our runs. Grouping is for histories too long for one call: on planted data the naive single call fell from 25/26 on 26-post histories to 16/26, with 213 pairs returned, on one 312-post history (Appendix D).

**Cards on real text.** Grouping v2 with realX returned 25 cards over the six held-out histories, about four per history. Raters judged 15-18 of them a real change or tension in the author's own views (blind Sonnet 16, Haiku 18; Opus, not blind, 16), so 7-10 were not; some genuine ones lie outside our key. Agreement was modest (κ 0.34-0.74, over these and 9 earlier cards). The single calls' first-run cards were labelled by the same blind prompt: naive, Haiku 23 and Sonnet 24 of 34 cards genuine (held-out 13 and 12 of 17); realX, 23 and 25 of 27 (held-out 11 and 13 of 14). All labels are from Claude models, not people.

## 4.4 What the model step gets right

Shown items directly, the production prompt flagged 0 of 96 synthetic decoys (74 GPT-written, 22 hand-written; 95% upper bound 3.8%) and no real-text control, and a GPT judge validated on hand labels (κ = 0.94) found 116 of 120 of its questions neutral. The failures are misses, not false alarms, which is why they stayed invisible.

# 5. Discussion and limitations

**What this means for epistemic products.** A tool meant to support decisions people later endorse failed in the cases closest to endorsement: changes of mind the person announced, and, on real writing, changes of mind at all. Both were silent: flags on synthetic look-alikes and real controls were zero throughout (though 7-10 of 25 real-text cards from the repaired pipeline were judged not genuine), and the product's own "change of mind" label is set by revision words or elapsed time, the first being the very cue that made its prompt drop the pair.

**What generalises.** Not the specific clause: genX and GPT's strict prompts have different blind spots. Two things do. First, a pipeline that groups by shared words will rarely put a person's earlier and later views together, because people describe a view differently once they have left it. Splitting a record that fits in one context window throws away the comparison the tool exists to make; past that size, grouping must be by meaning. And a prompt tuned for few false alarms can return nothing even when the pair is in view, so recall should be measured end to end, on real records. Second, the audit method: an answer key the tool cannot grade itself on, one-cue edits with a neutral control, clause ablations, simple baselines, and real writing with documented reversals, held out.

**Design.** Use realX, not the shipped definition; send the whole history in one call while it fits, and group by question with a model only beyond that. We deployed the first two in Persona on Nov 14 (realX plus the shipped output rules, at most 8 pairs per call); its effect on real users is not measured. For announced changes, a card that confirms ("You moved from X to Y; is that still where you stand?") may fit better than one that asks.

**Not shown:** that people want these cards, or that seeing them improves their decisions. End to end on real text, even the best arm found under half the pairs.

**Limitations** (full list in Appendix A). No users. Thirteen real cases, famous authors the model knows (26 of 27 passages attributed), English, and 19th-century prose; grouping's end-to-end real runs were single runs, whole-history calls varied from 5 to 10 of 19 across runs, both held-out grouping predictions narrowly failed, and the whole-history call was not tested with realX on records too long for one call. One model family, in an agent harness, run by the product's author; card labels from three raters with modest agreement.

**Future work.** A consented study in which people import their own history, list the changes of mind they know they made, rate each card, and revisit verdicts a month later; measuring the deployed whole-history path on users' records, adding model grouping beyond one call, and testing that switch on long real records; a cross-family replication.

# 6. Conclusion

On philosophers' own writing, Persona's shipped pipeline surfaced none of the 19 early-to-later pairs from 13 documented changes of mind: its word grouping never put the two views together, and its prompt, which defines a conflict as two views the person asserts at once, missed most announced reversals even when shown the pair. On planted items one "I've changed my mind" cut detection from 36/36 to 9-17/36. A generic contradiction prompt plus the product's exclusion list and a variant for real prose recover much of this on held-out items, without false alarms on look-alikes; sending a history that fits in one call whole surfaced 6-8 of the 19 real pairs on a majority of runs with those prompts, but none with the shipped one, and grouping by question helps beyond that size. Such blind spots hide behind zero false alarms; real records with known reversals find them.

# Code and data

Everything is at https://github.com/28gugales-dev/persona-audit: the evaluation code (`evals/conflicts/`); the data, raw model replies, the real-text cases and a ledger tying every number to its file are in `paper/`. Source texts are public domain; each case lists its URLs, line spans and secondary source (`paper/data/realtext_cases*.json`, `reversals_sources.md`). The audited product files, as shipped on Nov 1 and as deployed on Nov 14, are under `product/`.

# References

1. Cotton-Barratt, O., Vaintrob, L., Sourbut, O., Hadshar, R. (2026). Design Sketches: Angels-on-the-Shoulder. Forethought. https://www.forethought.org/research/design-sketches-angels-on-the-shoulder
2. Sharma, M. et al. (2023). Towards Understanding Sycophancy in Language Models. arXiv:2310.13548.
3. Cheng, M. et al. (2025). ELEPHANT: Measuring and understanding social sycophancy in LLMs. arXiv:2505.13995.
4. Cheng, M. et al. (2025). Sycophantic AI Decreases Prosocial Intentions and Promotes Dependence. arXiv:2510.01395.
5. Li, J., Raheja, V., Kumar, D. (2024). ContraDoc: Understanding Self-Contradictions in Documents with Large Language Models. NAACL 2024. arXiv:2311.09182.
6. Myakala, P. K., Agrawal, M., Manche, R. (2026). BeliefShift: Benchmarking Temporal Belief Consistency and Opinion Drift in LLM Agents. arXiv:2603.23848.
7. Lyu, Z., Yang, K., Kong, L., Klein, D. (2024). FactTrack: Time-Aware World State Tracking in Story Outlines. arXiv:2407.16347.
8. Kassner, N. et al. (2021). BeliefBank. EMNLP 2021. arXiv:2109.14723.
9. Vasileiou, S. L., Rago, A., Martinez, M. V., Yeoh, W. (2025). How Do People Revise Inconsistent Beliefs? Examining Belief Revision in Humans with User Studies. arXiv:2506.09977.
10. Bourget, D., Chalmers, D. (2023). Philosophers on Philosophy: The 2020 PhilPapers Survey. Philosophers' Imprint 23(11). https://survey2020.philpeople.org (CC BY-NC).
11. Apart Research. LidaSim: Testing AI Policies With Persona-Based Simulations (project page and reviews). https://apartresearch.com/sprints/projects/lidasim-testing-ai-policies-with-personabased-simulations-o8x6
12. Sclar, M. et al. (2024). Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design or: How I learned to start worrying about prompt formatting. ICLR 2024. arXiv:2310.11324.
13. Mohammadi, S. et al. (2025). Do LLMs Adhere to Label Definitions? Examining Their Receptivity to External Label Definitions. EMNLP 2025. arXiv:2509.02452.
14. García-Ferrero, I. et al. (2023). This is not a Dataset: A Large Negation Benchmark to Challenge Large Language Models. EMNLP 2023. arXiv:2310.15941.
15. Sakketou, F. et al. (2022). Investigating User Radicalization: A Novel Dataset for Identifying Fine-Grained Temporal Shifts in Opinion. LREC 2022. arXiv:2204.10190.


# Appendix A. Limitations and Dual-Use / Ethical Considerations

**Limitations, and how each would change the reading.**

1. **No user study.** We measure whether the tool surfaces changes of mind, not whether surfacing them helps people reach decisions they later endorse. The real-text sets stand in for a person's record and for endorsement: the authors endorsed their change in print, not our flag. If people do not want narrated changes shown, the fix is a regression for them.
   - *Protocol for next time:* consenting users list their known changes of mind before running, rate each card ("would I want this shown?", "is it fair?"), and are re-asked a month later.
2. **Synthetic and historical text.** GPT wrote the planted posts: short, English, about philosophy. The real-text sets are published 18th-20th-century prose by famous authors, sampled from books, not posts or chats; 13 cases, 6 of them held out. A modern person's history is shorter per entry, noisier and mixed. The planted decoys are cleaner than real look-alikes, so the 0/96 false-flag rate is optimistic; real-text cards from the repaired pipeline were judged non-genuine in 7-10 of 25.
3. **One model family, in an agent harness.**
   - The production call uses the API with effort "medium" and a real system prompt. Here the prompt reached Haiku inside a subagent, as text.
   - A harness check with a different wrapper and production's effort setting reproduced the contrast (36/36 vs 15/36), but individual borderline items flip between runs (20/36 marked items agree), so the size of the effect in production is uncertain. The direction was consistent across all phrasings, sets and wrappers.
   - Sonnet 5.5 reproduced the drop and the repair, but it is the same family. A cross-family check was planned and cut when the free and subscription quotas for GLM and DeepSeek ran out. We did not use paid capacity.
4. **Contamination and small n.** Haiku named the author of 9 of the 10 paraphrased cases, and of 26 of the 27 real passages shown without names (it took Huxley's 1862 passage for Darwin). This should make the real reversals easier to find, so the production prompt's misses are not explained by it; the repairs' recall may be inflated by it. The held-out real comparisons rest on 6 cases; grouping v2 was tuned on the 6 development histories, and both of its held-out predictions narrowly failed (grouping v1's real-text prediction also failed; Appendix F). The whole-history comparison was added after our mock review asked for it, with three runs per history; its realX arm was predicted before each run (the first threshold equalled the naive baseline's already-seen score), and realX itself was tuned on development pairs shown alone, not on whole histories. Model grouping with the shipped prompt was not run on real text, so "neither fix alone" rests on the two cells we did run (word themes with any prompt; whole histories with the shipped prompt). Our real histories are 72-124 excerpts; a person's years of posts and chats are longer, which is where grouping, not the single call, has to work.
5. **The fix.**
   - The fix line was written by the author after seeing failures and frozen before held-out runs (commit times, Appendix C). Because it names the cue, its recovery on marked text is partly instruction-following.
   - The cue-free rewrite avoids this, but was chosen after the ablations, then tested on fresh items, the hand-written sets and end to end (Table 4). The whole-history realX fix is deployed (Nov 14) but its effect in production is unmeasured; the deployed prompt adds the shipped output rules (neutral question, at most 8 pairs) to the tested realX text.
6. **Judge.** We corrected four of our own planted labels after the judge disagreed. We report the uncorrected κ (0.69), and the main neutrality claim rests on lean-vs-neutral agreement, which the correction does not affect.

**Dual-use and ethics.**
- **Profiling.** Mapping a person's inconsistencies is a profiling capability. Pointed at someone else, the same pipeline is a tool for opposition research, harassment ("you said the opposite in 2019"), or for targeting persuasion at beliefs that are already wavering. Persona's design limits this:
  - it imports only accounts the person connects;
  - the model step is opt-in, under a separate consent;
  - the default detector runs on device and sends nothing;
  - excerpts are aliased, and nothing is stored server-side;
  - a weekly allowance caps use.
  These controls reduce misuse but do not prevent someone from uploading another person's public posts.
- **Steering.** A reflection tool can steer while appearing to inform. We measured question neutrality (97%) for that reason. The kind label is a framing risk: labelling any pair a year apart a "change of mind" frames the newer view as growth before the person has said which they hold. This happened for 17 of the 36 unsignalled test positives, purely by date (a count that follows our chosen gaps).
- **Data used in this paper.** No personal data was used. Test text is synthetic, paraphrased from published philosophy, or quoted from public-domain texts (pre-1930 publications and translations, from Project Gutenberg, Wikisource and archive.org); PhilPapers figures are used as aggregates under CC BY-NC. We did not use classroom data or anyone's Reddit history. A planned consented study of friends' histories was not run.
- **Effect of the fix.** It surfaces more cards. More cards could mean more pressure on people to "resolve" views they are happy to hold loosely. Persona lets people mark a pair "not a conflict" or "both", and those choices should stay one tap away.

# Appendix B. Prompts and the one-line fix

**Production system prompt** (`apps/api/src/features/persona/conflicts.ts`, `CONFLICTS_SYSTEM`), with the fix line in bold:

> You read excerpts one person wrote over time on one theme. Find where two of their own claims cannot both stand. Count a pair only when the person asserts both as their own view, on the same point, and they clash. **A change of mind still counts: if a later excerpt asserts, as their current view, something that cannot stand with what an earlier excerpt asserted, include the pair even when they say they have changed their mind.** Do not count: different points or a change of subject; questions, doubt, or being less sure than before; one excerpt simply being more careful than the other; describing, quoting or answering someone else's view; jokes. Most themes have none, and an empty list is the right answer then. Return at most 3 pairs, the sharpest first. [...format and injection-defence instructions omitted; full text in the repository...]

**The rewrite** (Section 4.2) makes two edits. It replaces the sentence "Count a pair only when the person asserts both as their own view, on the same point, and they clash." with:

> Count a pair only when each excerpt, at the time it was written, stated the person's own view, on the same point, and the two clash.

and deletes "Most themes have none, and an empty list is the right answer then." The ablation "definition only" makes the first edit alone.

**Placebo definition** (Section 4.2), reworded to the rewrite's length but keeping the production meaning:

> Count a pair only when the person asserts both excerpts as their own view, about the very same point, and the two of them clash.

**Naive baseline prompt:**

> Below is everything one person has written over the last few years, oldest first. [posts] Where does this person contradict themselves? List every pair of posts in which they hold views that cannot both be true.

**Generic contradiction prompts** (Section 4.2). Each was followed by the same JSON output instruction:

> A: Here are excerpts one person wrote over time. Find pairs of excerpts that contradict each other.
>
> B: You check a person's writing for inconsistencies. List pairs of their claims that are logically inconsistent with each other. Ignore pairs that are only on different topics.
>
> C: Which of these excerpts by one person contradict each other?

**Independently written strict prompts** (Section 4.2). Codex (GPT) was given this brief and asked for three prompts in different styles (terse, numbered checklist, careful analyst): a journaling app reads one person's dated excerpts on one theme and should show pairs where their own views conflict; false alarms annoy users, so do not flag doubt or uncertainty, questions, someone else's view, jokes, or a later excerpt that merely refines or qualifies an earlier one; return the same JSON with one neutral question. The brief does not mention changes of mind. The three prompts are stored verbatim in `paper/data/strict_prompts_gpt.json`. Two of them allow that a dated change may count.

**Sycophancy pilot (earlier in the sprint, not part of the main claims).** Claude Haiku, Sonnet and Opus, run as subagents, each stated each side of 60 contested claims in separate chats. They agreed with both sides in 1.7%, 3.3% and 5.0% of pairs. Persona's on-device stance reader agreed with an LLM judge at κ = 0.02, so the "your AI agreed both times" flag needs the model step, not the on-device reader.

# Appendix C. Reproducibility record

Each arm's design was committed before any of its outputs were written (commit times, ET, Nov 14, 2026):

| Commit | Time | Contents |
|---|---|---|
| b7478374 | 01:12:02 | Evaluation data, harness, and the frozen fix line; held-out outputs written from 01:12:33 |
| 0806cd7e | 01:19:38 | Stage 4 design: marker on all positives, three more phrasings, second hand-written set, held-out pipeline |
| 8bebec36 | 01:34:27 | Mechanism arms (neutral prefix, three ablations) with written predictions |
| d080008d | 01:44:11 | Definition rewrite arms and harness check with written predictions |
| c1768442 | 01:51:29 | Generic prompts (unmarked and marked) and marked decoys, with predictions |
| 27e2a576 | 01:56:21 | Generic prompts on held-out decoys, with prediction |
| eb441c20 | 02:07:16 | Fresh narrated set and spec, repairs on it and on the hand-written sets and end to end, generic prompt plus exclusion list, variance reruns, with predictions |
| bae1e53d | 02:30:29 | Placebo definition, definition-by-default runs, Sonnet arms and the extra-card audit, with predictions |
| b51afc32 | 02:45:56 | GPT-written strict prompts, and genX on the fresh, hand-written and reversal sets, with predictions |
| acd69f6f | 02:59:33 | Fresh-set repeat runs, with predictions |
| 5772fec9 | 12:53:19 | Real-text test (PLAN v11), before the passages were collected |
| 3588b8d4 | 13:08:32 | Real-text development cases, histories and requests, before any run |
| cee78eb2 | 13:13:17 | Model grouping (v12) with predictions, after its planted development run, before held-out or real runs |
| 3bc7caf0 | 13:18:34 | realX frozen after one development run; grouping v2 and held-out predictions (v13) |
| ab802c07 | 13:40:57 | Held-out real-text cases, coding and requests, before any held-out run |
| 44357d00 | 13:53:42 | Whole-history naive baseline, author probe and run 3 (v14), before any of their runs |
| 28a01cc9 | 13:57:59 | Whole history + realX prediction (v15), after the v14 results, before its run |
| b6d9298f | 14:04:21 | Runs 2-3 of both whole-history arms (v16), before either run |
| 65a2f2b9 | 14:22:18 | Production prompt on whole histories, closed-book probe, no-call analyses (v17), before any run |

Every number in this paper is listed with its source file in `paper/RESULTS.md`; scoring scripts are in `evals/conflicts/gen/`.

# Appendix D. Paired tests and pipeline losses

**Table 6. End to end** (shipped request builder, one run). Planted: 12 held-out histories (t12-t23). Real: pairs in one group, and reversals surfaced, over the development (10 pairs) and held-out (9) sets; *whole history* sends all 72-124 excerpts of a history in one call, so every pair is together.

| Grouping + prompt | Planted positives /20 | Planted decoys /40 | Cards (planted) | Real pairs together (dev, held-out) | Real surfaced (dev, held-out) |
|---|---|---|---|---|---|
| Word sort + production (shipped) | 9 | 0 | 17 | 0/10, 0/9 | 0/10, 0/9 |
| Word sort + rewrite | 12 | 0 | 28 | 0/10, 0/9 | – |
| Model grouping + production | 16 | 0 | 37 | 1/10 (v1), – | – |
| Model grouping + genX | 18 | 0 | 53 | 1/10 (v1), – | – |
| Model grouping v2 + realX | – | – | – | 4/10, 4/9 | –, 3/9 |
| Whole history + production (one call; majority of 3 runs) | – | – | – | all | 0/10, 0/9 |
| Whole history + naive prompt (one call; majority of 3 runs) | – | – | – | all | 3/10, 3/9 |
| **Whole history + realX** (one call; majority of 3 runs) | – | – | – | all | **4/10, 4/9** |

**Table 5.** Each prompt variant (run 1 only; Table 3 uses all runs) against production on the same 36 marked planted items and 10 marked reversals: items gained and lost, exact McNemar p, and the Holm-adjusted p over the five ablations.

| Variant | Planted: gained-lost | p | Holm p | Reversals: gained-lost | p |
|---|---|---|---|---|---|
| No exclusion list | 11-7 | 0.48 | 0.48 | 2-2 | 1.0 |
| No doubt line | 9-3 | 0.15 | 0.29 | 1-0 | 1.0 |
| No empty-list default | 18-0 | 7.6×10⁻⁶ | 3.1×10⁻⁵ | 3-1 | 0.63 |
| Rewritten definition | 18-2 | 0.0004 | 0.0012 | 6-0 | 0.031 |
| Rewritten definition, no empty-list default | 24-0 | 1.2×10⁻⁷ | 6.0×10⁻⁷ | 6-0 | 0.031 |

![**Figure 3.** Recall on 36 marked planted reversals against false flags on 40 held-out decoys (Haiku, first run). Squares: generic prompts. Teal triangles: GPT-written strict prompts. Grey: ablations. Blue: repairs. Orange: production.](figures/fig2_tradeoff.svg)

![**Figure 4.** The 46 planted positives through each stage of the shipped design (production prompt, all 24 test histories). The on-device detector and a word-overlap baseline are floors.](figures/fig3_funnel.svg)

**Other pipeline losses** (production prompt):
- The 60-character filter left 10 of 30 hand-written items with nothing to send.
- The 20-excerpt window covers 44% of a theme's entry pairs at 30 entries, 11% at 60 and 1% at 200 (Figure 5).
- The on-device detector found 0/46 planted conflicts and none of the ten reversals. It needs verdict words like "myth", while people state positions as propositions. On the hand-written set it found 2 of 18 positives (both double negations) and flagged 1 of 12 decoys.
- A naive whole-history prompt found 25/26 positives on 26-post histories where the pipeline found 20/26 (6 vs 1 discordant, p = 0.125). Over one merged 312-post history it found 16/26 and returned 213 pairs.

![**Figure 5.** Share of entry pairs within one theme that reach the model together, computed from the shipped request builder (20 excerpts spread over time).](figures/fig4_window.svg)

# Appendix E. Reversal cases, prompt variants and the neutrality judge

**Real-text cases.** Sourced by two Sonnet agents from a fixed brief (public domain, verbatim, the announced passage from a later, separate work where possible, a secondary source opened). Rejected candidates and reasons are in `paper/data/realtext_dropped*.json`. Weak points the agents flagged and we kept: three development and three held-out announced passages retract without stating the new view (coded before any run); the Peirce 1905, Kant 1770, Mill 1848 and Spencer texts are OCR; Mill's early passage is from Laughlin's 1884 abridgement; the held-out Nietzsche case is the weakest (his announced passage is about idealism in general).

**realX** (Section 4.3) is genX with this paragraph after its first line: "People rarely restate an old view in the same words. Also count a pair when a later excerpt rejects, abandons or corrects a view that an earlier excerpt states, even when the later one describes that view in general terms, refers back to the earlier writing instead of quoting it, or calls it a view the writer formerly held." and "(a view the writer says they once held is their own)" added to the someone-else exclusion. Model-grouping prompts are in `evals/conflicts/gen/group_prompts.json`.

**Self-reported reversals (paraphrased).**
- Kept by a fixed rule: the philosopher says in print that they changed their mind, the sentence was checked on an opened page, and two sources support it.
- The cases:
  - Wittgenstein (meaning);
  - Putnam (functionalism; realism);
  - Jackson (knowledge argument);
  - Ayer (verifiability);
  - Rawls (stability);
  - Nozick (minimal state);
  - Singer (preference utilitarianism);
  - Flew (atheism);
  - Russell (denoting).
- Each is a first-person paraphrase with names removed, dated 2016 and 2023.

**Prompt variants.** We tested the production prompt, the fix line (Appendix B), and five ablations:
- no exclusion list;
- no doubt line;
- no empty-list default;
- the definition rewritten to "each excerpt, at the time it was written, stated the person's own view";
- the rewrite plus no empty-list default.

Each ran on the marked planted items, the marked reversals, the natural narrations (P3) and the 40 held-out decoys. The three generic contradiction prompts (Appendix B) ran on the planted items, unmarked and marked, and the decoys; generic A also ran on the fresh set and, with the production exclusion list added, as genX.

**Example cards from the rewrite** (Haiku, first run; production missed all three):
- 2019 "I would take both boxes..."; later "I have come round to taking only the sealed box when the predictor has an excellent record. I used to insist on taking both..." → "Do you hold that you should take both boxes, or only the sealed box, when the predictor is excellent?"
- "I think numbers exist independently of us"; later "I no longer think numbers are things existing somewhere independently of us" → "Do you hold that numbers exist independently of us, or that they do not?"
- "...a belief is justified when it comes from a way of forming beliefs that usually gets things right"; later "I changed my mind about what ultimately supports a belief..." → "Do you think a belief is justified by a reliable method, or only by basic beliefs that do not borrow support from others?"

Each question is neutral, but it asks which view the person holds when they have already said. For narrated changes, a card that confirms ("You moved from X to Y; is that still where you stand?") may fit better than one that asks. That is a design question for the user study.

**Neutrality.**
- A GPT judge labels each tool-written question as neutral, leaning earlier, leaning later, or off target.
- On 30 hand-labelled real questions plus 12 planted leaning ones, lean-vs-neutral agreement was 41/42 (κ = 0.94).
- Four-label κ was 0.69, our primary figure. Four of our planted labels had the direction wrong; correcting them gives 0.90.

# LLM usage statement

Claude (Claude Code, Opus) planned, built and ran the evaluation harness and drafted this report under the author's direction:
- Claude subagents ran the literature and source checks, reviewed the plan, and critiqued the results.
- GPT (via Codex) wrote the synthetic test posts and served as the neutrality judge.
- Claude Sonnet relabelled items blind and, as two agents, sourced the real-text cases; Haiku and Sonnet labelled the real-text cards.
- Claude Haiku 5.5 is the system under test.

Every number in the report is tied to a result file in `paper/RESULTS.md`; numbers from before the real-text rounds were re-checked by separate reviewer agents (two full passes). The author is responsible for the content.

# Appendix F. Every arm and its prediction

Each row was committed before its outputs existed (Appendix C); three rows had no numeric prediction, as marked, and one was untestable. Failed predictions are kept in the paper. Counts in the text take one prediction per row (35 rows with a numeric prediction) and count a row as failed if any part of it failed.

| Round | Arm (Haiku unless stated) | Prediction | Outcome |
|---|---|---|---|
| Stage 4 | Marker on all 36 planted positives and three more phrasings (confirmatory; designed after the first reversal result) | Paired contrast, no numeric prediction | 36→11; 18/40 pooled |
| 1 | Neutral sentence | ≥ 33/36 and ≥ 8/10 | Held: 36, 8 |
| 1 | No exclusion list | ≥ 30/36, decoys above 0/40 | **Failed** on recall: 15; decoys 2/40 |
| 1 | No doubt line; no empty-list default | Partial recovery, order not predicted | 17; 29 |
| 2 | Definition only | ≥ 25/36, ≥ 6/10, ≤ 2/40 decoys | Held: 27, 8, 1 |
| 2 | Rewrite; harness check | Exploratory | 35; 15 marked under a second wrapper |
| 3 | Generic A, B, C marked; decoys | ≥ 30/36 in 2 of 3; ≥ 3/40 in 2 of 3 | Held: 36, 36, 36; 9, 6, 7 |
| 3 | Marker on decoys | ≤ 3/40 for both repairs | Held: 0, 0 |
| 4 | Fresh set, production | ≤ 10/20 | **Failed**: 14 |
| 4 | Fresh set, fix / rewrite / generic A | ≥ 16/20 each; look-alikes ≤ 3 (generic ≥ 4) | Held: 20, 18, 20; 0, 0, 0 (6) |
| 4 | Rewrite on hand-written sets; end to end | Hedged ≥ 12, decoys ≤ 2; ≥ 11/20, ≤ 2/40 | Held: 12, 0; 12, 0 |
| 4 | genX on planted and decoys | ≥ 30/36, ≤ 2/40 | Held: 36, 0 |
| 4 | Variance reruns | Production 8-18 per run; rewrite ≥ 30 | Held: 11, 9, 17; 35, 35, 32 |
| 5 | Placebo, with and without default | Within production's range; within 5 of no default | Held: 10.0; 24.7 vs 26.3 |
| 5 | Definition x default, 3 runs | All four effects positive; rewrite ≥ 30 | Held |
| 5 | Sonnet: plain, neutral, marked, rewrite, decoys | ≥ 32; within 3; ≤ 24; ≥ 30; ≤ 2/40 | Held: 36; 36; 14; 35; 0, 0 |
| 5 | Extra cards end to end | Non-conflict share within 15 points of production | Untestable: production had none; rewrite 4, all non-conflicts |
| 6 | GPT strict prompts | Plain ≥ 32; decoys ≤ 4/40; ≥ 1 loses ≥ 8 marked | **Failed** for 2 of 3 (36, 30, 31); held (0, 0, 0); **failed** (max loss 4) |
| 6 | genX on fresh, hand-written, reversals | ≥ 18, ≤ 2; ≥ 12, ≤ 2; ≥ 8/10 | Held: 19, 0; 12, 0; 9 |
| 7 | Fresh set, runs 2-3: production, rewrite, genX | Production 11-17 per run; rewrite ≥ 16, genX ≥ 17; look-alikes ≤ 2; gains' CIs exclude 0 | Production **failed** low: 14, 10, 8. Others held: 18, 19, 19; 19, 20, 20; 0 every run; +8.0 [4.7, 11.3], +9.0 [6.0, 12.0] |
| 10 (v11) | Real text, Test A: rewrite and genX on development announced pairs | ≥ 80% each; production ≤ 50%; failure if both < 60% | **Failed**: 4/21, 5/21 (production 3/21); failure condition met |
| 10 | Real text: unannounced vs announced, production | ≥ +30 points | **Failed**: 33% vs 14% |
| 10 | Real text: controls | ≤ 10% every arm | Held: 0/21 each |
| 10 | Real text: word sort, early and later in one theme | ≤ 70% | Held: 0/10 |
| 11 (v12) | Model grouping, held-out planted, together | ≥ 18/20 | Held: 18 |
| 11 | Model grouping, real development, together | ≥ 6/10 | **Failed**: 1/10 |
| 11 | Model grouping + genX end to end, held-out planted | ≥ 17/20, ≤ 2/40 | Held: 18, 0 |
| 12 (v13) | realX on unseen planted, fresh and hand-written sets | Decoys ≤ 2, ≤ 2, ≤ 2; fresh ≥ 18/20 | Held: 0, 0, 1; 20 |
| 12 | Held-out real, new-view cases: realX; genX | realX ≥ 60%; genX ≤ 40% | realX held (6/6 tries, runs 1-2); genX **failed** (5/6) |
| 12 | Held-out real: grouping v2 together; with realX surfaced | ≥ 50%; ≥ 40% | **Failed** narrowly: 4/9; 3/9 |
| 13 (v14) | Whole history in one call, naive prompt, real text | ≤ 4/19 surfaced; > 3 pairs per history | **Failed** both (it did better): 7/19; 2.8 |
| 13 | Author probe, real passages | ≥ 15 named correctly | Held: 26/27 |
| 13 | Held-out Test A, run 3 | Each arm within 1 of its mean of runs 1-2; controls 0 | Production, realX held (1 vs 1, 5 vs 4.5); genX **failed** (2 vs 4); controls 0 |
| 14 (v15) | Whole history + realX, real text | ≥ 7/19 surfaced (held-out ≥ 4/9), thresholds set at the naive baseline's already-seen scores; ≤ 2.8 pairs per history; controls in ≤ 1 history | Held: 10/19 (6/9); 2.3; 0 |
| 14 | Its cards, blind Haiku and Sonnet labels | Real share ≥ naive's (23/34, 24/34) | Held: 23/27, 25/27 |
| 16 (v17) | Whole history + production prompt, real text | 2-6 of 19 surfaced (majority of 3 runs) | **Failed**: 0 |
| 16 | Closed-book probe, 13 cases | Change and direction stated for ≥ 9 | **Failed**: 7 |
| 15 (v16) | Whole history, runs 2-3 | realX ≥ 8/19 in each; realX 3-run mean ≥ naive's + 1.5; realX controls in ≤ 1 history per run | **Failed**: 7, 5; held: 7.3 vs 5.0; held: 0 |

The v12 prediction for model grouping + genX end to end on real text was not tested (version 1 was replaced before any real end-to-end run).

Exploratory comparisons beyond these rows (by-type breakdowns, item-level variance) are reported as descriptive only.
