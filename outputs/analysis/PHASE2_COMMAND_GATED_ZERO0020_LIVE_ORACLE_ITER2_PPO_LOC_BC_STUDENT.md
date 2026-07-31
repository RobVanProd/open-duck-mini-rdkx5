# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2/live_oracle_dagger_aggregate_manifest.json`
- samples: `11555`
- weighted samples: `19827.0000`
- pairs: `11539`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.002748`
- p95 abs error: `0.010067`
- max abs error: `0.198142`
- target-rate p95: `1.220553` rad/s
- target-rate max: `2.245606` rad/s
- sample weight p50/p95/max: `1.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.112966 |
| 1000 | 0.000061 |
| 2000 | 0.000038 |
| 3000 | 0.000037 |
| 4000 | 0.000043 |
| 5000 | 0.000048 |
| 6000 | 0.000025 |
| 7000 | 0.000032 |
| 8000 | 0.000029 |
| 9000 | 0.000025 |
| 10000 | 0.000038 |
| 11000 | 0.000031 |
| 12000 | 0.000020 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000004`
- max abs error: `0.00000007`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
