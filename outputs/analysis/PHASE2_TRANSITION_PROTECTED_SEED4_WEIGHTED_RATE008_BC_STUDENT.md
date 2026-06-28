# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_transition_protected_seed4_weighted_manifest.json`
- samples: `500`
- weighted samples: `2747.0000`
- pairs: `498`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_transition_protected_seed4_weighted_rate008_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_transition_protected_seed4_weighted_rate008_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.009549`
- p95 abs error: `0.029385`
- max abs error: `0.307811`
- target-rate p95: `2.144853` rad/s
- target-rate max: `2.812821` rad/s
- sample weight p50/p95/max: `5.0000` / `15.0000` / `15.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.196570 |
| 500 | 0.000671 |
| 1000 | 0.000667 |
| 1500 | 0.000435 |
| 2000 | 0.000393 |
| 2500 | 0.000418 |
| 3000 | 0.000397 |
| 3500 | 0.000378 |
| 4000 | 0.000486 |
| 4500 | 0.000444 |
| 5000 | 0.000375 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000015`
- max abs error: `0.00000030`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
