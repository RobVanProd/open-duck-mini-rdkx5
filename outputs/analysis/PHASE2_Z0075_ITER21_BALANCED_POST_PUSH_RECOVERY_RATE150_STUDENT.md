# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0075_iter21_balanced_post_push_recovery_merged_manifest.json`
- samples: `53559`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_z0075_iter21_balanced_post_push_recovery_rate150_student/candidate_mlp.npz`
- ONNX: `policy/candidates/phase2_z0075_iter21_balanced_post_push_recovery_rate150_20260704/candidate.onnx`

## Fit Metrics

- MAE: `0.012026`
- p95 abs error: `0.034633`
- max abs error: `0.511629`
- target-rate p95: `1.375063` rad/s
- target-rate max: `9.350019` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000018`
- max abs error: `0.00000036`
