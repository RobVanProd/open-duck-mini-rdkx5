# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/live_oracle_dagger_aggregate_manifest.json`
- samples: `6117`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[128, 64]`
- context hidden sizes: `[32]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short_student/candidate.onnx`

## Fit Metrics

- MAE: `0.006736`
- p95 abs error: `0.019630`
- max abs error: `0.335301`
- target-rate p95: `1.816270` rad/s
- target-rate max: `2.788720` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000030`
