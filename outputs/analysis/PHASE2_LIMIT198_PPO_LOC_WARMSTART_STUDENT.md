# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_iter2_right_ankle_limit198_manifest.json`
- samples: `28500`
- weighted samples: `84460.0000`
- pairs: `28462`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_limit198_ppo_loc_warmstart_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_limit198_ppo_loc_warmstart_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.006760`
- p95 abs error: `0.019078`
- max abs error: `0.294988`
- target-rate p95: `1.422011` rad/s
- target-rate max: `2.306970` rad/s
- sample weight p50/p95/max: `3.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.152133 |
| 500 | 0.000434 |
| 1000 | 0.000309 |
| 1500 | 0.000297 |
| 2000 | 0.000356 |
| 2500 | 0.000179 |
| 3000 | 0.000142 |
| 3500 | 0.000326 |
| 4000 | 0.000198 |
| 4500 | 0.000179 |
| 5000 | 0.000174 |
| 5500 | 0.000115 |
| 6000 | 0.000231 |
| 6500 | 0.000254 |
| 7000 | 0.000148 |
| 7500 | 0.000215 |
| 8000 | 0.000153 |
| 8500 | 0.000099 |
| 9000 | 0.000148 |
| 9500 | 0.000147 |
| 10000 | 0.000153 |
| 10500 | 0.000184 |
| 11000 | 0.000176 |
| 11500 | 0.000086 |
| 12000 | 0.000088 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000019`
- max abs error: `0.00000031`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
