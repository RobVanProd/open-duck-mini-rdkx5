# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_terrain_live_oracle_dagger/iter_002/live_oracle_dagger_aggregate_manifest.json`
- samples: `2511`
- weighted samples: `8335.0000`
- pairs: `2498`
- hidden sizes: `[256, 256]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.013927`
- p95 abs error: `0.043603`
- max abs error: `0.304107`
- target-rate p95: `1.583490` rad/s
- target-rate max: `4.142439` rad/s
- sample weight p50/p95/max: `4.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.196712 |
| 750 | 0.001091 |
| 1500 | 0.000848 |
| 2250 | 0.000538 |
| 3000 | 0.000489 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000020`
- max abs error: `0.00000033`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
