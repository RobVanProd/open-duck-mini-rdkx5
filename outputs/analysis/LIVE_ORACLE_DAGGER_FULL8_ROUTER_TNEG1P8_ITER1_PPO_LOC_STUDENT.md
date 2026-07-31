# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/live_oracle_dagger_full8_router_tneg1p8/iter_001/live_oracle_dagger_aggregate_manifest.json`
- samples: `18836`
- weighted samples: `38022.0000`
- pairs: `18810`
- hidden sizes: `[512, 256]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/live_oracle_dagger_full8_router_tneg1p8_iter1_ppo_loc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/live_oracle_dagger_full8_router_tneg1p8_iter1_ppo_loc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.003753`
- p95 abs error: `0.011881`
- max abs error: `0.091833`
- target-rate p95: `1.308459` rad/s
- target-rate max: `2.117395` rad/s
- sample weight p50/p95/max: `1.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.185164 |
| 1000 | 0.000092 |
| 2000 | 0.000069 |
| 3000 | 0.000061 |
| 4000 | 0.000061 |
| 5000 | 0.000048 |
| 6000 | 0.000051 |
| 7000 | 0.000043 |
| 8000 | 0.000046 |
| 9000 | 0.000042 |
| 10000 | 0.000039 |
| 11000 | 0.000037 |
| 12000 | 0.000035 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000008`
- max abs error: `0.00000012`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
