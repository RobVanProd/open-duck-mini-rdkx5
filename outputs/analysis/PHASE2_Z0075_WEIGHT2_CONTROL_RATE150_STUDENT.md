# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0075_iter6_weight2_control_manifest.json`
- samples: `50253`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `policy/candidates/phase2_z0075_weight2_control_rate150_20260704/student.npz`
- ONNX: `policy/candidates/phase2_z0075_weight2_control_rate150_20260704/candidate.onnx`

## Fit Metrics

- MAE: `0.009053`
- p95 abs error: `0.030133`
- max abs error: `0.513354`
- target-rate p95: `1.366491` rad/s
- target-rate max: `2.448786` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000024`
