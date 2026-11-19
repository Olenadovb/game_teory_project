# Huang (2006) — Person 1: baseline and individual manipulation

Copy the files into your existing Git repository root. Requires Python 3.9+ only; no packages or pip installation are necessary.

## Files
- `src/stable_matching/core.py`: preference validation, Gale–Shapley, stability, ranks.
- `src/stable_matching/manipulation.py`: individual misreports, Lemma 1/2 report generators.
- `run_experiments.py`: baseline, single-man manipulation and random Section 2 checks; CSV output.
- `tests/test_person1.py`: correctness, individual strategy-proofness, Lemmas 1/2 and paper Figure 2 example.
- `outputs/person1_results.csv`: generated after running.

## Run in VS Code terminal (repository root)

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m unittest discover -s tests -v
python run_experiments.py
```

Windows PowerShell:
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m unittest discover -s tests -v
python run_experiments.py
```

To do a faster demo:
```bash
python run_experiments.py --trials 10 --sizes 3 4 5 --seed 42
```

More trials:
```bash
python run_experiments.py --trials 500 --sizes 3 4 5 10 --seed 42
```

## Definitions
- `improved`: TRUE partner rank after manipulation is less than the truthful rank (1 is best).
- `same`/`worse`: equal/larger TRUE partner ranks.
- `reports`: number of individual reported preference lists checked across the trials.
- `average_baseline_rank`: average TRUE partner rank across trials, not a manipulated score.
- For n <= 6 the experiment checks every n! individual reports per sampled instance; for larger n it samples reports.
- `improved` must be 0 for individual proposers (strategy-proofness). Do not confuse this with coalition manipulation.
- Lemma 1/2 assertions are empirical checks for a collection of sampled instances, not proofs.
- The stable matching after a lie is verified against REPORTED preferences; rank welfare is always evaluated against TRUE preferences.

## Integration contract for Person 2
```python
from stable_matching import gale_shapley, generate_preferences, is_stable, partner_ranks, compare_ranks
men, women = generate_preferences(5, seed=42)
M0 = gale_shapley(men, women)
reported_men = {m: p.copy() for m, p in men.items()}
# Person 2 changes reported_men for a coalition
Ms = gale_shapley(reported_men, women)
assert is_stable(Ms, reported_men, women)
print(compare_ranks(M0, Ms, men))
```

## Source
Huang, C.-C. (2006), *Cheating by Men in the Gale-Shapley Stable Matching Algorithm*, Sections 1–3 (Fig. 1, Lemmas 1–2, Fig. 2).
https://www.di.ens.fr/~cchuang/work/marriage_cheating.pdf
