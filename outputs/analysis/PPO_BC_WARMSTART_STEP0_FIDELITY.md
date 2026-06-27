# PPO BC Step-0 Fidelity

status: `HOLD_PPO_BC_STEP0_ACTION_FIDELITY`

This is an offline action-fidelity check. It did not train, deploy, SSH,
run robot tests, or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/source_vx_selector_trace_dagger3_manifest.json`
- BC NPZ: `outputs/analysis/source_vx_selector_trace_dagger3_mlp512_256_128_rate_reg_candidate/candidate_mlp.npz`
- samples: `9268`
- hidden sizes: `[512, 256, 128]`

## Baseline Consistency

Dataset trace actions compared with the BC NPZ prediction:

- p95 abs error: `0.043367`
- max abs error: `0.290411`

## Direct PPO Copy

Directly copying the BC final action head into PPO loc produces
`tanh(BC_raw_action)`, not `BC_action`. This is the measured mismatch:

- p95 abs error: `0.125398`
- max abs error: `0.211684`
- MAE: `0.030740`

## Final Loc Head Refit

Keeping the BC normalizer and hidden layers fixed, the final PPO loc head
was refit to `atanh(BC_action)`.

- best alpha: `0.01`
- p95 abs error: `0.012226`
- max abs error: `0.165617`
- MAE: `0.002886`

| alpha | p95 abs error | max abs error | MAE |
|---:|---:|---:|---:|
| 0 | 0.012243 | 0.166646 | 0.002887 |
| 1e-08 | 0.012243 | 0.166646 | 0.002887 |
| 1e-06 | 0.012243 | 0.166646 | 0.002887 |
| 0.0001 | 0.012243 | 0.166635 | 0.002887 |
| 0.01 | 0.012226 | 0.165617 | 0.002886 |

## Decision

Use final-head arctanh refit for PPO loc initialization; direct BC final-head copy is not exact because PPO exports tanh(loc).

This is still only an action-level step-0 check. If it passes, the
next gate must build actual PPO params with this loc head, keep value
params fresh, initialize scale logits deliberately, and run the
standard task-matched fitted closed-loop evaluator before any PPO
updates. If it holds, train or fit a PPO-loc student directly instead
of forcing an action-space BC head into a tanh-normal actor.
