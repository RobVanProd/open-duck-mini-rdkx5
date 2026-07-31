# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/source_vx_selector_trace_dagger3_manifest.json`
- samples: `9268`
- pairs: `9243`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/ppo_loc_swish_bc_student_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/ppo_loc_swish_bc_student_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.012030`
- p95 abs error: `0.035899`
- max abs error: `0.317852`
- target-rate p95: `2.228610` rad/s
- target-rate max: `4.498640` rad/s

## Loss

| step | loss |
|---:|---:|
| 1 | 0.191376 |
| 500 | 0.000768 |
| 1000 | 0.000666 |
| 1500 | 0.000587 |
| 2000 | 0.000568 |
| 2500 | 0.000442 |
| 3000 | 0.000493 |
| 3500 | 0.000412 |
| 4000 | 0.000396 |
| 4500 | 0.000396 |
| 5000 | 0.000407 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000018`
- max abs error: `0.00000040`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
