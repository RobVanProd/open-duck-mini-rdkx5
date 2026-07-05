# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/phase2_command_gated_zero0020_with_seed5_rate160_antilunge_manifest.json`
- samples: `7524`
- weighted samples: `7644.0000`
- pairs: `7513`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/phase2_command_gated_zero0020_seed5_rate160_antilunge_ppo_loc_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_command_gated_zero0020_seed5_rate160_antilunge_ppo_loc_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.002257`
- p95 abs error: `0.007259`
- max abs error: `0.399780`
- target-rate p95: `1.263753` rad/s
- target-rate max: `2.860975` rad/s
- sample weight p50/p95/max: `1.0000` / `1.0000` / `6.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.111526 |
| 500 | 0.000162 |
| 1000 | 0.000084 |
| 1500 | 0.000183 |
| 2000 | 0.000031 |
| 2500 | 0.000073 |
| 3000 | 0.000114 |
| 3500 | 0.000065 |
| 4000 | 0.000118 |
| 4500 | 0.000148 |
| 5000 | 0.000028 |
| 5500 | 0.000024 |
| 6000 | 0.000051 |
| 6500 | 0.000053 |
| 7000 | 0.000037 |
| 7500 | 0.000015 |
| 8000 | 0.000018 |
| 8500 | 0.000021 |
| 9000 | 0.000038 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000007`
- max abs error: `0.00000014`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
