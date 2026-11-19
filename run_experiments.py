"""Run baseline, individual misreports and Huang's Section 2 lemma checks."""
import argparse
import csv
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from stable_matching import (gale_shapley, is_stable, generate_preferences, 
                             partner_ranks, exhaustive_individual_search, sample_individual_search, section2_misreports)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trials', type=int, default=100)
    parser.add_argument('--sizes', type=int, nargs='+', default=[3, 4, 5, 10])
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--samples', type=int, default=100, help='Misreports sampled for n > 6')
    parser.add_argument('--output', default='outputs/person1_results.csv')
    args = parser.parse_args()
    if args.trials < 1 or args.samples < 1 or any(n < 1 for n in args.sizes):
        parser.error('trials, samples and all sizes must be positive')
    rng = random.Random(args.seed)
    rows = []
    for n in args.sizes:
        totals = {'improved': 0, 'same': 0, 'worse': 0, 'reports': 0}
        total_rank = 0
        for _ in range(args.trials):
            men, women = generate_preferences(n, seed=rng.randrange(2**32))
            baseline = gale_shapley(men, women)
            assert is_stable(baseline, men, women)
            total_rank += sum(partner_ranks(baseline, men).values()) / n
            man = rng.randrange(n)
            result = (exhaustive_individual_search(men, women, man, gale_shapley)
                      if n <= 6 else sample_individual_search(men, women, man, gale_shapley, samples=args.samples, seed=rng.randrange(2**32)))
            for k in totals:
                totals[k] += result[k]
            # Verify Lemmas 1 and 2 on a *subset of men*, potentially multiple liars.
            liars = rng.sample(list(men), rng.randint(1, n))
            for mode in ('lemma1', 'lemma2'):
                reported = section2_misreports(men, baseline, liars, rng, mode)
                changed = gale_shapley(reported, women)
                assert is_stable(changed, reported, women)
                before = partner_ranks(baseline, men)
                after = partner_ranks(changed, men)
                assert all(after[m] <= before[m] for m in men) if mode == 'lemma1' else changed == baseline, f'{mode} failed'
        assert totals['improved'] == 0, 'Individual strategy-proofness unexpectedly violated'
        row = {'n': n, 'trials': args.trials, 'average_baseline_rank': round(total_rank / args.trials, 4), **totals}
        row['improved_pct'] = round(100 * totals['improved'] / totals['reports'], 2)
        row['same_pct'] = round(100 * totals['same'] / totals['reports'], 2)
        row['worse_pct'] = round(100 * totals['worse'] / totals['reports'], 2)
        rows.append(row)
        print(f"n={n:2d} | avg truthful rank={row['average_baseline_rank']:.3f} | reports={totals['reports']} | improved={totals['improved']} | same={totals['same']} | worse={totals['worse']} | lemma checks OK")
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print('Saved:', out.resolve())


if __name__ == '__main__':
    main()
