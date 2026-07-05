# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_full8_router_tneg1p8_bc_trace_manifest.json`
- samples: `12000`
- weighted samples: `12000.0000`
- pairs: `11984`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_full8_router_tneg1p8_ppo_loc_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_full8_router_tneg1p8_ppo_loc_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.001233`
- p95 abs error: `0.004127`
- max abs error: `0.024370`
- target-rate p95: `1.265294` rad/s
- target-rate max: `1.888090` rad/s
- sample weight p50/p95/max: `1.0000` / `1.0000` / `1.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.111208 |
| 1000 | 0.000031 |
| 2000 | 0.000017 |
| 3000 | 0.000013 |
| 4000 | 0.000014 |
| 5000 | 0.000010 |
| 6000 | 0.000008 |
| 7000 | 0.000007 |
| 8000 | 0.000007 |
| 9000 | 0.000006 |
| 10000 | 0.000006 |
| 11000 | 0.000005 |
| 12000 | 0.000006 |
| 13000 | 0.000005 |
| 14000 | 0.000004 |
| 15000 | 0.000006 |
| 16000 | 0.000004 |
| 17000 | 0.000004 |
| 18000 | 0.000004 |
| 19000 | 0.000004 |
| 20000 | 0.000003 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000005`
- max abs error: `0.00000007`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
