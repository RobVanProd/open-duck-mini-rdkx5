# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_terrain_live_oracle_dagger/iter_001/live_oracle_dagger_aggregate_manifest.json`
- samples: `1761`
- weighted samples: `5938.0000`
- pairs: `1751`
- hidden sizes: `[256, 256]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_terrain_live_oracle_dagger_iter1_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_terrain_live_oracle_dagger_iter1_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.013701`
- p95 abs error: `0.042290`
- max abs error: `0.307172`
- target-rate p95: `1.558475` rad/s
- target-rate max: `4.122499` rad/s
- sample weight p50/p95/max: `4.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.226519 |
| 750 | 0.001546 |
| 1500 | 0.000721 |
| 2250 | 0.000512 |
| 3000 | 0.000416 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000024`
- max abs error: `0.00000044`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
