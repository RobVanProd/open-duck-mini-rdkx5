# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json`
- samples: `4000`
- weighted samples: `4000.0000`
- pairs: `3992`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/pitch_chain_4p3_ppo_shape_rate_student_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/pitch_chain_4p3_ppo_shape_rate_student_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.010959`
- p95 abs error: `0.035272`
- max abs error: `0.219779`
- target-rate p95: `2.296857` rad/s
- target-rate max: `4.171165` rad/s
- sample weight p50/p95/max: `1.0000` / `1.0000` / `1.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.190420 |
| 500 | 0.000752 |
| 1000 | 0.000599 |
| 1500 | 0.000488 |
| 2000 | 0.000469 |
| 2500 | 0.000446 |
| 3000 | 0.000429 |
| 3500 | 0.000385 |
| 4000 | 0.000401 |
| 4500 | 0.000331 |
| 5000 | 0.000321 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000017`
- max abs error: `0.00000036`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
