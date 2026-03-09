# Tests: Stochastic Generation

This folder contains tests for the stochastic state generation added in `ai/ai_abstract.py`.

Main test file:

- `test_stochastic_generation.py`

## What these tests check

- Dice outcome probabilities are complete and correct:
  - 21 unordered dice outcomes
  - total dice probability = `1.0`
- One-ply state distribution is valid:
  - non-empty
  - no negative probabilities
  - probabilities sum to `1.0`
- Determinism:
  - same input state gives same distribution result
- Multi-ply behavior:
  - `depth=0` returns exactly one state with probability `1.0`
  - `depth=1` matches one-ply generation
  - `depth=2` still forms a valid probability distribution
- Policy behavior:
  - `move_policy="best"` raises `ValueError` if no evaluator is provided
  - `move_policy="best"` with evaluator still returns a valid distribution

## How to run

From project root:

```bash
python -m pytest -q
```

## Expected result

You should see:

- `8 passed` (or more if new tests are added later)

## If a test fails

- `ModuleNotFoundError: No module named 'ai'`
  - Run from project root, or make sure `tests/conftest.py` exists.
- `sum != 1.0` assertions
  - Usually means probability aggregation changed or a move path is being dropped incorrectly.
- `best policy requires evaluator`
  - Pass `state_evaluator=...` when using `move_policy="best"`.
