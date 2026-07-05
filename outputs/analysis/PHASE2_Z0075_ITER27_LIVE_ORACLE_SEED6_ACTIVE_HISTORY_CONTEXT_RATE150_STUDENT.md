# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_027_history_context_resetsettle10_seed6_active/live_oracle_dagger_aggregate_manifest.json`
- samples: `71969`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[128, 128]`
- context hidden sizes: `[32, 32]`
- modulation scale: `0.15`

## Outputs

- NPZ: `policy/candidates/phase2_z0075_iter27_live_oracle_seed6_active_history_context_rate150_20260705/student.npz`
- ONNX: `policy/candidates/phase2_z0075_iter27_live_oracle_seed6_active_history_context_rate150_20260705/candidate.onnx`

## Fit Metrics

- MAE: `0.009598`
- p95 abs error: `0.031434`
- max abs error: `0.506875`
- target-rate p95: `1.362844` rad/s
- target-rate max: `7.131151` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000018`
