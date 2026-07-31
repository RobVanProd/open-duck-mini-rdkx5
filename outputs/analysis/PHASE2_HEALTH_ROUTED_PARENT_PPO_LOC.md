# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_health_routed_parent_manifest.json`
- samples: `3750`
- weighted samples: `3750.0000`
- pairs: `3745`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_health_routed_parent_ppo_loc/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_health_routed_parent_ppo_loc/candidate.onnx`

## Fit Metrics

- MAE: `0.002642`
- p95 abs error: `0.006637`
- max abs error: `0.025348`
- target-rate p95: `1.430866` rad/s
- target-rate max: `1.826638` rad/s
- sample weight p50/p95/max: `1.0000` / `1.0000` / `1.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.176929 |
| 500 | 0.000075 |
| 1000 | 0.000041 |
| 1500 | 0.000027 |
| 2000 | 0.000023 |
| 2500 | 0.000026 |
| 3000 | 0.000018 |
| 3500 | 0.000018 |
| 4000 | 0.000019 |
| 4500 | 0.000014 |
| 5000 | 0.000011 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000016`
- max abs error: `0.00000031`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
