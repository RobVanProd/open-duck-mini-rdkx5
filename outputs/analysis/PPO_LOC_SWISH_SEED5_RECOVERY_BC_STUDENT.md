# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/ppo_swish_seed5_recovery_manifest.json`
- samples: `9342`
- pairs: `9316`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/ppo_loc_swish_seed5_recovery_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/ppo_loc_swish_seed5_recovery_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.011601`
- p95 abs error: `0.035147`
- max abs error: `0.266879`
- target-rate p95: `2.232609` rad/s
- target-rate max: `4.324731` rad/s

## Loss

| step | loss |
|---:|---:|
| 1 | 0.192597 |
| 500 | 0.000841 |
| 1000 | 0.000650 |
| 1500 | 0.000610 |
| 2000 | 0.000477 |
| 2500 | 0.000453 |
| 3000 | 0.000552 |
| 3500 | 0.000444 |
| 4000 | 0.000404 |
| 4500 | 0.000389 |
| 5000 | 0.000376 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000016`
- max abs error: `0.00000031`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
