# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/ppo_swish_command_conditioned_manifest.json`
- samples: `12342`
- pairs: `12310`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/ppo_loc_swish_command_conditioned_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/ppo_loc_swish_command_conditioned_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.010749`
- p95 abs error: `0.032331`
- max abs error: `0.306286`
- target-rate p95: `1.956745` rad/s
- target-rate max: `4.501909` rad/s

## Loss

| step | loss |
|---:|---:|
| 1 | 0.154841 |
| 500 | 0.000666 |
| 1000 | 0.000570 |
| 1500 | 0.000484 |
| 2000 | 0.000467 |
| 2500 | 0.000407 |
| 3000 | 0.000455 |
| 3500 | 0.000353 |
| 4000 | 0.000299 |
| 4500 | 0.000347 |
| 5000 | 0.000326 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000010`
- max abs error: `0.00000030`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
