# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_terrain_tracking_aware_bc_manifest.json`
- samples: `1150`
- weighted samples: `2797.0000`
- pairs: `1143`
- hidden sizes: `[256, 256]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_terrain_tracking_aware_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_terrain_tracking_aware_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.008591`
- p95 abs error: `0.023855`
- max abs error: `0.284242`
- target-rate p95: `1.940176` rad/s
- target-rate max: `2.531113` rad/s
- sample weight p50/p95/max: `2.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.279991 |
| 500 | 0.000514 |
| 1000 | 0.000309 |
| 1500 | 0.000281 |
| 2000 | 0.000227 |
| 2500 | 0.000177 |
| 3000 | 0.000176 |
| 3500 | 0.000201 |
| 4000 | 0.000176 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000021`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
