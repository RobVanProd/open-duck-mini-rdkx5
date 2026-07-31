# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/live_oracle_phase_quadrant_iter0_x008_split/phase_bin_1/manifest.json`
- samples: `1568`
- weighted samples: `4079.0000`
- pairs: `1567`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/live_oracle_phase_quadrant_iter0_x008_phase1_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/live_oracle_phase_quadrant_iter0_x008_phase1_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.007380`
- p95 abs error: `0.021736`
- max abs error: `0.159838`
- target-rate p95: `4.078670` rad/s
- target-rate max: `13.937644` rad/s
- sample weight p50/p95/max: `2.0000` / `5.0000` / `5.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.186046 |
| 500 | 0.000269 |
| 1000 | 0.000227 |
| 1500 | 0.000196 |
| 2000 | 0.000172 |
| 2500 | 0.000153 |
| 3000 | 0.000137 |
| 3500 | 0.000150 |
| 4000 | 0.000106 |
| 4500 | 0.000105 |
| 5000 | 0.000091 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000018`
- max abs error: `0.00000039`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
