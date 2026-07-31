# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_merged_manifest.json`
- samples: `53130`
- weighted samples: `157111.6562`
- pairs: `53042`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_z0075_iter21_ppo_loc_swish_rate150_candidate/candidate_mlp.npz`
- ONNX: `policy/candidates/phase2_z0075_iter21_ppo_loc_swish_rate150_20260704/candidate.onnx`

## Fit Metrics

- MAE: `0.009427`
- p95 abs error: `0.031326`
- max abs error: `0.532789`
- target-rate p95: `1.361154` rad/s
- target-rate max: `8.851505` rad/s
- sample weight p50/p95/max: `3.0000` / `5.0000` / `8.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.113150 |
| 500 | 0.000459 |
| 1000 | 0.001158 |
| 1500 | 0.000546 |
| 2000 | 0.000835 |
| 2500 | 0.000273 |
| 3000 | 0.000398 |
| 3500 | 0.000267 |
| 4000 | 0.000315 |
| 4500 | 0.000305 |
| 5000 | 0.000333 |
| 5500 | 0.000308 |
| 6000 | 0.000219 |
| 6500 | 0.000283 |
| 7000 | 0.000356 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000015`
- max abs error: `0.00000031`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
