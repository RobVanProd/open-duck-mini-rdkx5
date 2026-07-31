# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/filtered_source_vx_selector_dagger6_recovery_manifest.json`
- samples: `19628`
- pairs: `19585`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/ppo_loc_dagger6_recovery_student_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/ppo_loc_dagger6_recovery_student_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.014300`
- p95 abs error: `0.044702`
- max abs error: `0.375403`
- target-rate p95: `2.351068` rad/s
- target-rate max: `4.737401` rad/s

## Loss

| step | loss |
|---:|---:|
| 1 | 0.186796 |
| 500 | 0.000993 |
| 1000 | 0.000774 |
| 1500 | 0.000753 |
| 2000 | 0.000776 |
| 2500 | 0.000657 |
| 3000 | 0.000686 |
| 3500 | 0.000616 |
| 4000 | 0.000558 |
| 4500 | 0.000556 |
| 5000 | 0.000676 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000017`
- max abs error: `0.00000032`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
