# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_health_routed_pass_parent_aggregate_manifest.json`
- samples: `5250`
- weighted samples: `7810.0000`
- pairs: `5243`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_health_routed_pass_parent_ppo_loc_rate150_prior/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_health_routed_pass_parent_ppo_loc_rate150_prior/candidate.onnx`

## Fit Metrics

- MAE: `0.001967`
- p95 abs error: `0.005765`
- max abs error: `0.024172`
- target-rate p95: `1.368890` rad/s
- target-rate max: `1.589359` rad/s
- sample weight p50/p95/max: `1.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.103985 |
| 1000 | 0.000029 |
| 2000 | 0.000017 |
| 3000 | 0.000014 |
| 4000 | 0.000011 |
| 5000 | 0.000008 |
| 6000 | 0.000012 |
| 7000 | 0.000009 |
| 8000 | 0.000009 |
| 9000 | 0.000006 |
| 10000 | 0.000005 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000014`
- max abs error: `0.00000028`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
