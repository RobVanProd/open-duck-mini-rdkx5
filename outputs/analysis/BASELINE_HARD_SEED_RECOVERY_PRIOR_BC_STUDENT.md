# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/baseline_step0_hard_seed_positive_trace_manifest.json`
- samples: `2250`
- pairs: `2247`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/baseline_hard_seed_recovery_prior_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/baseline_hard_seed_recovery_prior_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.005497`
- p95 abs error: `0.014711`
- max abs error: `0.053143`
- target-rate p95: `1.716564` rad/s
- target-rate max: `2.708561` rad/s

## Loss

| step | loss |
|---:|---:|
| 1 | 0.209799 |
| 500 | 0.000314 |
| 1000 | 0.000183 |
| 1500 | 0.000118 |
| 2000 | 0.000103 |
| 2500 | 0.000069 |
| 3000 | 0.000058 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000018`
- max abs error: `0.00000032`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
