# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_000/live_oracle_dagger_aggregate_manifest.json`
- samples: `11500`
- weighted samples: `23964.0000`
- pairs: `11482`
- hidden sizes: `[128, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/live_oracle_dagger_phase_student_iter0_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/live_oracle_dagger_phase_student_iter0_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.013879`
- p95 abs error: `0.043352`
- max abs error: `0.268549`
- target-rate p95: `2.225589` rad/s
- target-rate max: `4.110077` rad/s
- sample weight p50/p95/max: `2.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.294067 |
| 500 | 0.000864 |
| 1000 | 0.000653 |
| 1500 | 0.000505 |
| 2000 | 0.000478 |
| 2500 | 0.000450 |
| 3000 | 0.000385 |
| 3500 | 0.000405 |
| 4000 | 0.000355 |
| 4500 | 0.000344 |
| 5000 | 0.000360 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000016`
- max abs error: `0.00000030`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
