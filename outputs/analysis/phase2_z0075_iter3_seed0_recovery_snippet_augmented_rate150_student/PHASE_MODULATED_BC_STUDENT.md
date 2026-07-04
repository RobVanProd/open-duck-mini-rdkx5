# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0075_iter3_seed0_recovery_snippet_augmented_weighted_manifest.json`
- samples: `51294`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `policy/candidates/phase2_z0075_iter3_seed0_recovery_snippet_augmented_rate150_20260704/student.npz`
- ONNX: `policy/candidates/phase2_z0075_iter3_seed0_recovery_snippet_augmented_rate150_20260704/candidate.onnx`

## Fit Metrics

- MAE: `0.009070`
- p95 abs error: `0.028178`
- max abs error: `0.670479`
- target-rate p95: `1.355027` rad/s
- target-rate max: `5.560378` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000024`
