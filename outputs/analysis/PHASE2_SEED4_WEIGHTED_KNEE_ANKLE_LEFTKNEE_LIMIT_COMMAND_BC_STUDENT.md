# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_seed4_weighted_knee_ankle_leftknee_limit_command_weighted_manifest.json`
- samples: `750`
- weighted samples: `4444.0000`
- pairs: `747`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_seed4_weighted_knee_ankle_leftknee_limit_command_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_seed4_weighted_knee_ankle_leftknee_limit_command_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.003264`
- p95 abs error: `0.010397`
- max abs error: `0.060935`
- target-rate p95: `1.701605` rad/s
- target-rate max: `2.395611` rad/s
- sample weight p50/p95/max: `1.0000` / `20.0000` / `20.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.038749 |
| 500 | 0.000050 |
| 1000 | 0.000014 |
| 1500 | 0.000010 |
| 2000 | 0.000012 |
| 2500 | 0.000006 |
| 3000 | 0.000010 |
| 3500 | 0.000010 |
| 4000 | 0.000004 |
| 4500 | 0.000010 |
| 5000 | 0.000004 |
| 5500 | 0.000003 |
| 6000 | 0.000005 |
| 6500 | 0.000004 |
| 7000 | 0.000006 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000019`
- max abs error: `0.00000033`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
