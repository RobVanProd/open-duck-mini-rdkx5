# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_health_routed_parent_seed5_w2p5_manifest.json`
- samples: `6000`
- weighted samples: `9685.0000`
- pairs: `5992`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_health_routed_parent_seed5_w2p5_ppo_loc_rate150_prior/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_health_routed_parent_seed5_w2p5_ppo_loc_rate150_prior/candidate.onnx`

## Fit Metrics

- MAE: `0.002130`
- p95 abs error: `0.006061`
- max abs error: `0.026270`
- target-rate p95: `1.378539` rad/s
- target-rate max: `1.564553` rad/s
- sample weight p50/p95/max: `1.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.115994 |
| 1000 | 0.000035 |
| 2000 | 0.000019 |
| 3000 | 0.000015 |
| 4000 | 0.000012 |
| 5000 | 0.000008 |
| 6000 | 0.000013 |
| 7000 | 0.000008 |
| 8000 | 0.000007 |
| 9000 | 0.000012 |
| 10000 | 0.000006 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000015`
- max abs error: `0.00000028`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
