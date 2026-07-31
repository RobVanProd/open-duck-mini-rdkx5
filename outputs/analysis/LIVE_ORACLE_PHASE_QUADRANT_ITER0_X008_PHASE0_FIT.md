# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/live_oracle_phase_quadrant_iter0_x008_split/phase_bin_0/manifest.json`
- samples: `1568`
- weighted samples: `4956.0000`
- pairs: `1567`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/live_oracle_phase_quadrant_iter0_x008_phase0_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/live_oracle_phase_quadrant_iter0_x008_phase0_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.007918`
- p95 abs error: `0.023037`
- max abs error: `0.129506`
- target-rate p95: `4.059961` rad/s
- target-rate max: `13.783243` rad/s
- sample weight p50/p95/max: `3.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.191789 |
| 500 | 0.000378 |
| 1000 | 0.000278 |
| 1500 | 0.000254 |
| 2000 | 0.000231 |
| 2500 | 0.000204 |
| 3000 | 0.000171 |
| 3500 | 0.000189 |
| 4000 | 0.000156 |
| 4500 | 0.000123 |
| 5000 | 0.000144 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000017`
- max abs error: `0.00000034`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
