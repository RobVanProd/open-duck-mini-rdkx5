# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_transition_protected_rate_limit_manifest.json`
- samples: `500`
- weighted samples: `1411.0000`
- pairs: `498`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_transition_protected_rate_limit_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_transition_protected_rate_limit_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.007776`
- p95 abs error: `0.022175`
- max abs error: `0.266933`
- target-rate p95: `2.206232` rad/s
- target-rate max: `3.578050` rad/s
- sample weight p50/p95/max: `2.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.207889 |
| 500 | 0.000540 |
| 1000 | 0.000447 |
| 1500 | 0.000354 |
| 2000 | 0.000363 |
| 2500 | 0.000340 |
| 3000 | 0.000316 |
| 3500 | 0.000276 |
| 4000 | 0.000305 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000015`
- max abs error: `0.00000026`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
