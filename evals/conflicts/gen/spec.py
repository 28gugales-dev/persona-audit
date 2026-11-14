"""Seeded spec for the blind test set: which topic, stance and label each item gets, and when.
The writer (GPT via Codex) turns each spec into posts from data/LABELS.md alone."""
import json, random, sys
SEED = 20261114
rng = random.Random(SEED)
ROOT = sys.argv[1]
bank = {q['id']: q for q in json.load(open(f'{ROOT}/evals/argue/bank/philosophy.json'))}
TOPICS = [('abstract_objects','platonism','nominalism'),('aesthetic_value','objective','subjective'),('moral_motivation','internalism','externalism'),
  ('newcomb','one_box','two_box'),('teletransporter','survival','death'),('time','a_theory','b_theory'),('extended_mind','extended','bounded'),
  ('immortality','choose','decline'),('sufficient_reason','holds','brute_facts'),('statue_and_lump','one_thing','two_things'),('time_travel','possible','impossible'),
  ('epistemic_justification','internalism','externalism'),('proper_names','fregean','millian'),('normative_ethics','consequentialism','deontology'),
  ('units_of_selection','genes','organisms'),('meaning_of_life','subjective','objective'),('knowledge_source','empiricism','rationalism'),
  ('material_composition','restrictivism','universalism'),('metaontology','heavyweight_realism','deflationary_realism'),('practical_reason','aristotelian','humean'),
  ('propositional_attitudes','dispositional','representational'),('values_in_science','necessarily_laden','laden_by_choice'),
  ('philosophical_progress','modest','substantial'),('continuum_hypothesis','determinate','indeterminate')]
LABELS = ['P1']*12 + ['P2']*14 + ['P3']*10 + ['P4']*10 + ['D1']*11 + ['D2']*11 + ['D3']*10 + ['D4']*11 + ['D5']*10 + ['D6']*10 + ['D7']*11
assert len(LABELS) == 120
rng.shuffle(LABELS)
GAPS = [2, 4, 6, 9, 14, 20, 30]  # months; under half are a year or more apart
def stmt(q, o): return next(x['statement'] for x in bank['phil.' + q]['options'] if x['id'].endswith('.' + o))
histories = []
for h in range(24):
    topics = rng.sample(TOPICS, 5)
    items = []
    for k, (q, o1, o2) in enumerate(topics):
        x, y = (o1, o2) if rng.random() < 0.5 else (o2, o1)
        label = LABELS[h * 5 + k]
        start = 2021 * 12 + rng.randrange(0, 30)
        gap = rng.choice(GAPS)
        items.append({'item': f't{h:02d}_{k}', 'label': label, 'question_id': 'phil.' + q, 'question': bank['phil.' + q]['question'],
                      'view_X': stmt(q, x), 'view_Y': stmt(q, y), 'a_month': f'{start // 12}-{start % 12 + 1:02d}',
                      'b_month': f'{(start + gap) // 12}-{(start + gap) % 12 + 1:02d}', 'gap_months': gap})
    histories.append({'history': f't{h:02d}', 'items': items})
json.dump({'seed': SEED, 'histories': histories}, open(f'{ROOT}/paper/data/test_spec.json', 'w'), indent=1)
from collections import Counter
print(Counter(LABELS), sum(1 for hh in histories for i in hh['items'] if i['gap_months'] < 12), 'pairs under a year')
