# Results ledger (Stage 3). Every number, the file it comes from, and how it was computed.

All paths are relative to `paper/results/` unless noted. Scripts: `evals/conflicts/src/*.test.ts` (run the shipped code), `evals/conflicts/gen/*.py` (generation, scoring).
"Haiku" = Claude Haiku 5.5 run through Claude Code subagents ("agent harness"), one fresh subagent per request, production system prompt passed verbatim, output parsed with the production `readConflicts`.

## Data
| Number | Source |
|---|---|
| Test set: 24 histories, 120 items (46 positive: P1 12, P2 14, P3 10, P4 10; 74 decoys D1-D7). 26 posts per history | `../data/test_spec.json`, `../data/answer_key.json`, `../data/histories.json`; writer GPT via Codex from `../data/LABELS.md` (`../data/writer_out/`) |
| Hand-written adversarial set: 30 items, 6 histories (18 positive: H1, H2, N1; 12 decoys: H3 sarcasm, N2 negated refinement) | `../data/adversarial.json` |
| Dev (template) set: 12 histories, 60 items | `../data/answer_key.json` (set=dev) |
| Blind label check: 149/150 agree, Cohen's kappa 0.986, 1 UNSURE | `blind_label_check.json` (Sonnet labeller, `blind_labels.jsonl`, `blind_rowmap.json`) |
| Reversal set: 10 cases, 9 independent authors (two Putnam cases share a source), endorsement sentences verified on opened pages | `../data/reversals.json`, `../data/reversals_sources.md` |
| PhilPapers 2020: 35 of 98 questions contested (top two both >=25%, within 15 points) | `../data/philpapers2020_contested.tsv` |

## Q1: philosopher reversals (n=10 cases)
| Number | Source |
|---|---|
| Production prompt, later view stated plainly: 9/10 (Wilson 95% [0.60, 0.98]) | `reversals_scores.json` reversals["prod/plain"] |
| Production prompt, same later view prefixed "I used to see this differently, but I've changed my mind.": 2/10 ([0.06, 0.51]) | reversals["prod/marker"] |
| Paired: 7 cases found plain and missed with marker, 0 the reverse; exact McNemar p = 0.016 | `marker_mcnemar.json` |
| Fixed prompt (one added line, `evals/conflicts/src/variant.ts`, frozen in commit b7478374 before these runs): 10/10 plain, 10/10 marker ([0.72, 1.0]) | reversals["fixed/plain"], ["fixed/marker"] |
| Same-era controls flagged: 0/7 in every arm; hard (same-topic, compatible) controls flagged with the later view: 0/9 in every arm | reversals[*].ctl_flags, hard_flags |
| Contamination probe: Haiku named the author in 9/10 cases (Nozick not recognised) | `reversals_scores.json` probe |
| On-device detector: 0/10 reversals (both arms) | `local_reversals.json` |

## Q2: planted conflicts, model step seeing the item (oracle: the item's own posts as one theme)
| Number | Source |
|---|---|
| Haiku, production, t00-t11: positives 22/26 (bootstrap 95% [0.76, 0.95]); P1 8/8, P2 5/5, P4 7/7, P3 2/6; decoys 0/34 | `scores.json` ["haiku/oracle"], `scores.txt` |
| Haiku, production, held-out t12-t23: P1 4/4, P2 9/9, P4 3/3, P3 0/4; decoys 0/40 (D1-D7 cells 7+6+6+4+7+6+4; an earlier '0/46' wrongly added the 6 hand-written sarcasm items, caught in mock judging) | `reversals_scores.json` heldout.prod |
| => Unsignalled positives (P1, P2, P4), all 24 histories: 36/36. Signalled changes (P3): 2/10. GPT-written decoys shown directly: 0/74 (34 + 40); with the 22 hand-written decoys (12 + 10), 0/96 | sum of the rows above and below |
| Haiku, fixed prompt, held-out t12-t23: P3 4/4, P1/P2/P4 16/16, decoys 0/40 | heldout.fixed |
| Haiku, production, hand-written (direct requests, no length filter): positives 18/18, decoys 0/12 (sarcasm 0/6, negated refinement 0/6) | `scores.json` ["haiku/direct"], heldout.prod |
| Haiku, fixed prompt, hand-written: H1 6/6, H2 4/6, N1 6/6; sarcasm 1/5 flagged (one reply missing: 199/200 calls succeeded), N2 0/6 | heldout.fixed |
| Run-to-run: 20 requests repeated, 20/20 same any-conflict decision, 17/20 identical pairs | `haiku_repeat_agreement.json` |
| On-device detector, test set: 0/46 positives, 0/74 decoys flagged; dev: 0/20, 0/40; hand-written: 2/18 positives (both double-negation), 1/12 decoys | `scores.json` ["local"] |
| Word-overlap baseline (Jaccard >= 0.15 + one side negated), test: 2/46 positives, 2/74 decoys | `scores.json` ["overlap"] |

## Q3: what the shipped pipeline loses before the model
| Number | Source |
|---|---|
| Test positives whose two posts `sortLibrary` puts in one theme: 30/46 (65%); decoys 41/74 | `scores.json` ["staged"] (computed in score.py `staged()`) |
| Hand-written: 11/18 positives in one theme; 10/30 items have a post under 60 characters, so no oracle request exists (`conflictRequests` drops excerpts under 60 chars) | `scores.json` staged; `requests.jsonl` (20 adversarial oracle requests) |
| Share of entry pairs in one theme that reach the model together (20-excerpt window): 100% up to 20 entries, 44% at 30, 24% at 40, 11% at 60, 3% at 120, 1% at 200 | `q3_window_coverage.json` (`evals/conflicts/src/window.test.ts`) |
| End-to-end Haiku pipeline, t00-t11: positives 20/26 (0.77 [0.57, 0.92]); P2 2/5; decoys 0/34 | `scores.json` ["haiku/pipeline"] |
| Naive "where do I contradict myself?" prompt over the whole history (26 posts): 25/26 (0.96), decoys 1/34 | `scores.json` ["haiku/naive_whole_history"] |
| Naive minus pipeline: +0.19 (paired bootstrap over histories [0.00, 0.45]); discordant items 6 vs 1 (exact McNemar p = 0.125, not significant) | `paired_diffs.json` |
| Naive on merged histories: 78 posts mean recall 0.85 across four merges (8/9, 5/5, 10/10, 1/2); 312 posts 16/26 (0.62); 624 posts not measured (the agent harness read only 340 of the entries) | `naive_long.json`, `haiku_raw/L24__naive.r1.txt` |

## Q4: does the card steer?
| Number | Source |
|---|---|
| Lean judge (GPT via Codex) validation: lean-vs-neutral agreement 41/42, kappa 0.94; 12/12 planted leans detected; 29/30 hand-labelled real questions judged neutral; four-label kappa 0.69 against our first-pass key, 0.90 after correcting 4 planted items whose direction we had keyed wrongly (disclosed in the file) | `q4_judge_validation.json`, `q4_validation_gold.json` |
| All 120 questions Haiku wrote: 116 neutral (96.7%, Wilson [0.917, 0.987]); 2 lean later, 1 lean earlier, 1 off target | `q4_summary.json`, `q4_all_gpt.jsonl`, `q4_rows_all.json` |
| Kind label: of 53 positives with no revision words (36 blind-test + 17 hand-written), 17 are labelled "change of mind" by elapsed time alone (>= 365 days); all 17 are blind-test items, so the paper reports 17 of the 36 unsignalled test positives (counts: test/live 19, test/date only 17). Mechanism only; the rate follows our chosen gaps | `kind_label.json` |

## Q5: sycophancy (pre-sprint harness, sprint pilot)
| Number | Source |
|---|---|
| Claude Haiku/Sonnet/Opus via subagents, 60 pairs: agreed with both sides 1.7%, 3.3%, 5.0%; on-device stance reader vs judge kappa 0.02 | `../../evals/sycophancy/results/subagent-pilot.md` |

## Stage 4 reruns (design committed 0806cd7e at 01:19:38 before any run; `rerun_scores.json`, `requests_rerun.jsonl`, script `evals/conflicts/gen/score_rerun.py`)
| Number | Source |
|---|---|
| The change marker ("I used to see this differently, but I've changed my mind.") added to post B of all 36 unsignalled test positives (P1 12, P2 14, P4 10), oracle, production prompt: found 36/36 unmarked → 11/36 marked (Wilson [0.18, 0.47]); 25 lost, 0 gained; exact McNemar p = 6.0e-8. By type: P1 12→4, P2 14→2, P4 10→5 | rerun_scores.json marker_positives |
| Same, fixed prompt: 36/36 | marker_positives.marked_fixed |
| Reversals, three more phrasings, production: "I've come around on this since I last wrote about it." 5/10; "My view on this has changed." 6/10; "I was wrong about this before." 5/10. With the first phrasing (2/10): 18/40 marked (Wilson [0.31, 0.60]) vs 9/10 plain | rerun_scores.json phrasings; reversals_scores.json |
| Reversals, three more phrasings, fixed prompt: 10/10 each (40/40 with the first phrasing); same-era controls 0 flagged; hard control flagged once in 40 (fixed/ph2) | phrasings |
| Second hand-written set (20 items, `../data/adversarial2.json`), production / fixed: hedged reversals 6/10 / 5/10; concessions 0/5 / 0/5 flagged; reaffirmations with change words 0/5 / 0/5 flagged | rerun_scores.json adversarial2 |
| Held-out pipeline end to end (t12-t23, 12 histories), production / fixed: positives 9/20 / 12/20 (P3 0/4 / 3/4; P1 4/4 both; P2 3/9 both; P4 2/3 both); decoys 0/40 both; flags per history 1.42 / 2.08 | rerun_scores.json pipeline_heldout |
| Held-out positives whose two posts share a theme: 11/20 (t00-t11: 19/26; all 30/46) | scores.json staged |

## Stage 6 mechanism reruns (design and predictions committed 8bebec36 before any run; `mech_scores.json`, `requests_mech.jsonl`, script `evals/conflicts/gen/score_mech.py`; 334/334 replies)
| Number | Source |
|---|---|
| Neutral, non-revision prefix ("I was reading about this again today.") on post B of the 36 unsignalled positives, production: 36/36. Paired with the change marker on the same items: 36 vs 11, 25-0 discordant, exact McNemar p = 6.0e-8 | mech_scores.json cells["neutralpos/P124/prod"], neutral_vs_marker |
| Same neutral prefix on the 10 reversals: 8/10 (plain 9/10, marker 2/10); controls 0 flagged | cells["rev/neutral/prod"] |
| Change marker under ablated prompts, 36 planted positives: no "Do not count" list 15/36; only the doubt line removed 17/36; "empty list is the right answer" line removed 29/36 (production 11/36, fixed 36/36) | cells["markerpos/P124/*"] |
| Same ablations, 10 marked reversals: 2/10, 3/10, 4/10 (production 2/10, fixed 10/10) | cells["rev/marker/*"] |
| Same ablations, GPT's natural narrated changes (P3, 10): 7/10, 3/10, 8/10 (production 2/10) | cells["oracle/P3/*"] |
| Same ablations, held-out decoys (t12-t23, 40): 2/40, 1/40, 0/40 flagged (production 0/40) | cells["oracle/DECOY/*"] |
| Prediction check: neutral prefix >= 33/36 and >= 8/10 (held); removing the "Do not count" list recovers >= 30/36 (failed: 15/36) | PLAN.md v4 |
| Headline 36 -> 11, history-cluster bootstrap (18 histories, 10,000 resamples, seed 20261114): drop 0.69, 95% CI [0.55, 0.84], no resample <= 0 | headline_cluster |
| Headline on held-out histories t12-t23 only (never used to write the fix): 16/16 unmarked -> 4/16 marked (12-0, exact p = 0.0005); fixed 16/16 | headline_heldout_only |
| Held-out pipeline end to end, production vs fixed, paired on the same 20 positives: 9 vs 12, 3-0 discordant, exact McNemar p = 0.25 (not significant) | mech_scores.json pipeline_heldout_fix_paired |

## Stage 6 round-2 reruns (design and predictions committed d080008d before any run; `requests_mech2.jsonl`, `mech_scores.json`; 264/264 replies)
| Number | Source |
|---|---|
| Definition rewritten only ("each excerpt, at the time it was written, stated the person's own view ... and the two clash"; no change-of-mind wording), marker present: planted 27/36 (18 gained, 2 lost vs production, exact p = 0.0004); reversals 8/10 (6-0, p = 0.031); natural narrations P3 10/10; held-out decoys 1/40 | mech_scores.json cells["*/defOnly"], ablation_vs_prod.defOnly |
| Definition rewritten and empty-list default removed: planted 35/36 (24-0, p = 1.2e-7); reversals 8/10 (6-0, p = 0.031); P3 8/10; decoys 0/40 | cells["*/defNoEmpty"], ablation_vs_prod.defNoEmpty |
| Paired vs production on the 36 marked planted items: noDNC 11 gained / 7 lost (p = 0.48); noDoubt 9/3 (p = 0.15); noEmpty 18/0 (p = 7.6e-6) | ablation_vs_prod |
| Prediction check (PLAN v5): defOnly >= 25/36 and >= 6/10 with decoys <= 2/40 (held: 27/36, 8/10, 1/40) | PLAN.md v5 |
| Harness check: same production requests, different wrapper, effort "medium" (run 3): unmarked 36/36, marked 15/36 (21-0, exact p = 9.5e-7). Item-level agreement with run 1 on marked items 20/36 (aggregate effect stable, item decisions near the boundary are not) | harness_check |
| Pooled marked reversals 18/40 (4 phrasings x 10 cases): case-level bootstrap 95% CI [0.23, 0.68] (the pooled Wilson [0.31, 0.60] assumes independence and is too narrow) | reversals_marked_case_bootstrap |

## Stage 6 round-3 reruns (designs and predictions committed c1768442 and 27e2a576 before running; `requests_mech3.jsonl`, `requests_mech4.jsonl`, `mech_scores.json`; 456/456 replies, 22 re-run after a full disk lost their first write)
| Number | Source |
|---|---|
| Three generic contradiction prompts (genA "find pairs that contradict each other"; genB consistency checker; genC one-line question), 36 planted positives: unmarked 36/36, marked 36/36 for each (0 lost) | mech_scores.json generic_prompts, cells["genplain/*"], ["genmarked/*"] |
| Same generic prompts on the 40 held-out decoys (unmarked): 9/40, 6/40, 7/40 flagged (production 0/40). Pooled by type: D2 doubt-only 16/18, D3 question 4/18, D5 1/21, D6 1/18, D1/D4/D7 0 | cells["gendecoy/*"], generic_decoys_by_type |
| Change marker pasted onto post B of the 40 held-out decoys: production 0/40, fix line 0/40, rewritten definition without empty-list line 0/40 | cells["markeddecoy/*"] |
| Prediction check (PLAN v6, v6b): generic marked recall >= 30/36 in >= 2 of 3 (held: 36/36 in all three); generic decoys >= 3/40 in >= 2 of 3 (held: 9, 6, 7); repairs on marked decoys <= 3/40 (held: 0, 0) | PLAN.md v6, v6b |
| Holm-adjusted p over the five prompt-variant tests on marked planted items: rewritten def. without empty-list 6.0e-7; no empty-list 3.1e-5; rewritten def. 0.0012; no doubt line 0.29; no exclusion list 0.48 | ablation_holm_planted |
| Wilson 95% upper bounds for zero false flags: 0/96 -> 3.8%; 0/40 -> 8.8% | computed: z^2/(n+z^2) |

## Round-4 confirmation (design and predictions committed eb441c20 before any run; `requests_mech5.jsonl`, `confirm_scores.json`, script `evals/conflicts/gen/score_confirm.py`; 511/511 replies, 306 re-run after a full disk lost their first write)
| Number | Source |
|---|---|
| Fresh narrated set (GPT via Codex from `../data/fresh_spec.md`; blind Sonnet labels agree 40/40, `fresh_blind_check.json`): 20 narrated reversals in varied wording (3 use "changed my mind"), 20 narrated look-alikes (7 refinements, 7 reaffirmations, 6 doubts) | `../data/fresh_narrated.json` |
| Fresh narrated reversals found: production 14/20; fix line 20/20; rewritten definition without empty-list line 18/20; generic A 20/20 | confirm_scores.json cells["fresh/NR/*"] |
| Fresh narrated look-alikes flagged: production 0/20; fix 0/20; rewrite 0/20; generic A 6/20 (all 6 doubts) | cells["fresh/lookalike/*"], ["fresh/ND/genA"] |
| Production misses on fresh reversals: f01, f07, f09, f15, f22, f40; found 6/9 that say "changed my mind", "I was wrong" or "I used to", 8/11 of the others | fresh_prod_nr |
| Generic A plus the production exclusion list ("genX"): marked planted 36/36; held-out decoys 0/40 (generic A alone: 36/36, 9/40) | cells["genmarked/genX"], ["gendecoy/genX"] |
| Rewrite on hand-written items: hedged reversals 12/16 (production 12/16, fix 9/16); reported view adopted 6/6; double negation 6/6; sarcasm 0/6; negated refinement 0/6; concession 0/5; reaffirmation 0/5 (decoys 0/22) | cells["hw/*/defNoEmpty"] |
| Rewrite end to end, held-out histories t12-t23: positives 12/20 (vs production 9/20: 3-0, p = 0.25), decoys 0/40, 2.33 pairs per history | pipeline_heldout_defNoEmpty |
| Variance, same wrapper: production marked planted 11/36, 9/36, 17/36 over runs 1, 4, 5 (14/36 items identical in all three); rewrite marked 35/36, 35/36, 32/36 (31/36 identical) | variance_marked |
| Prediction check (PLAN v7): fresh production <= 10/20 FAILED (14/20); all others held (fix 20 >= 16, rewrite 18 >= 16, generic 20 >= 16; look-alikes 0, 0, 0 <= 3 and generic 6 >= 4; hedged 12 >= 12; hand-written decoys 0 <= 2; end to end 12 >= 11 and 0 <= 2; genX 36 >= 30 and 0 <= 2; production runs 9-17 within 8-18; rewrite runs >= 30) | PLAN.md v7 |

## Stage 6 round-5 controls (PLAN v8, bae1e53d; scored by `evals/conflicts/gen/score_mech6.py` → `results/mech6_scores.json`)

Marked planted items (36), Haiku, three runs per cell (production 1, 4, 5; others 1, 2, 3). Mean = sum over items of each item's hit rate across runs.

| Arm | Runs | Mean of 36 | Items same all runs |
|---|---|---|---|
| production | 11, 9, 17 | 12.3 | 14 |
| placebo definition | 8, 7, 15 | 10.0 | 18 |
| no empty-list default | 29, 25, 25 | 26.3 | 19 |
| placebo, no default | 24, 26, 24 | 24.7 | 12 |
| definition only | 27, 31, 29 | 29.0 | 22 |
| rewrite (definition + no default) | 35, 35, 32 | 34.0 | 31 |

History-cluster bootstrap (10,000 resamples, seed 20261115) of the difference in item-mean recall, in items of 36 [95% CI] (`contrasts_items_of_36`):
- definition, default kept (definition only − production): +16.7 [11.6, 21.9]
- definition, default removed (rewrite − no default): +7.7 [5.2, 10.6]
- default removed, old definition (no default − production): +14.0 [10.5, 17.7]
- default removed, new definition (rewrite − definition only): +5.0 [1.9, 8.4]
- placebo − production: −2.3 [−5.8, 1.3]
- placebo no default − no default: −1.7 [−5.3, 2.6]
- definition only − placebo: +19.0 [13.4, 24.4]
- rewrite − placebo no default: +9.3 [6.0, 12.3]

Sonnet 5.5, same agent harness, one run (`sonnet`): unmarked 36/36; neutral 36/36 (0 lost); marked 14/36 (22 lost, 0 gained, McNemar p = 4.8×10⁻⁷); rewrite marked 35/36; held-out decoys 0/40 under production and 0/40 under the rewrite.

Extra-card audit (`extra_cards`; blind set `extra_cards_blind.json`, labels `extra_cards_labels.json`): end to end on t12-t23, production returned 17 pairs, all on planted reversals; the rewrite returned 28, of which 24 sit on planted reversals and 4 join posts of different planted items (histories t13, t21). The blind Sonnet labeller marked all 4 "not a conflict" (different points).

Predictions (PLAN v8): placebo within production's range — held (10.0; runs 7-15). Placebo no default within 5 of no default — held (24.7 vs 26.3). Both definition effects and both default effects positive — held. Rewrite highest, ≥ 30 — held (34.0). Sonnet unmarked ≥ 32 (36), marked ≤ 24 (14), neutral within 3 (36), rewrite ≥ 30 (35), decoys ≤ 2/40 (0, 0) — all held. Extra-card prediction (non-conflict share within 15 points of production's) could not be tested as written: production had no non-planted pairs; the rewrite's 4 were all non-conflicts.
- Saved replies after round 5: 2,891 files in results/haiku_raw (2,667 Haiku, 224 Sonnet `.rs1.txt`); after round 7: 3,567 files, 3,343 Haiku; counted with `ls | wc -l`.

## Round-6 generality arms (PLAN v9, b51afc32; `requests_mech7.jsonl`, scored by `evals/conflicts/gen/score_mech7.py` → `results/mech7_scores.json`; 436/436 replies, 1 re-run after the subagent returned without writing)

GPT-written strict prompts (`paper/data/strict_prompts_gpt.json`; Codex wrote them from a product brief that asks for few false alarms on doubt, questions, others' views, jokes and refinements, and never mentions narrated changes). Haiku, one run, 36 planted items (`strict_marker`, `cells`):

| Prompt | Unmarked | Marked | Lost-gained | Exact p | Held-out decoys flagged |
|---|---|---|---|---|---|
| gs1 (terse) | 36/36 | 32/36 | 4-0 | 0.125 | 0/40 |
| gs2 (checklist) | 30/36 | 35/36 | 0-5 | 0.0625 | 0/40 |
| gs3 (analyst) | 31/36 | 31/36 | 3-3 | 1.0 | 0/40 |

All misses were empty answers. Unmarked misses were P4 (buried) and P2 (reworded) items only: gs2 4 P4 + 2 P2, gs3 4 P4 + 1 P2.

genX (generic A + production exclusion list) on unseen sets (`cells`): fresh narrated reversals 19/20; fresh look-alikes flagged 0/20; hedged reversals 12/16; hand-written decoys flagged 0/22 (C1 0/5, C2 0/5, H3 0/6, N2 0/6); reported view adopted (H1) 6/6; double negation (N1) 6/6; marked philosophers' reversals 9/10, with controls flagged in 0/10 cases.

Predictions (PLAN v9): strict prompts unmarked ≥ 32/36 — held for gs1 only (36), failed for gs2 (30) and gs3 (31). Decoys ≤ 4/40 — held (0, 0, 0). At least one strict prompt loses ≥ 8 when marked — FAILED (largest loss 4, p = 0.125). genX: fresh ≥ 18 (19), look-alikes ≤ 2 (0), hedged ≥ 12 (12), hand-written decoys ≤ 2 (0), marked reversals ≥ 8 (9) — all held.

## Round-7 fresh-set repeats (PLAN v10, acd69f6f; `evals/conflicts/gen/score_fresh_runs.py` → `results/fresh_runs_scores.json`; 240/240 replies)

Fresh 40 items, runs 1-3, same wrapper. Narrated reversals found of 20: production 14, 10, 8 (10 of 20 items stable); rewrite (defNoEmpty) 18, 19, 19 (19 stable); genX 19, 20, 20 (19 stable). Look-alikes flagged: 0/20 for all three prompts on every run. Mean gain over production in items of 20 (each item's hit rate over three runs, bootstrap over the 20 items, 10,000 resamples, seed 20261115): rewrite +8.0 [4.7, 11.3]; genX +9.0 [6.0, 12.0].

Predictions (PLAN v10): production 11-17 per run — FAILED (10 and 8 on runs 2-3). Rewrite ≥ 16 and genX ≥ 17 on each run — held. Look-alikes ≤ 2 — held (0). Both gains' intervals exclude 0 — held.

Unnamed decoy types (the exclusion list does not name them): GPT-written D6 hypotheticals (10) and D7 restatements (11), and hand-written concessions (5) and reaffirmations using change words (5). Production flagged 0/31 (part of the 0/96).

## Round 10: real text (PLAN v11) and model grouping (PLAN v12)

| Result | Source |
|---|---|
| Real-text Test A, early + announced, 7 cases x 3 runs: production 3/21, rewrite 4/21, genX 5/21. On the 4 cases whose announced passage states the new view: 3/12, 4/12, 5/12. A1 FAILED (predicted rewrite and genX >= 80%); the stated failure condition (both < 60%) holds: the repairs do not transfer to real prose | real_scores.json A |
| Real-text Test A, early + unannounced, 4 cases x 3 runs: production 4/12, rewrite 5/12, genX 6/12. A2 FAILED (predicted unannounced >= announced + 30 points for production: 33% vs 14%, +19) | real_scores.json A |
| Real-text Test A, early + control, 7 cases x 3 runs: 0/21 flagged for every arm (A3 held) | real_scores.json A |
| Real-text Test B, word sort: early and later passage in one theme 0 of 6 histories (0 of 10 pairs; B1 predicted <= 70%, held far beyond); paragraphs in any theme 29-95 per history (32-77%); no arm surfaced any pair end to end (0/10). Cards: production 1, rewrite 6, genX 5 over 6 histories; 1 production request missing (Haiku returned no file) | real_scores.json B, real_themes.json |
| Model grouping (Haiku, prompts v1), dev t00-t11: planted positives in one group 26/26 (word sort 19/26) | group_themes_v1_dev.json; PLAN v12 |
| Model grouping, held-out t12-t23: positives in one group 18/20 (word sort 11/20); decoys in one group 17/40; posts grouped 212/312. G1 held (>= 18) | group_themes_v1_test.json |
| Model grouping end to end, held-out t12-t23: + production 16/20 positives, 0/40 decoys; + genX 18/20, 0/40. Against word sort + production (9/20): production 8 gained / 1 lost (exact McNemar p = 0.039), genX 10 / 1 (p = 0.012). G3 held. Cards: 37 and 53 over 12 histories (word sort + production 17), none joining two different planted items | group_scores_v1_test.json |
| Model grouping, real text: early and later passage in one group 1/10 (Peirce only); 337/615 paragraphs grouped; 46-92 merged groups per history, mostly of 1-3 paragraphs. G2 FAILED (predicted >= 6/10) | group_themes_v1_real.json |
| Grouping cost: 1 labelling call per 30 posts plus 1 merge call per history over 30 posts (planted: 1 call per history; real: 4-6) | make_group.py |
| Real-prose prompt realX_v1 (frozen after one dev run) on unseen sets, 1 run: planted held-out decoys 0/40, fresh look-alikes 0/20, hand-written decoys 1/22 (the sarcasm item a17: a sarcastic "sign me right up" read as endorsing eternal life), fresh narrated reversals 20/20. P1 held | realx_prec_scores.json |
| HELD-OUT real text (v13 set, 6 cases, 2 runs), Test A early + announced: production 2/12, genX 8/12, realX 9/12; on the 3 cases whose announced passage states the new view: 2/6, 5/6, 6/6. Unannounced (3 cases): 0/6, 1/6, 1/6. Controls 0/12 for every arm. P2: realX >= 60% HELD; genX <= 40% FAILED (genX 83% on these cases) | real2_scores.json A |
| Held-out word sort: early and later passage in one theme 0 of 9 pairs (dev set 0 of 10) | real2_themes.json |
| HELD-OUT grouping v2 (frozen after the dev set): early and later passage in one group 4 of 9 pairs (word sort 0 of 9); 659/741 paragraphs grouped; 15.7 groups per history, largest 17. P3 grouping >= 50% FAILED narrowly | group_themes_v2_real2.json |
| HELD-OUT end to end, grouping v2 + realX (1 run, 94 calls): documented reversals surfaced 3 of 9 (Darwin and Spencer announced, Nietzsche unannounced); word sort + any prompt 0 of 9 (never in one theme). P3 end to end >= 40% FAILED narrowly. 25 cards over 6 histories | group_scores_v2_real2.json |
| Real-text cards (34: 9 from v11 word-sort runs, 25 from held-out grouping v2 + realX), labelled blind by Haiku and Sonnet (same prompt, one call each) and by Claude (Opus, not blind to which run produced the card). Agreement: Sonnet-Claude 25/34 (kappa 0.46), Sonnet-Haiku 30/34 (0.74), Haiku-Claude 23/34 (0.34). Held-out end-to-end cards judged a real change or tension in the author's own views: Claude 16/25, Sonnet 16/25, Haiku 18/25, majority 15/25. Disagreements concentrate on passages where the author narrates his own change (Mill, Newman; the label prompt's "narrates" clause) and on Hume excerpts that present an alternative he goes on to reject | real_cards_labels_{claude,sonnet,haiku}.json, real_cards_labels.json (majority) |
| v11 word-sort cards judged real (majority): 2 of 9 (Nietzsche metaphysical comfort, a different early passage; Hume's Appendix on personal identity) | real_cards_labels.json |
| realX_v1 development run (tuning, 1 run): announced 4/7 (Peirce, Wagner, Mill, Russell; 0/3 retraction-only), unannounced 2/4, controls 0/7 | requests_realx_dev.jsonl, haiku_raw/realX1__realA__* |
| Saved replies after round 13: 4,712 files; Sonnet 225 (224 .rs1 + 1 card-labelling call); Haiku 4,487. Subagent tool calls average 2.0 per agent (e.g. 1,162 for 576; 188 for 94) | haiku_raw/, workflow usage |
| Planted end to end, model grouping: every card joins two posts of one planted reversal (cross-item 0, decoys 0); genX 53 cards for 18 reversals found, production 37 for 16 | group_scores_v1_test.json |

## Round 14: judge checks (PLAN v14)

| Result | Source |
|---|---|
| Whole-history baseline on the 12 real histories (one Haiku call each, naive prompt, 72-124 excerpts): 7 of 19 early-to-later pairs surfaced (development 3/10: Peirce, Russell announced, Kant unannounced; held-out 4/9: Darwin, Mill, Spencer announced, Nietzsche unannounced); 2.8 pairs returned per history. Prediction <= 4/19 FAILED (it did better); > 3 pairs per history FAILED (2.8) | v14_scores.json naive |
| Author probe: Haiku named the right author for 26 of 27 real passages (missed: Huxley 1862, attributed to Darwin). Prediction >= 15 held | v14_scores.json probe |
| Held-out Test A over 3 runs (announced): production 3/18, genX 10/18, realX 14/18; unannounced 1/9, 2/9, 3/9; controls 0/18 each. Run 3 vs mean of runs 1-2: production 1 vs 1, genX 2 vs 4, realX 5 vs 4.5; prediction (within 1) held for production and realX, FAILED for genX | v14_scores.json case_level |
| Case level, announced, found on a majority of runs: held-out production 1/6, genX 4/6, realX 5/6 (any run: 1, 5, 5); development (3 runs) production 1/7, rewrite 1/7, genX 2/7 (any run: 2, 2, 2) | v14_scores.json case_level |
| Whole-history baseline cards (34 over 12 histories; 17 held-out), labelled blind by Haiku and Sonnet with the same prompt as the grouping cards: Haiku 23/34 real (held-out 13/17), Sonnet 24/34 (held-out 12/17); raters agree 27/34 (kappa 0.52). Grouping v2 + realX held-out for comparison: Haiku 18/25, Sonnet 16/25. On these ~120-excerpt histories the single call surfaces more documented pairs (4/9 vs 3/9) with fewer cards and similar precision | v14_scores.json naive_cards |

## Round 15: whole history with realX (PLAN v15)

| Claim | Source |
|---|---|
| Whole history + realX on the 12 real histories (same 12 requests as the v14 baseline, system prompt realX_v1, one run): 10 of 19 pairs surfaced (development 4/10: Peirce, Russell announced; Nietzsche metaphysical comfort, Kant unannounced; held-out 6/9: Darwin, Newman, Mill, Spencer, Huxley announced, Nietzsche pity unannounced); 2.25 pairs per history; controls flagged in 0 of 12 histories. Prediction (>= 7/19, held-out >= 4/9, <= 2.8 pairs, controls <= 1) held | v15_scores.json, requests_v15.jsonl |
| Its 27 cards labelled blind (same prompt as the other real-text cards): Haiku 23/27 real (held-out 11/14), Sonnet 25/27 (held-out 13/14). Prediction (real share >= naive baseline's) held | v15_scores.json cards, wh_cards_blind.json, wh_cards_map.json |
| Size of the real histories in one call: 72-124 excerpts, user message 31,919-55,144 characters | requests_v14.jsonl |

## Round 16: whole-history reruns (PLAN v16)

| Claim | Source |
|---|---|
| Whole history, 3 runs on the 19 real pairs: naive 7, 4, 4 surfaced (held-out 4, 2, 2), controls flagged in 0, 1, 1 histories; realX 10, 7, 5 (held-out 6, 3, 3), controls 0, 0, 0. Pairs returned per run: naive 34, 31, 34; realX 27, 27, 30 | v16_scores.json per_run |
| Found on a majority of the 3 runs: naive 6/19 Wilson [0.15, 0.54] (dev 3/10, held-out 3/9); realX 8/19 [0.23, 0.64] (dev 4/10, held-out 4/9). realX vs naive: gained 2 (Huxley announced, Nietzsche metaphysical comfort unannounced), lost 0, exact McNemar p = 0.5 | v16_scores.json majority, mcnemar_realX_vs_naive, pairs |
| Predictions: realX >= 8 in runs 2 and 3 FAILED (7, 5); realX 3-run mean >= naive's + 1.5 held (7.33 vs 5.0); realX controls <= 1 per run held (0) | v16_scores.json per_run |
| Held-out Test A, three cases whose announced passage states the new view (Darwin, Spencer, Huxley), three runs: realX 9/9, genX 7/9, production 3/9 | v16_scores.json held_newview_testA_3runs |
| Harness read depth, whole-history calls (72 replies, 3 runs x 2 arms x 12 histories): 70 cite at least one excerpt; of those, 59 cite one in the last third of the request and 32 in the last tenth | read_depth.json (check_read_depth.py) |
| (Superseded by the v17 tally below.) Appendix F tally (one prediction per row, a row fails if any part fails): 34 rows with a numeric prediction; 12 failed (planted 4 of 18, real text 8 of 16) | paper.md Appendix F |

## Round 17: constructive-judge checks (PLAN v17)

| Claim | Source |
|---|---|
| Production prompt on the whole history (same 12 requests, 3 runs): 0 of 19 pairs surfaced on a majority of runs (0 in every run); it returned 4, 5 and 1 pairs in total over the 12 histories per run. Prediction (2-6 of 19) FAILED | v17_scores.json majority.production; requests_v17.jsonl |
| Announced vs unannounced, majority of 3 runs: realX 6/12 announced, 2/7 unannounced; naive 5/12, 1/7; production 0/12, 0/7; shipped pipeline 0/12, 0/7 | v17_scores.json majority |
| History-cluster bootstrap (12 histories, 10,000 resamples) of pairs surfaced per run: realX 7.34 [5.0, 9.67], naive 5.01 [2.33, 7.67], production 0; realX minus naive 2.33 [0.33, 4.67] | v17_scores.json cluster_bootstrap_pairs_per_run |
| Closed-book probe (author, years, question only; no text): Haiku stated the documented change and its direction for 7 of 13 cases (Nietzsche x3, Kant, Mill x2, Russell); "unknown" for Hume, Darwin, Newman, Spencer, Huxley; "no" for Peirce. Prediction >= 9 FAILED. Of the 8 pairs realX surfaces on a majority of runs, 4 are in cases Haiku could not recall (Darwin, Huxley, Peirce, Spencer) | v17_scores.json closed_book |
| TF-IDF cosine rank of each early passage's true later partner within its history (about 120 posts): median rank 72; top 5 for 2 of 19, top 20 for 2 of 19 | v17_scores.json tfidf_partner_rank |
| Appendix F tally after v17 (one prediction per row, a row fails if any part fails): 38 rows, 3 without a numeric prediction, 1 untestable; 35 numeric, 14 failed (planted 4 of 17, real text 10 of 18) | paper.md Appendix F |
| TF-IDF partner rank as a share of the history (rank / other posts): median 0.59; 8 of 19 later partners have cosine 0 with the early passage (no shared content word after stop-word removal) | v17_scores.json tfidf_partner_rank |
| Kind label ("change of mind" vs live) was added on 2026-11-13, during the sprint (commit 5609693d) | git log apps/web/src/features/vault/conflicts.ts |

## Deployment (2026-11-14)

| Claim | Source |
|---|---|
| Whole-history + realX deployed to Persona: Amphi main c27f1622 (web auto-deployed, Vercel status success); API deployed by hand, aliased to amphi-api.vercel.app, /health ok. Whole history goes in one request when it has at most 120 excerpts and 50,000 characters; otherwise per-theme requests of 20 as before. Prompt = realX_v1 text plus the shipped output rules (at most 8 pairs, neutral question, data-not-instructions) | product/deployed-2026-11-14/ in the public repo; Amphi commit c27f1622 |
| Public repository: https://github.com/28gugales-dev/persona-audit | |
| Saved replies after round 17: 4,871 files in results/haiku_raw/; Sonnet 227 (224 .rs runs + 3 Sonnet card-labelling calls); Haiku 4,644 | results/haiku_raw/ (file names: .rsN = Sonnet run, _s = Sonnet label call) |

## Round 18: scoring by change of mind, a second prompt, longer excerpts, two fresh held-out sets (PLAN v18-v18c)

| Claim | Source |
|---|---|
| Thesis labels (Haiku and Sonnet, blind, against the case's question), all 7 rounds pooled (a pair can appear in more than one round): key pairs 102/110 both-yes; random decoys 6/102 both-yes; returned off-key pairs 202/307 both-yes | thesis_cards_map{,3,x,x3,x4,x5,x6}.json, haiku_raw/label__thesis* |
| Case-level whole-history results, cross-era scoring, majority of runs (single call): production dev 1/12, fresh1 0/6; naive dev 10/12; realX dev 11/12, fresh1 4/6; changes dev 12/12, fresh1 4/6 | v18b_scores.json summary |
| Longer excerpts (min(1000, 120000 // n) characters), two calls merged, majority of looks: realX x2 dev 11/12, fresh1 5/6; changes x2 11/12, 6/6; realX + changes 11/12, 6/6 (controls per look 0.25, 0.75) | v18b_scores.json summary |
| Persona sends only the first 400 characters of each post (before Nov 14 evening); Godwin's and James's key words fall after that cut, and at 400 characters every prompt misses both | web conflicts.ts (excerptChars 400), v18b_scores.json |
| Control flags from the changes prompt read as real changes on another question (Spencer on women's political rights 1851 vs 1891; Romanes on theism) | requests_v18.jsonl, requests_v18b_chglong.jsonl, replies |
| One-shot test on fresh2 (Lyell x2, Besant, Darwin on Glen Roy, Buckland, Sedgwick), deployed configuration: 6/6 cases, 18/18 looks, controls 0; production 1/6; strict key pairs 22/27 vs 1/9 | v18b_scores.json fresh2, requests_v18c_*.jsonl |
| Deployed: Amphi main 34bfd61e (web Vercel success); API redeployed by hand, aliased to amphi-api.vercel.app, /health 200 | git log, vercel output |
| Harness fault found and fixed: 12 of 36 v18 subagents declined the eval step and replied with text containing "ok", which the runner counted; the runner now requires a bare "ok" and states the task source; missing replies re-run | haiku-ids runner, journal |
| Merged-look control flags (two runs of one prompt per look), longer excerpts: changes x2 0.5 per look (dev), 1.0 (fresh 1); realX x2 0, 0 | v18b_scores.json summary merged_controls_per_look |
| Fresh set 2 counting the two Lyell cases (same two works) as one: deployed 5/5, production 1/5 | v18b_scores.json cases (final, production) |
| Appendix F tally after round 18: 42 rows; 3 without a numeric prediction, 1 untestable; 38 numeric, 16 failed (planted 4 of 16, real text 12 of 22). The earlier "35 numeric" count was one too many (34) | paper.md Appendix F, counted by script |
| Production prompt, whole history: mean pairs returned per history 0.3 (dev), 0.0 (fresh 1), 0.2 (fresh 2) | v18b_scores.json pairs_per_history_run |

## Round 19 (v19): simpler arms on fresh set 2, prior-art-style prompts on all 24 (Haiku, 3 runs, 400 characters, case level, blind labels map x7)

| Arm | Dev /12 | Fresh 1 /6 | Fresh 2 /6 | Controls per run |
|---|---|---|---|---|
| naive | (10, earlier) | – | 5 (Lyell antiquity 0/3) | 0 |
| realX_v1 | (11) | (4) | 6 | 0 |
| changes_v1 | (12) | (4) | 6 | 0 |
| contradoc_style ("cannot both be true") | 3 | 2 | 2 | 0 |
| beliefshift_style (stance over time) | 10 (Hume 1/3, Spencer 1/3) | 5 (Godwin 3/3; James 0/3) | 6 | 0 |

- Fresh set 2 does not discriminate between the repaired configurations: single 400-character prompts find 5-6/6 there. The shipped prompt's 1/6 is the finding the set supports.
- x7 labels: key pairs 37/39 both-yes, decoys 1/24, returned 23/57. Pooled over eight rounds: keys 139/149, decoys 7/126, returned 225/364.
- Predictions (PLAN v19): fresh2 simple arms held; contradoc below realX held (3 vs 11, 2 vs 4); beliefshift ≥ realX failed on dev (10 vs 11), held on fresh1 (5 vs 4). Appendix F now 41 numeric rows, 17 failed (real text 13 of 25).
- Cost: 198 Haiku replies (~19.5M subagent tokens, mostly reading), 2 label calls.

## Round 20 (v20): card cost (existing replies, first run or look, 24 histories, blind real/not labels, Haiku + Sonnet)

| Arm | Cards | Per history | Both "real" | Haiku / Sonnet "real" | Not-real per history |
|---|---|---|---|---|---|
| Shipped prompt (400) | 5 | 0.21 | 3 (60%) | 4 / 3 | 0.08 |
| realX (400) | 60 | 2.5 | 50 (83%) | 52 / 54 | 0.42 |
| Deployed (realX + changes, longer, capped at 8) | 119 | 4.96 | 95 (80%) | 102 / 103 | 1.0 |
| Anchor: early + announced | 24 | – | 22 | 23 / 22 | – |
| Anchor: control + announced | 24 | – | 5 | 8 / 8 | – |

- Deployed exceeded the 8-card cap in 2 of 24 histories. Labeller agreement: realX 54/60, deployed 104/119.
- Prediction (PLAN v20): all parts held except controls ≤ 3/24 (5). Appendix F: 42 numeric rows, 18 failed (real text 14 of 26).
- Files: evals/conflicts/gen/make_cost_cards.py, score_cost.py; results/cost_cards_map.json, cost_scores.json.

## Round 21 (v21): fresh set 3, hard and sourced blind (Haiku, whole history, 3 runs or looks, case level, blind labels map x8)

Commits: plan + predictions e083b001 (02:18:52 ET Nov 15), cases cc168613 (02:51:20), first run after. Five of six announcements retract without restating the new view.

| Arm | Found /6 | Missed | Controls per run or look |
|---|---|---|---|
| Shipped prompt (400) | 0 | all | 0 |
| naive (400) | 2 | Coleridge, Miller, Frazer, Wordsworth | 0.33 |
| realX_v1 (400) | 4 | Coleridge, Wordsworth | 0.33 |
| changes_v1 (400) | 4 | Coleridge, Wordsworth | 0.33 |
| beliefshift_style (400) | 4 | Coleridge, Wordsworth | 0 |
| Deployed (realX_deployed + changes, longer; 12/18 looks) | 4 | Coleridge, Wordsworth | 0 |

- x8 labels: keys 9/12 both-yes (Wordsworth keys split 1-1, Frazer unannounced 0-2), decoys 0/6, returned 6/46. Pooled over nine rounds: keys 148/161, decoys 7/132, returned 231/410.
- Predictions: all held except the necessity test (deployed ≥ realX + 1): 4 vs 4. By the rule written beforehand, the second prompt and longer excerpts are not shown to help on unseen cases. Across both unseen sets: realX 10/12, deployed 10/12. All 30 cases: realX-400 25, deployed 27, shipped 2 (superseded: round 22 reran the shipped prompt on fresh sets 1-2 for three runs; 3 of 30 is the figure used).
- Appendix F: 43 numeric rows, 19 failed (real text 15 of 27). Cost: 126 Haiku replies, 2 label calls, one Sonnet sourcing agent.

## Round 22 (v22): definition swap on real text, and the retraction-link probe (plan 6ad576bd, 12:00 ET Nov 15, before any request)

Definition swap (whole history, 400 characters, 3 runs, 30 histories, case level, blind labels map x9). Shipped prompt now has 3 runs on every set (runs 2-3 on fresh sets 1-2 added here).

| Arm | Dev /12 | F1 /6 | F2 /6 | F3 /6 | Total /30 | Controls |
|---|---|---|---|---|---|---|
| Shipped prompt | 1 | 0 | 2 (Besant, Buckland) | 0 | 3 | 0 |
| defOnly (time-anchored definition) | 2 | 2 | 1 | 1 | 6 | 0 |
| defNoEmpty (that, and no empty-list default) | 5 | 2 | 2 | 2 | 11 | 0 |
| realX (for comparison) | 11 | 4 | 6 | 4 | 25 | – |

Retraction-link probe (14 cases whose announcement does not state the new view; longer excerpts; told which excerpt retracts; up to 3 candidates; credited if the keyed early passage or a both-labelled early paragraph is in the top 3): 11/14 on a majority of runs (top-1: 10). Missed: Hume 1/3 runs, Kant 0/3, Coleridge 1/3. Wordsworth credited 3/3 (via labelled early paragraphs), though no detection prompt found it.

- x9 labels: keys 48/51 both-yes (1 card missing a label), decoys 2/30, returned 31/39. Pooled over ten rounds: keys 196/212, decoys 9/162, returned 262/449.
- Predictions: definition-swap row failed (defOnly 6 < 8, defNoEmpty 11 < 14); link row failed on Hume. Appendix F: 45 numeric rows, 21 failed (real text 17 of 29).
- Shipped-prompt headline updated: 3 of 30 (was 2 of 30 with one run on fresh sets 1-2); fresh set 2: 2 of 6.

## Product change, Nov 15 (main c9a32b4c, API deployed, Aliased amphi-api.vercel.app, health 200)

findConflicts now asks realX (CONFLICTS_SYSTEM, deployed text) once, with longer excerpts; CHANGES_SYSTEM removed. Evidence: realX with longer excerpts 26/30 (dev 11, F1 5, F2 6, F3 4; F2-F3 from the first call of each two-call look) vs two-call 27/30 (only James differs, a tuning case); on the 12 unseen cases 10 each; the second call doubled non-genuine cards (round 20). API tests 55/55, typecheck clean.

## Round 23 (v23): GPT strict prompts on real text; card cost of what ships (plan e08fae03, 12:16 ET Nov 15, before any request)

GPT's three strict prompts (written from a brief asking for few false alarms; on planted items they kept 36, 30, 31 of 36 and lost 0-4 when marked), whole history, 400 characters, 3 runs, case level, blind labels map x10:

| Prompt | Dev /12 | F1 /6 | F2 /6 | F3 /6 | Total /30 | Controls |
|---|---|---|---|---|---|---|
| gs1 | 0 | 1 | 0 | 0 | 1 (Gladstone) | 0 |
| gs2 | 3 | 2 | 1 | 0 | 6 | 0 |
| gs3 | 1 | 0 | 0 | 0 | 1 (Peirce) | 0 |

What ships (realX, longer excerpts; first run; 30 histories; blind real/not card labels, cost23_scores.json): 101 cards, 3.37 per history, both "real" 74 (73%), Haiku 83 / Sonnet 80; not real 0.9 per history; none over the 8 cap. Anchors: keys 26/30 real, controls 4/30.

- x10 labels: keys 44/51 both-yes (the same 51 drew 48 in x9), decoys 1/30, returned 1/1. Pooled over eleven rounds: keys 240/263, decoys 10/192.
- Predictions: strict row failed (gs1 and gs3 below the shipped prompt's 3), its main clause held (all ≤ 15); card row failed on genuine share (73% < 75%). Appendix F: 47 numeric rows, 23 failed (real text 19 of 31).
- Reproducibility note: make_cost_cards.py keeps an arbitrary 8 cards for histories over the cap (S.pairs returns a set); 2 of 24 histories, 1 card differs between runs; round-20 files restored as committed.

## Round 24 (v24, plan b8d1a401): what ships as itself; the retraction paragraph crossed with the shipped prompt

Whole history, Haiku, 3 runs, case level (majority), blind thesis labels map x11 (Haiku + Sonnet), score_v18b.py. Request files requests_v24_genx.jsonl (prodPara, defNoEmptyPara, genX at 400 characters) and requests_v24_ships.jsonl (deployed realX text, min(1000, 120000 / posts)).

| Arm | Dev /12 | F1 /6 | F2 /6 | F3 /6 | Total | Controls |
|---|---|---|---|---|---|---|
| prodPara (shipped + realX's retraction paragraph + "a view the writer says they once held is their own") | 8 | 4 | 5 | 2 | 19/30 [0.46, 0.78] | 0 |
| defNoEmptyPara (time-anchored, no empty default, + same) | 9 | 4 | 5 | 3 | 21/30 [0.52, 0.83] | 0 |
| genX (realX without those additions) | 7 | 2 | 2 | 2 | 13/30 [0.27, 0.61] | F3 0.33 per run (1 history, 1 run) |
| ships (realX deployed, longer), own runs | – | – | 6 | 4 | 10/12 [0.55, 0.95] | 0 |

- Ships vs shipped prompt (2/12: Besant, Buckland) on the 12 unseen histories: ships-only 8, shipped-only 0, exact McNemar p = 0.0078. Missed: Coleridge, Wordsworth.
- Comparison cells (round 22, 23, earlier): shipped 3, defOnly 6, defNoEmpty 11, realX 25. Paragraph adds +16 (shipped), +10 (defNoEmpty), +12 (genX → realX).
- x11 labels: keys 47/51 both-yes (same 51 drew 48 in x9, 44 in x10), decoys 0/30, returned 13/23. Pooled over twelve rounds: keys 287/314, decoys 10/222.
- Predictions: ships row held (10 ≥ 9; p = 0.008 < 0.05; 0 controls). Factorial row failed: prodPara 19 > 12; defNoEmptyPara 21 ≥ 18 held; genX 13 ≤ 15 held; controls held. Appendix F: 49 numeric rows, 24 failed (real text 20 of 33).

## Round 25 (v25, plan 133fb59f): masked unseen histories, naive on all 30, analyses of existing replies

Masked = in fresh sets 2-3, author names and own-work titles replaced ("the author", "an earlier work"; 40 spans, 0 in four histories), dates shifted so each history starts in 2001 with gaps kept (make_masked.py). Names of other people (e.g. Lyell in Darwin's autobiography) left in. Haiku, 3 runs, case level, labels map x12 (judged on original text), score_v18b.py.

| Arm | F2 /6 | F3 /6 | Total | Controls |
|---|---|---|---|---|
| ships_masked (realX deployed, longer) | 6 | 4 | 10/12 (same 10 as unmasked; missed Coleridge, Wordsworth) | 0 |
| production_masked (shipped, 400) | 0 | 0 | 0/12 (unmasked: 2) | 0 |

- McNemar ships_masked vs production_masked: 10-0, p = 0.0020.
- Naive, fresh set 1 (requests_v25_naive_f1.jsonl): 3/6 (missed Romanes, Godwin, James). Naive all 30: 10 + 3 + 5 + 2 = 20 [0.48, 0.81]. realX (400) 25 vs naive 20: realX-only 5 (Frazer, Lyell antiquity, Miller, Nietzsche Wagner, Romanes), naive-only 0; exact McNemar p = 0.0625.
- analyze_v25.py (v25_analyses.json), majority of runs:
  - (a) credit without the keyed announced passage: realX 14/30, shipped 2/30, naive 10/24 (before fresh set 1), ships 5/12, prodPara 6/30 (19 with it), defNoEmptyPara 7/30, genX 7/30, stance 10/30.
  - (b) first two returned pairs per run only: realX 25/30 (unchanged), ships 10/12 (unchanged), realX_long 14/18 (16 with all), stance 24/30, genX 12/30.
- (c) Leakage: 0 of 1,582 real-text replies (haiku_raw/*realN*) match answer_key|realtext_cases|keyed|/Users/|worktree|paper/; 0 inputs match. Harness transcripts (6,333 text-completion agents): no agent that wrote a scored reply opened a case file, answer key or label map; agents that read PLAN.md / label scripts were the refusals of the round-18 declining batch, two of which then wrote replies (chg__realN__huxley_progressive_modification.r1, chg__realN__spencer_ethics_foundation.r2; changes prompt, dev).
- x12 labels: keys 29/32 both-yes, decoys 0/18, returned 4/11. Pooled over thirteen rounds: keys 316/346, decoys 10/240.
- Predictions: masked row held; naive row failed on p (0.06 vs < 0.05); (a), (b), (c) held. Appendix F: 54 numeric rows, 25 failed (real text 21 of 38).

## Round 26 (v26, plan 2211dd97): hard negatives and an evidence-quoting third judge

make_v26_labels.py, score_v26.py (v26_scores.json). Passages = history paragraphs cut to 1,000 characters.

- Haiku + Sonnet (map x13, usual blind prompt): hard negatives (control x announced/unannounced) both-yes 3/51 (Peirce announced, Romanes announced, Spencer announced; the first two disown the whole earlier work); keys 46/51 (not both-yes: Wordsworth announced, Kant announced, Frazer, James, Godwin unannounced).
- Opus 5.5 (map opus26, four files, verbatim quote required for yes; quotes checked after removing quote marks and whitespace): keys 42/51 (1 unanswered: Gladstone announced; no on 8, mostly unannounced passages cut at 1,000 characters: Spencer, Godwin, Ruskin, Russell, Frazer, James unannounced; Wordsworth, Kant announced); hard negatives 2/51 (Peirce, Romanes announced); credited off-key pairs 105/116 (1 unanswered, Sedgwick e9 x announced). Every yes quote verbatim.
- Case credit with Opus also required on off-key pairs (keys still credited): realX (400) 25 → 23 (fresh2 6 → 5, fresh3 4 → 3); ships unseen 10 → 10; ships masked 10; realX_long 16/18 unchanged; naive 20 unchanged; prodPara 19 → 18; shipped 3; shipped masked 0. realX vs naive: 3-0, p = 0.25. Ships vs shipped unseen: 10 vs 2, 8-0, p = 0.0078.
- Pooled keys over fourteen rounds: 362/397; random decoys 10/240; hard negatives 3/51.
- Predictions: row 1 held; row 2 failed on keys (42 < 45); row 3 held. Appendix F: 57 numeric rows, 26 failed (real text 22 of 41).

## Round 27 (v27, plan 33f11bfc): card cost of every main prompt, naive at longer excerpts, closed-book on later sets, author-level test

- Naive, longer excerpts (requests_v27_naive_long.jsonl, 3 runs; Gladstone r1 refilled after the agent returned text), labels x14: dev 9, F1 4, F2 5, F3 2 = 20/30; controls ≤ 0.67 per run.
- Card cost (make_cost_cards27.py, score_cost.py cost27 → cost27_scores.json; first run, cap 8, one fresh batch, Haiku + Sonnet, the round-20 real/not prompt; two Sonnet agents returned their labels as text instead of writing, saved verbatim: label__cost27_2_s, label__cost27_8_s, all cards present):

| Arm | Cards/history | Genuine (both real) | Not genuine/history |
|---|---|---|---|
| shipped | 0.20 | 2/6 (33%) | 0.13 |
| prodPara | 0.83 | 21/25 (84%) | 0.13 |
| gs2 | 0.27 | 8/8 | 0.00 |
| naive (400) | 2.33 | 33/70 (47%) | 1.23 |
| naive (longer) | 3.10 | 41/93 (44%) | 1.73 |
| realX (400) | 2.33 | 55/70 (79%) | 0.50 |
| ships | 3.37 | 71/101 (70%) | 1.00 (round 23 batch: 73%, 0.90) |
| anchors: keys / controls | | 26/30 / 3/30 | |

- Closed-book probe, 18 later cases (closedbook__later.r1, closedbook_later_items.json; the plan said 17, the later sets hold 18): Haiku stated the change for 8 (Freud, Gladstone, Lyell antiquity, Besant, Darwin Glen Roy, Sedgwick, Newton, Coleridge); unknown for 10. What ships found 8 of the 10 unknown (missed James, Wordsworth) and 7 of the 8 known (missed Coleridge).
- Author-level sign test, unseen sets, ships vs shipped (Lyell's two cases once): ships better for Lyell, Darwin, Sedgwick, Newton, Miller, Ruskin, Frazer (7); worse for none; ties Besant, Buckland, Coleridge, Wordsworth. p = 2 × 0.5^7 = 0.016.
- Predictions: naive-long row failed (20 < 22); cost row failed on shipped (0.13 > 0.1), held otherwise; closed-book row held; sign test held. Appendix F: 61 numeric rows, 28 failed (real text 24 of 45).

## Round 28 (v28, plan eda4f6a0): no-change histories, change-of-mind one-liner, bootstrap on the precision gap

- No-change histories (make_nochange.py; each case's early-work sampled paragraphs only, keyed early and control removed, 32-60 posts, redated evenly 2001-01 to 2006-12; one run per prompt; cards labelled in cost28, one batch with the one-liner's real-history cards; label__cost28_1_s returned as text by its agent and saved verbatim, all 50 cards present):

| Prompt | Cards/history | Both labellers "real" | Not genuine/history |
|---|---|---|---|
| shipped (400) | 0.03 | 1/1 | 0.00 |
| realX (400, tested text) | 0.33 | 2/10 | 0.27 |
| change-of-mind one-liner (400) | 0.70 | 1/21 | 0.67 |
| naive (400) | 0.93 | 2/28 | 0.87 |
| what ships (deployed text, longer) | 1.17 | 2/35 (Haiku alone 21) | 1.10 |

- Change-of-mind one-liner (requests_v28_naivechange.jsonl, 3 runs, labels x15): dev 11, F1 4, F2 6, F3 4 = 25/30; controls 0. First-run cards (cost28): 2.5 per history, 46/75 genuine (61%), 0.97 not genuine per history. Anchors in this batch: keys 25/30 real, controls 6/30.
- Bootstrap over histories (bootstrap_v28.py, v28_bootstrap.json; round-27 cards): realX (400) minus naive (400) genuine share +0.31 [0.19, 0.44]; non-genuine per history −0.73 [−1.13, −0.33].
- Predictions: no-change row failed (naive 0.93 < 1.5), held otherwise; one-liner row held; bootstrap row held. Appendix F: 64 numeric rows, 29 failed (real text 25 of 48).

## Round 29 (v29, plan 0b509794): the deployed prompt at 400 characters, a product decision

- requests_v29_dep400.jsonl (3 runs, labels x16) and requests_v29_nochange_dep400.jsonl (same excerpts and dates as round 28, one run); cards in cost29 (one batch; anchors keys 23/30, controls 5/30 real).
- Real histories: dev 11, F1 4, F2 6, F3 5 = 26/30 (missed Hume, Godwin, James, Coleridge; found Wordsworth); unseen 11/12; controls 0. First run: 3.1 cards per history, 66/93 genuine (71%), 0.90 not genuine per history.
- No-change histories: 0.80 cards per history, 4/24 genuine, 0.67 not genuine per history.
- Rule (written before the run): switch only if ≥ 24/30, ≥ 9/12 unseen, ≤ 0.7 non-genuine (real), ≤ 0.5 (no change). (a) holds; (b) 0.90 and (c) 0.67 fail → keep longer excerpts. Prediction row failed.
- Same length, different text: realX tested text at 400 raised 0.50 (real) and 0.27 (no change); the deployed text at 400 raised 0.90 and 0.67. The deployed text adds "Return at most 8 pairs, the sharpest first", the question format and an injection guard.
- Appendix F: 65 numeric rows, 30 failed (real text 26 of 49).

## Round 30 (v30, plan fc3f3559): the deployed prompt without "Return at most 8 pairs, the sharpest first", a product decision

- depNoCap = realX_deployed with that one line removed; longer excerpts. requests_v30_depnocap.jsonl (3 runs, labels x17), requests_v30_nochange_depnocap.jsonl (round-28 excerpts, one run); cards in cost30 (anchors keys 25/30, controls 3/30 real).
- Real histories: dev 10 (missed Hume, Russell), F1 6 (Godwin and James both found on a majority), F2 6, F3 4 (missed Coleridge, Wordsworth) = 26/30; unseen 10/12; controls 0.67 per run on dev. First run: 2.3 cards per history, 60/69 genuine (87%), 0.30 not genuine per history; none over the cap of 8.
- No-change histories: 0.50 cards per history, 3/15 genuine, 0.40 not genuine per history (what ships: 1.10).
- Rule: ship if ≥ 25/30, ≥ 10/12 unseen, ≤ 0.8 (real), ≤ 0.6 (no change). All held → shipped: main 2a5e359e (apps/api/src/features/persona/conflicts.ts; the parser still keeps the first 8), API typecheck clean, 1,744 tests pass, deployed with vercel deploy --prebuilt --prod, aliased https://amphi-api.vercel.app, /health 200.
- Prediction row failed only on (b): 0.30 below the predicted 0.5-0.8. Appendix F: 66 numeric rows, 31 failed (real text 27 of 50).

## Judge look 4 (round-30 draft), factual fixes

- Abstract: precision now quoted for what Persona runs (87% genuine, 0.30 non-genuine per history, cost30) beside naive 47% (cost27); "half its finds" replaced by 11 of 25 (realX at 400 without the announced passage).
- Table 4 caption: Ctrl is mean histories with a control flagged per run (Persona now 0.67 = Spencer in 2 of 3 runs); cards labelled one batch per round, rounds 27-30, anchors keys 23-26, controls 3-5 of 30; GPT strict cards are gs2 only.
- Final configuration's 26 is not the same 26 as the earlier deployed text: loses Russell (dev), gains James (F1).
- §3.3 now states Opus accepted 42 of 51 keyed pairs; plan-commit wording made consistent (rounds 18-20 committed after their runs).

## Round 31 (v31, plan e8982646): what Persona runs, without the announcing post

- Post-hoc (round-30 depNoCap runs, credit not counting pairs that use the announced passage; analyze_v25.py → v25_analyses.json): dev 7, F1 4, F2 1, F3 0 = 12/30; unseen 1/12.
- Announced post deleted from the input (make_noann.py → requests_v31_noann.jsonl; depNoCap, longer excerpts, 3 runs, labels x18: 61 cards, keys 18/21 both-yes, returned 8/10, decoys 5/30 both-yes): dev 7, F1 4, F2 3, F3 2 = 16/30; unseen 5/12; controls 0.33 per run on F1. Lost vs depNoCap with the announcement: Buckland, Darwin (utility, Glen Roy), Franklin, Frazer, Godwin, Mill, Miller, Sedgwick, Spencer; gained none. Of the 9 cases left with no later-passage key (no unannounced passage), 4 were found (Freud, Huxley, Newman, Peirce); of the 21 with one, 12.
- The post-hoc cut understated: with the announcement present the model spends its pairs on it; removed, it returns other cross-era pairs.
- Decoys both-yes 5/30 here (17%) against 10/240 before: this round's labels are looser, which favours the 16.
- Predictions: 12 (12-16) held; 16 (12-17) held; 5 of 12 (4-7) held; within 2 of post-hoc failed (16 vs 12); controls held. Appendix F: 67 numeric rows, 32 failed (real text 28 of 51).

## Round 32 (v32, plan d17c1fd6): one Sonnet + Opus labelling batch; matched card budget

- make_cost_cards32.py → cost32_cards_map.json, 450 cards in 9 files, labelled by Sonnet (_s) and Opus (_o), no Haiku. label__cost32_7_s returned its JSON instead of writing; saved verbatim (50 of 50 cards). cost32_scores.json; bootstrap_v32.py → v32_bootstrap.json.

| Arm | Cards | Both real | Not genuine/history | No-change not genuine/history |
|---|---|---|---|---|
| shipped (400) | 6 | 4 (67%) | 0.07 | 0.00 (1 card, real) |
| shipped + paragraph | 25 | 23 (92%) | 0.07 | – |
| naive (400) | 70 | 35 (50%) | 1.17 | 0.93 |
| change-of-mind one-liner (400) | 75 | 47 (63%) | 0.93 | 0.67 |
| realX (400) | 70 | 56 (80%) | 0.47 | 0.30 |
| Persona now (depNoCap, longer) | 69 | 61 (88%) | 0.27 | 0.40 |
| anchors key / control | 30 / 30 | 26 / 3 | | |

- Bootstrap over histories, Persona now minus naive: genuine share +0.38 [0.25, 0.51]; non-genuine per history −0.90 [−1.23, −0.57].
- Agreement Sonnet/Opus: 60-66 of 69-75 per main arm; control anchors Sonnet 8, Opus 3.
- Matched budget (analyze_v32.py → v32_budget.json; first k pairs per run): shipped 3/3/3; naive 18/20/20; realX (400) 24/25/25; one-liner 24/25/25; Persona now 24/25/26 (k = 1/2/all); unseen at k = 1: 2, 6, 9, 10, 10.
- Predictions: both rows held. Appendix F: 69 numeric rows, 32 failed (real text 28 of 53).

## Round 33 (v33, plan be99564a): recall split by closed-book memory

- Stated from memory (rounds 17, 27 probes): 14 cases; not stated: 16. From v18b_scores.json (majority of runs); v33_memory_split.json.

| Prompt | Found, stated (14) | Found, not stated (16) | Missed among not stated |
|---|---|---|---|
| shipped | 2 | 1 | 15 |
| naive (400) | 11 (79%) | 9 (56%) | Frazer, Godwin, Hume, James, Miller, Romanes, Wordsworth |
| one-liner | 13 | 12 | Godwin, Hume, James, Wordsworth |
| realX (400) | 13 | 12 | Godwin, Hume, James, Wordsworth |
| Persona now | 12 (86%) | 14 (88%) | Hume, Wordsworth |

- Predictions: Persona now ≥ 12 of 16 held (14); naive ≤ 10 held (9); within 20 points for every prompt failed (naive 23 points). Appendix F: 70 numeric rows, 33 failed (real text 29 of 54).
