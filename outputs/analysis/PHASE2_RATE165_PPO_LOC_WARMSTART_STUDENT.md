# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_rate165_ppo_loc_warmstart_manifest.json`
- samples: `12000`
- weighted samples: `12000.0000`
- pairs: `11984`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_rate165_ppo_loc_warmstart_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_rate165_ppo_loc_warmstart_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.001119`
- p95 abs error: `0.003386`
- max abs error: `0.028045`
- target-rate p95: `1.234259` rad/s
- target-rate max: `1.680458` rad/s
- sample weight p50/p95/max: `1.0000` / `1.0000` / `1.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.128081 |
| 500 | 0.000046 |
| 1000 | 0.000020 |
| 1500 | 0.000015 |
| 2000 | 0.000011 |
| 2500 | 0.000008 |
| 3000 | 0.000007 |
| 3500 | 0.000007 |
| 4000 | 0.000005 |
| 4500 | 0.000006 |
| 5000 | 0.000017 |
| 5500 | 0.000005 |
| 6000 | 0.000004 |
| 6500 | 0.000006 |
| 7000 | 0.000003 |
| 7500 | 0.000003 |
| 8000 | 0.000003 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000017`
- max abs error: `0.00000029`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
