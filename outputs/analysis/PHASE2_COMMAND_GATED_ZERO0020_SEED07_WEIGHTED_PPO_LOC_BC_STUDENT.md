# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_command_gated_zero0020_seed07_weighted_bc_manifest.json`
- samples: `7500`
- weighted samples: `10500.0000`
- pairs: `7490`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_command_gated_zero0020_seed07_weighted_ppo_loc_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_command_gated_zero0020_seed07_weighted_ppo_loc_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.001438`
- p95 abs error: `0.004171`
- max abs error: `0.011380`
- target-rate p95: `1.261821` rad/s
- target-rate max: `1.873344` rad/s
- sample weight p50/p95/max: `1.0000` / `3.0000` / `3.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.143107 |
| 500 | 0.000051 |
| 1000 | 0.000024 |
| 1500 | 0.000017 |
| 2000 | 0.000014 |
| 2500 | 0.000010 |
| 3000 | 0.000015 |
| 3500 | 0.000009 |
| 4000 | 0.000010 |
| 4500 | 0.000011 |
| 5000 | 0.000008 |
| 5500 | 0.000012 |
| 6000 | 0.000007 |
| 6500 | 0.000013 |
| 7000 | 0.000010 |
| 7500 | 0.000005 |
| 8000 | 0.000010 |
| 8500 | 0.000003 |
| 9000 | 0.000005 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000008`
- max abs error: `0.00000013`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
