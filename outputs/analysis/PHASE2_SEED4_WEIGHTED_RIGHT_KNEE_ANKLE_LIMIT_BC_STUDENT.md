# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_seed4_weighted_right_knee_ankle_limit_manifest.json`
- samples: `500`
- weighted samples: `500.0000`
- pairs: `498`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_seed4_weighted_right_knee_ankle_limit_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_seed4_weighted_right_knee_ankle_limit_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.002170`
- p95 abs error: `0.005617`
- max abs error: `0.031979`
- target-rate p95: `1.988126` rad/s
- target-rate max: `2.412099` rad/s
- sample weight p50/p95/max: `1.0000` / `1.0000` / `1.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.173772 |
| 500 | 0.000068 |
| 1000 | 0.000048 |
| 1500 | 0.000026 |
| 2000 | 0.000023 |
| 2500 | 0.000015 |
| 3000 | 0.000019 |
| 3500 | 0.000014 |
| 4000 | 0.000014 |
| 4500 | 0.000011 |
| 5000 | 0.000012 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000015`
- max abs error: `0.00000027`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
