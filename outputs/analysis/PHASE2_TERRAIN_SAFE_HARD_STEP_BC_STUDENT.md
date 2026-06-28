# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_terrain_safe_hard_step_bc_manifest.json`
- samples: `400`
- weighted samples: `400.0000`
- pairs: `396`
- hidden sizes: `[256, 256]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_terrain_safe_hard_step_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_terrain_safe_hard_step_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.003494`
- p95 abs error: `0.008626`
- max abs error: `0.018634`
- target-rate p95: `2.134406` rad/s
- target-rate max: `3.763411` rad/s
- sample weight p50/p95/max: `1.0000` / `1.0000` / `1.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.297825 |
| 500 | 0.000091 |
| 1000 | 0.000040 |
| 1500 | 0.000025 |
| 2000 | 0.000020 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000022`
- max abs error: `0.00000037`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
