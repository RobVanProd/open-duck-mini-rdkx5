# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_manifest.json`
- samples: `10322`
- weighted samples: `10322.0000`
- pairs: `10302`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.006891`
- p95 abs error: `0.024189`
- max abs error: `0.202729`
- target-rate p95: `1.733526` rad/s
- target-rate max: `2.500935` rad/s
- sample weight p50/p95/max: `1.0000` / `1.0000` / `1.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.159281 |
| 500 | 0.000403 |
| 1000 | 0.000309 |
| 1500 | 0.000274 |
| 2000 | 0.000213 |
| 2500 | 0.000178 |
| 3000 | 0.000193 |
| 3500 | 0.000226 |
| 4000 | 0.000181 |
| 4500 | 0.000171 |
| 5000 | 0.000160 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000016`
- max abs error: `0.00000028`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
