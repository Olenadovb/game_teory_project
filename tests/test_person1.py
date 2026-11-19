import random
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from itertools import permutations
from stable_matching import (gale_shapley, generate_preferences, is_stable, partner_ranks,
    exhaustive_individual_search, section2_misreports)


class MatchingTests(unittest.TestCase):
    def test_example(self):
        men = {0: [0, 1, 2], 1: [0, 1, 2], 2: [1, 0, 2]}
        women = {0: [1, 0, 2], 1: [0, 2, 1], 2: [2, 0, 1]}
        result = gale_shapley(men, women)
        self.assertEqual(result, {0: 1, 1: 0, 2: 2})
        self.assertTrue(is_stable(result, men, women))

    def test_stability_and_strategy_proofness(self):
        for seed in range(10):
            men, women = generate_preferences(4, seed)
            baseline = gale_shapley(men, women)
            self.assertTrue(is_stable(baseline, men, women))
            for man in men:
                result = exhaustive_individual_search(men, women, man, gale_shapley)
                self.assertEqual(result['improved'], 0)
                self.assertEqual(result['reports'], 24)

    def test_section2_lemmas(self):
        rng = random.Random(42)
        for n in (3, 4, 5, 8):
            for _ in range(40):
                men, women = generate_preferences(n, rng.randrange(2**32))
                base = gale_shapley(men, women)
                liars = rng.sample(list(men), rng.randint(1, n))
                for mode in ('lemma1', 'lemma2'):
                    changed = section2_misreports(men, base, liars, rng, mode)
                    new = gale_shapley(changed, women)
                    self.assertTrue(is_stable(new, changed, women))
                    if mode == 'lemma1':
                        rb, rn = partner_ranks(base, men), partner_ranks(new, men)
                        self.assertTrue(all(rn[m] <= rb[m] for m in men))
                    else:
                        self.assertEqual(new, base)

    def test_paper_figure_2(self):
        # Huang (2006), Fig. 2: A and E misreport; B and D improve.
        to_ids = lambda s: [ord(c)-ord('a') for c in s]
        men = dict(enumerate(map(to_ids, ['abedc', 'bedac', 'ebacd', 'dabce', 'edbca'])))
        women = dict(enumerate([[ord(c)-ord('A') for c in s] for s in ['CBDAE', 'DEABC', 'BCDEA', 'ABCED', 'ABECD']]))
        baseline = gale_shapley(men, women)
        self.assertEqual(partner_ranks(baseline, men), {0: 3, 1: 3, 2: 3, 3: 3, 4: 4})
        reported = {m: list(p) for m, p in men.items()}
        reported[0] = to_ids('aedcb')
        reported[4] = to_ids('ecabd')
        changed = gale_shapley(reported, women)
        self.assertTrue(is_stable(changed, reported, women))
        self.assertEqual(partner_ranks(changed, men), {0: 3, 1: 1, 2: 3, 3: 1, 4: 4})


if __name__ == '__main__':
    unittest.main()
