# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_full8_router_tneg1p8_bc_trace_manifest_seed56_weighted.json`
- samples: `12000`
- weighted samples: `16500.0000`
- pairs: `11984`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_full8_router_tneg1p8_ppo_loc_bc_seed56_weighted_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_full8_router_tneg1p8_ppo_loc_bc_seed56_weighted_student/candidate.onnx`

## Fit Metrics

- MAE: `0.001505`
- p95 abs error: `0.004912`
- max abs error: `0.029114`
- target-rate p95: `1.258051` rad/s
- target-rate max: `1.864973` rad/s
- sample weight p50/p95/max: `1.0000` / `4.0000` / `4.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.153669 |
| 1000 | 0.000039 |
| 2000 | 0.000020 |
| 3000 | 0.000014 |
| 4000 | 0.000012 |
| 5000 | 0.000011 |
| 6000 | 0.000010 |
| 7000 | 0.000008 |
| 8000 | 0.000009 |
| 9000 | 0.000006 |
| 10000 | 0.000006 |
| 11000 | 0.000007 |
| 12000 | 0.000006 |
| 13000 | 0.000005 |
| 14000 | 0.000004 |
| 15000 | 0.000005 |
| 16000 | 0.000005 |
| 17000 | 0.000005 |
| 18000 | 0.000005 |
| 19000 | 0.000005 |
| 20000 | 0.000005 |
| 21000 | 0.000004 |
| 22000 | 0.000004 |
| 23000 | 0.000004 |
| 24000 | 0.000004 |
| 25000 | 0.000006 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000006`
- max abs error: `0.00000011`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
