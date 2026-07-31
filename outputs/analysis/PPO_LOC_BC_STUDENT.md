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

## Outputs

- NPZ: `outputs/analysis/ppo_loc_bc_student_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/ppo_loc_bc_student_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.014198`
- p95 abs error: `0.040378`
- max abs error: `0.284595`
- target-rate p95: `2.203947` rad/s
- target-rate max: `5.154907` rad/s

## Loss

| step | loss |
|---:|---:|
| 1 | 0.432344 |
| 500 | 0.001047 |
| 1000 | 0.000981 |
| 1500 | 0.000751 |
| 2000 | 0.000705 |
| 2500 | 0.000572 |
| 3000 | 0.000583 |
| 3500 | 0.000563 |
| 4000 | 0.000506 |
| 4500 | 0.000536 |
| 5000 | 0.000518 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000030`
- max abs error: `0.00000059`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
