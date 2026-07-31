# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0075_iter8_neighbor_stabilized_merged_manifest.json`
- samples: `54497`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `policy/candidates/phase2_z0075_neighbor_stabilized_rate150_20260704/student.npz`
- ONNX: `policy/candidates/phase2_z0075_neighbor_stabilized_rate150_20260704/candidate.onnx`

## Fit Metrics

- MAE: `0.014710`
- p95 abs error: `0.048543`
- max abs error: `0.813995`
- target-rate p95: `1.298335` rad/s
- target-rate max: `2.441719` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000013`
- max abs error: `0.00000030`
