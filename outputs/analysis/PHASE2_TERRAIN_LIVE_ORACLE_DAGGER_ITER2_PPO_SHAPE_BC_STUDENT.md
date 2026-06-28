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
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.008875`
- p95 abs error: `0.026690`
- max abs error: `0.272437`
- target-rate p95: `1.614097` rad/s
- target-rate max: `4.511911` rad/s
- sample weight p50/p95/max: `4.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.168654 |
| 500 | 0.001183 |
| 1000 | 0.000598 |
| 1500 | 0.000413 |
| 2000 | 0.000348 |
| 2500 | 0.000317 |
| 3000 | 0.000249 |
| 3500 | 0.000281 |
| 4000 | 0.000231 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000018`
- max abs error: `0.00000037`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
