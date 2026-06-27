# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/command_conditioned_hard_seed_recovery_manifest.json`
- samples: `10250`
- pairs: `10231`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/command_conditioned_hard_seed_recovery_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/command_conditioned_hard_seed_recovery_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.007639`
- p95 abs error: `0.024773`
- max abs error: `0.209880`
- target-rate p95: `1.736061` rad/s
- target-rate max: `2.759758` rad/s

## Loss

| step | loss |
|---:|---:|
| 1 | 0.166434 |
| 500 | 0.000405 |
| 1000 | 0.000308 |
| 1500 | 0.000265 |
| 2000 | 0.000235 |
| 2500 | 0.000213 |
| 3000 | 0.000171 |
| 3500 | 0.000170 |
| 4000 | 0.000173 |
| 4500 | 0.000160 |
| 5000 | 0.000165 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000016`
- max abs error: `0.00000033`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
