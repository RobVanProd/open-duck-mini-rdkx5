# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/gate_aware_rollout_correction_merged_manifest.json`
- samples: `5000`
- weighted samples: `7688.0000`
- pairs: `4990`
- hidden sizes: `[128, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/gate_aware_rollout_correction_student_smoke/candidate_mlp.npz`
- ONNX: `outputs/analysis/gate_aware_rollout_correction_student_smoke/candidate.onnx`

## Fit Metrics

- MAE: `0.033490`
- p95 abs error: `0.096491`
- max abs error: `0.758375`
- target-rate p95: `2.225281` rad/s
- target-rate max: `5.830774` rad/s
- sample weight p50/p95/max: `1.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.253288 |
| 200 | 0.002696 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000019`
- max abs error: `0.00000088`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
