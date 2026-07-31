# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_002/live_oracle_dagger_aggregate_manifest.json`
- samples: `11500`
- weighted samples: `26757.0000`
- pairs: `11482`
- hidden sizes: `[128, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/live_oracle_dagger_phase_student_iter2_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/live_oracle_dagger_phase_student_iter2_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.013317`
- p95 abs error: `0.042437`
- max abs error: `0.377292`
- target-rate p95: `2.102227` rad/s
- target-rate max: `4.104966` rad/s
- sample weight p50/p95/max: `2.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.258958 |
| 500 | 0.000826 |
| 1000 | 0.000541 |
| 1500 | 0.000479 |
| 2000 | 0.000425 |
| 2500 | 0.000413 |
| 3000 | 0.000350 |
| 3500 | 0.000379 |
| 4000 | 0.000324 |
| 4500 | 0.000308 |
| 5000 | 0.000297 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000022`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
