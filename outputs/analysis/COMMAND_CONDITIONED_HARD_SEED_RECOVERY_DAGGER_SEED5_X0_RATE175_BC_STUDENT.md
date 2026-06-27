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

- NPZ: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.010691`
- p95 abs error: `0.040171`
- max abs error: `0.244990`
- target-rate p95: `1.573163` rad/s
- target-rate max: `1.997019` rad/s
- sample weight p50/p95/max: `1.0000` / `1.0000` / `1.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.174562 |
| 500 | 0.000690 |
| 1000 | 0.000556 |
| 1500 | 0.000486 |
| 2000 | 0.000455 |
| 2500 | 0.000427 |
| 3000 | 0.000436 |
| 3500 | 0.000513 |
| 4000 | 0.000433 |
| 4500 | 0.000425 |
| 5000 | 0.000423 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000015`
- max abs error: `0.00000029`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
