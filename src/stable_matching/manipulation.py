"""Misreports used to experimentally test the paper's Section 2 properties."""
from itertools import permutations
import random


def exhaustive_individual_search(men_prefs, women_prefs, man, gale_shapley):
    """Test ALL n! reports for one man. Use n<=6 to avoid factorial blowup."""
    if len(men_prefs) > 6:
        raise ValueError('Exhaustive search limited to n <= 6; use sample_individual_search instead.')
    baseline = gale_shapley(men_prefs, women_prefs)
    old_rank = men_prefs[man].index(baseline[man]) + 1
    better = same = worse = 0
    for report in permutations(men_prefs[man]):
        changed = {m: list(p) for m, p in men_prefs.items()}
        changed[man] = list(report)
        new_matching = gale_shapley(changed, women_prefs)
        new_rank = men_prefs[man].index(new_matching[man]) + 1
        if new_rank < old_rank:
            better += 1
        elif new_rank == old_rank:
            same += 1
        else:
            worse += 1
    return {'improved': better, 'same': same, 'worse': worse, 'reports': better + same + worse}


def sample_individual_search(men_prefs, women_prefs, man, gale_shapley, samples=100, seed=None):
    """Sample alternative reports with a local reproducible RNG."""
    if samples < 1:
        raise ValueError('samples must be positive')
    rng = random.Random(seed)
    baseline = gale_shapley(men_prefs, women_prefs)
    old_rank = men_prefs[man].index(baseline[man]) + 1
    counts = {'improved': 0, 'same': 0, 'worse': 0, 'reports': samples}
    for _ in range(samples):
        changed = {m: list(p) for m, p in men_prefs.items()}
        changed[man] = rng.sample(men_prefs[man], len(men_prefs))
        new = gale_shapley(changed, women_prefs)
        new_rank = men_prefs[man].index(new[man]) + 1
        counts['improved' if new_rank < old_rank else 'worse' if new_rank > old_rank else 'same'] += 1
    return counts


def section2_misreports(true_men_prefs, baseline, liars, rng, mode):
    """Generate Huang Section 2 lists. mode='lemma1' or 'lemma2'.

    For Lemma 1, move a random subset X of women ABOVE the baseline partner
    to BELOW it, permuting within each side. For Lemma 2, only permute
    within each side. Never move the baseline partner itself.
    """
    if mode not in ('lemma1', 'lemma2'):
        raise ValueError('mode must be lemma1 or lemma2')
    changed = {m: list(p) for m, p in true_men_prefs.items()}
    for man in liars:
        p = true_men_prefs[man]
        pivot = p.index(baseline[man])
        left, right = p[:pivot], p[pivot + 1:]
        x = [w for w in left if rng.choice((True, False))] if mode == 'lemma1' else []
        kept = [w for w in left if w not in x]
        changed[man] = rng.sample(kept, len(kept)) + [baseline[man]] + rng.sample(right + x, len(right) + len(x))
    return changed
