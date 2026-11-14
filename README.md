# Persona audit: does a belief-mapping tool find real changes of mind?

Code, data and every model reply behind the Apart AI x Epistemics sprint paper (Track 3, Nov 13-16, 2026):
**"A belief-mapping tool misses the changes of mind people announce: an audit on planted items and philosophers' own writing"** — [`paper/paper.pdf`](paper/paper.pdf).

Persona (part of [Amphi](https://amphi-forum.org)) reads what a person has written and shows where their views conflict or have changed. We audited the shipped version against answer keys it cannot grade itself on: planted conflicts with known truth, and 13 documented changes of mind in public-domain writing by ten authors (Hume, Peirce, Nietzsche, Kant, Mill, Russell, Darwin, Newman, Spencer, Huxley).

**Headline:** the shipped pipeline surfaced 0 of 19 real early-to-later pairs. Its word-overlap theme sort never put the two views together, and its prompt found none even when given the whole history. Sending a history that fits in one call, with a prompt that counts a formerly held view (realX), surfaced 8 of 19 (majority of three runs). That fix was deployed to Persona on Nov 14, 2026.

## Layout

| Path | What |
|---|---|
| `paper/paper.md`, `paper.pdf` | The paper. `build_pdf.py` renders it (`uv run --with markdown python paper/build_pdf.py`). |
| `paper/RESULTS.md` | Ledger: every number in the paper with the file it comes from. |
| `paper/PLAN.md` | Each round's design and numeric predictions, committed before its runs. Failed predictions are kept. |
| `paper/REFLECTION.md` | What each round changed in our beliefs and plan. |
| `paper/data/` | Planted histories and answer keys, hand-written sets, the real-text cases (passages, source URLs, line spans, secondary sources) and histories. |
| `paper/results/` | Requests sent (`requests_*.jsonl`, with the exact system prompt), every raw model reply (`haiku_raw/`, `raw/`), and scores (`*_scores.json`). |
| `paper/research/` | Reviews and critiques of the plan written during the sprint. |
| `evals/conflicts/gen/` | Python scorers and builders. Run from the repo root, e.g. `python3 evals/conflicts/gen/score_v16.py .` (`score_v17.py` needs `uv run --with scikit-learn`). |
| `evals/conflicts/src/` | TypeScript request builders. They import Persona's own request builder and prompt, so they ran inside the Amphi monorepo; `src/shipped.ts` pins the Nov 1 prompt. |
| `product/shipped-2026-11-01/` | The audited product code (request builder, theme sort, prompt, limits) as shipped. |
| `product/deployed-2026-11-14/` | The same files after the fix: whole history in one request when it fits, realX prompt. |

## Reproducing numbers

All scorers read only files in this repo, so every reported number can be recomputed from the saved replies without model access. Model calls were made with Claude Haiku 5.5 (and Sonnet 5.5 for checks) through Claude Code subagents, one fresh agent per request; GPT (via Codex) wrote the planted posts and served as the question-neutrality judge.

## Data and licences

Real-text passages are public domain (pre-1930 publications and translations from Project Gutenberg, Wikisource and archive.org). PhilPapers 2020 figures are used as aggregates under CC BY-NC. Planted and hand-written items are synthetic. No personal data is included.
