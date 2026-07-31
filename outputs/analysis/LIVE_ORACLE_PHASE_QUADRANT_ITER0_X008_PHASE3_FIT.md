# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/live_oracle_phase_quadrant_iter0_x008_split/phase_bin_3/manifest.json`
- samples: `1296`
- weighted samples: `3921.0000`
- pairs: `1295`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/live_oracle_phase_quadrant_iter0_x008_phase3_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/live_oracle_phase_quadrant_iter0_x008_phase3_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.006822`
- p95 abs error: `0.018928`
- max abs error: `0.131117`
- target-rate p95: `4.173622` rad/s
- target-rate max: `15.238923` rad/s
- sample weight p50/p95/max: `3.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.184051 |
| 500 | 0.000323 |
| 1000 | 0.000240 |
| 1500 | 0.000233 |
| 2000 | 0.000191 |
| 2500 | 0.000159 |
| 3000 | 0.000155 |
| 3500 | 0.000139 |
| 4000 | 0.000116 |
| 4500 | 0.000113 |
| 5000 | 0.000086 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000017`
- max abs error: `0.00000034`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
