# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_terrain_live_oracle_dagger/iter_000/live_oracle_dagger_aggregate_manifest.json`
- samples: `1011`
- weighted samples: `2878.0000`
- pairs: `1004`
- hidden sizes: `[256, 256]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_terrain_live_oracle_dagger_iter0_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_terrain_live_oracle_dagger_iter0_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.007340`
- p95 abs error: `0.019478`
- max abs error: `0.394078`
- target-rate p95: `1.753598` rad/s
- target-rate max: `4.376833` rad/s
- sample weight p50/p95/max: `2.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.233912 |
| 750 | 0.000214 |
| 1500 | 0.000130 |
| 2250 | 0.000189 |
| 3000 | 0.000086 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000022`
- max abs error: `0.00000041`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
