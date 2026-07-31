# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_iter2_right_ankle_limit198_manifest.json`
- samples: `28500`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_iter2_right_ankle_limit198_rate165_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_iter2_right_ankle_limit198_rate165_student/candidate.onnx`

## Fit Metrics

- MAE: `0.007362`
- p95 abs error: `0.020872`
- max abs error: `0.308668`
- target-rate p95: `1.431168` rad/s
- target-rate max: `1.946180` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000021`
