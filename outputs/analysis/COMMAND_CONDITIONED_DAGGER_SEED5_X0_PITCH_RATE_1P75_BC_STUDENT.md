# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/command_conditioned_dagger_seed5_x0_pitch_rate_1p75_manifest.json`
- samples: `8072`
- weighted samples: `8072.0000`
- pairs: `8055`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.006966`
- p95 abs error: `0.024948`
- max abs error: `0.199382`
- target-rate p95: `1.643471` rad/s
- target-rate max: `2.516868` rad/s
- sample weight p50/p95/max: `1.0000` / `1.0000` / `1.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.152445 |
| 500 | 0.000357 |
| 1000 | 0.000292 |
| 1500 | 0.000255 |
| 2000 | 0.000238 |
| 2500 | 0.000174 |
| 3000 | 0.000212 |
| 3500 | 0.000182 |
| 4000 | 0.000204 |
| 4500 | 0.000145 |
| 5000 | 0.000173 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000014`
- max abs error: `0.00000025`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
