# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_transition_protected_seed4_weighted_manifest.json`
- samples: `500`
- weighted samples: `2747.0000`
- pairs: `498`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_transition_protected_seed4_weighted_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_transition_protected_seed4_weighted_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.007652`
- p95 abs error: `0.022310`
- max abs error: `0.272646`
- target-rate p95: `2.205765` rad/s
- target-rate max: `4.049849` rad/s
- sample weight p50/p95/max: `5.0000` / `15.0000` / `15.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.189190 |
| 500 | 0.000502 |
| 1000 | 0.000334 |
| 1500 | 0.000327 |
| 2000 | 0.000312 |
| 2500 | 0.000338 |
| 3000 | 0.000332 |
| 3500 | 0.000288 |
| 4000 | 0.000335 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000017`
- max abs error: `0.00000029`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
