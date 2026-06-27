# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/ppo_swish_cmd_conditioned_pitch_ratelimit_2p25_manifest.json`
- samples: `8000`
- pairs: `7984`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/ppo_loc_swish_cmd_pitch_rl_2p25_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/ppo_loc_swish_cmd_pitch_rl_2p25_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.006876`
- p95 abs error: `0.024947`
- max abs error: `0.215340`
- target-rate p95: `1.784699` rad/s
- target-rate max: `2.497077` rad/s

## Loss

| step | loss |
|---:|---:|
| 1 | 0.141597 |
| 500 | 0.000378 |
| 1000 | 0.000316 |
| 1500 | 0.000254 |
| 2000 | 0.000268 |
| 2500 | 0.000277 |
| 3000 | 0.000211 |
| 3500 | 0.000239 |
| 4000 | 0.000200 |
| 4500 | 0.000162 |
| 5000 | 0.000160 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000014`
- max abs error: `0.00000029`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
