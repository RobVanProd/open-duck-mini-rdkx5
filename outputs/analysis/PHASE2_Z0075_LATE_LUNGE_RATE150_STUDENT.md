# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0075_iter9_late_lunge_merged_manifest.json`
- samples: `52765`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `policy/candidates/phase2_z0075_late_lunge_rate150_20260704/student.npz`
- ONNX: `policy/candidates/phase2_z0075_late_lunge_rate150_20260704/candidate.onnx`

## Fit Metrics

- MAE: `0.010445`
- p95 abs error: `0.032991`
- max abs error: `0.884549`
- target-rate p95: `1.368537` rad/s
- target-rate max: `2.319002` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000030`
