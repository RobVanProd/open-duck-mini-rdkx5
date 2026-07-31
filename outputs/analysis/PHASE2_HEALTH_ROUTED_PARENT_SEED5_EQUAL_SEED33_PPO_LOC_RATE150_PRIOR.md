# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_health_routed_parent_seed5_augmented_manifest.json`
- samples: `6000`
- weighted samples: `8560.0000`
- pairs: `5992`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_health_routed_parent_seed5_equal_seed33_ppo_loc_rate150_prior/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_health_routed_parent_seed5_equal_seed33_ppo_loc_rate150_prior/candidate.onnx`

## Fit Metrics

- MAE: `0.001895`
- p95 abs error: `0.005423`
- max abs error: `0.020492`
- target-rate p95: `1.383798` rad/s
- target-rate max: `1.582585` rad/s
- sample weight p50/p95/max: `1.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.102941 |
| 1000 | 0.000043 |
| 2000 | 0.000018 |
| 3000 | 0.000046 |
| 4000 | 0.000011 |
| 5000 | 0.000012 |
| 6000 | 0.000007 |
| 7000 | 0.000009 |
| 8000 | 0.000015 |
| 9000 | 0.000017 |
| 10000 | 0.000006 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000015`
- max abs error: `0.00000025`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
