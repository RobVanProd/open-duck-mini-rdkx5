# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/filtered_source_vx_selector_dagger7_targeted_recovery_manifest.json`
- samples: `22778`
- pairs: `22635`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/ppo_loc_dagger7_targeted_recovery_student_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/ppo_loc_dagger7_targeted_recovery_student_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.013451`
- p95 abs error: `0.043166`
- max abs error: `0.390570`
- target-rate p95: `2.379108` rad/s
- target-rate max: `4.556419` rad/s

## Loss

| step | loss |
|---:|---:|
| 1 | 0.206706 |
| 500 | 0.000939 |
| 1000 | 0.000765 |
| 1500 | 0.000745 |
| 2000 | 0.000630 |
| 2500 | 0.000675 |
| 3000 | 0.000559 |
| 3500 | 0.000622 |
| 4000 | 0.000594 |
| 4500 | 0.000590 |
| 5000 | 0.000521 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000017`
- max abs error: `0.00000034`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
