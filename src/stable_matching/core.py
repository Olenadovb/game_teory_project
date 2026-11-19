"""Gale–Shapley baseline and validation. Preferences are dict[id, list[id]]."""
from collections import deque
import random


def validate_preferences(men, women):
    if not men or set(men) != set(women):
        raise ValueError('Men and women must have the same nonempty participant IDs (e.g. 0..n-1).')
    ids = set(men)
    for side, name in ((men, 'men'), (women, 'women')):
        for participant, pref in side.items():
            if len(pref) != len(ids) or set(pref) != ids:
                raise ValueError(f'Invalid {name} preference list for {participant}: expected a permutation of {ids}')


def gale_shapley(men_prefs, women_prefs):
    """Return mapping man -> woman for the men-proposing deferred-acceptance algorithm."""
    validate_preferences(men_prefs, women_prefs)
    ranking = {w: {m: i for i, m in enumerate(pref)} for w, pref in women_prefs.items()}
    next_choice = {m: 0 for m in men_prefs}
    free = deque(men_prefs)
    engaged = {}  # woman -> man
    while free:
        m = free.popleft()
        if next_choice[m] >= len(men_prefs):
            raise RuntimeError('Participant exhausted choices (should never happen with complete lists).')
        w = men_prefs[m][next_choice[m]]
        next_choice[m] += 1
        incumbent = engaged.get(w)
        if incumbent is None:
            engaged[w] = m
        elif ranking[w][m] < ranking[w][incumbent]:
            engaged[w] = m
            free.append(incumbent)
        else:
            free.append(m)
    return {m: w for w, m in engaged.items()}


def is_stable(matching, men_prefs, women_prefs):
    """Check stability with respect to the supplied (possibly reported) preferences."""
    validate_preferences(men_prefs, women_prefs)
    ids = set(men_prefs)
    if set(matching) != ids or set(matching.values()) != ids:
        return False
    women_partner = {w: m for m, w in matching.items()}
    women_rank = {w: {m: i for i, m in enumerate(p)} for w, p in women_prefs.items()}
    for m, prefs in men_prefs.items():
        for w in prefs[:prefs.index(matching[m])]:
            if women_rank[w][m] < women_rank[w][women_partner[w]]:
                return False
    return True


def partner_ranks(matching, true_men_prefs):
    """1-based ranks using TRUE preferences (never the falsified lists)."""
    return {m: true_men_prefs[m].index(w) + 1 for m, w in matching.items()}


def compare_ranks(baseline, alternative, true_men_prefs):
    before = partner_ranks(baseline, true_men_prefs)
    after = partner_ranks(alternative, true_men_prefs)
    return {m: 'improved' if after[m] < before[m] else 'worse' if after[m] > before[m] else 'same' for m in true_men_prefs}


def generate_preferences(n, seed=None):
    if n < 1:
        raise ValueError('n must be at least 1')
    rng = random.Random(seed)
    men, women = {}, {}
    for i in range(n):
        men[i] = rng.sample(range(n), n)
        women[i] = rng.sample(range(n), n)
    return men, women
