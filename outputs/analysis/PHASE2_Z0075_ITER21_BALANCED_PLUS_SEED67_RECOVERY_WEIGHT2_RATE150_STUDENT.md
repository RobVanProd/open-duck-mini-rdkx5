# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0075_iter21_balanced_plus_seed67_recovery_weight2_merged_manifest.json`
- samples: `53706`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_z0075_iter21_balanced_plus_seed67_recovery_weight2_rate150_student/candidate_mlp.npz`
- ONNX: `policy/candidates/phase2_z0075_iter21_balanced_plus_seed67_recovery_weight2_rate150_20260704/candidate.onnx`

## Fit Metrics

- MAE: `0.013093`
- p95 abs error: `0.038015`
- max abs error: `0.803865`
- target-rate p95: `1.348443` rad/s
- target-rate max: `11.809631` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000019`
- max abs error: `0.00000037`
