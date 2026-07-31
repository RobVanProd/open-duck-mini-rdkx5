# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/ppo_swish_seed5_source_vx_recovery_manifest.json`
- samples: `9342`
- pairs: `9316`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/ppo_loc_swish_seed5_source_vx_recovery_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/ppo_loc_swish_seed5_source_vx_recovery_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.011618`
- p95 abs error: `0.035149`
- max abs error: `0.257882`
- target-rate p95: `2.231686` rad/s
- target-rate max: `4.352456` rad/s

## Loss

| step | loss |
|---:|---:|
| 1 | 0.192612 |
| 500 | 0.000849 |
| 1000 | 0.000660 |
| 1500 | 0.000607 |
| 2000 | 0.000481 |
| 2500 | 0.000464 |
| 3000 | 0.000561 |
| 3500 | 0.000450 |
| 4000 | 0.000409 |
| 4500 | 0.000397 |
| 5000 | 0.000383 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000017`
- max abs error: `0.00000033`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
