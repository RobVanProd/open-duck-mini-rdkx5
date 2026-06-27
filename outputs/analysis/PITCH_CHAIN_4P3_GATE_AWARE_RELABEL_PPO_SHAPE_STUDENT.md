# PPO-Loc BC Student

status: `PASS_PPO_LOC_BC_FIT_SMOKE`

This is an offline behavior-cloning fit using the PPO actor's deterministic
`tanh(loc)` contract. It did not train PPO, deploy, SSH, run robot tests,
or change robot runtime behavior.

## Inputs

- manifest: `outputs/analysis/pitch_chain_4p3_gate_aware_relabel_weighted_manifest.json`
- samples: `5000`
- weighted samples: `16000.0000`
- pairs: `4990`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`

## Outputs

- NPZ: `outputs/analysis/pitch_chain_4p3_gate_aware_relabel_ppo_shape_student_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/pitch_chain_4p3_gate_aware_relabel_ppo_shape_student_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.015000`
- p95 abs error: `0.047586`
- max abs error: `0.252386`
- target-rate p95: `2.326586` rad/s
- target-rate max: `4.566728` rad/s
- sample weight p50/p95/max: `1.0000` / `12.0000` / `12.0000`

## Loss

| step | loss |
|---:|---:|
| 1 | 0.220500 |
| 500 | 0.001039 |
| 1000 | 0.000752 |
| 1500 | 0.000758 |
| 2000 | 0.000749 |
| 2500 | 0.000657 |
| 3000 | 0.000603 |
| 3500 | 0.000589 |
| 4000 | 0.000516 |
| 4500 | 0.000448 |
| 5000 | 0.000466 |

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000017`
- max abs error: `0.00000029`

## Gate

This only verifies a PPO-compatible supervised fit. The next gate is the
standard task-matched fitted closed-loop candidate sweep using the exported
ONNX, followed by actual PPO-param step-0 fidelity if the ONNX behavior is
worth promoting.
