# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_seed4_weighted_right_knee_limit_manifest.json`
- samples: `500`
- weighted samples: `500.0000`
- pairs: `498`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_seed4_weighted_right_knee_limit_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_seed4_weighted_right_knee_limit_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.003243`
- p95 abs error: `0.008071`
- max abs error: `0.035014`
- target-rate p95: `2.029987` rad/s
- target-rate max: `2.495348` rad/s
- sample weight p50/p95/max: `1.0000` / `1.0000` / `1.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.178537 |
| 500 | 0.000072 |
| 1000 | 0.000034 |
| 1500 | 0.000026 |
| 2000 | 0.000032 |
| 2500 | 0.000028 |
| 3000 | 0.000020 |
| 3500 | 0.000020 |
| 4000 | 0.000015 |
| 4500 | 0.000014 |
| 5000 | 0.000016 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000015`
- max abs error: `0.00000025`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
