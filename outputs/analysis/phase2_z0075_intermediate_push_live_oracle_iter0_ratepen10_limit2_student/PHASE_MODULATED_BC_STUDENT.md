# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter0_curated/live_oracle_dagger_curated_aggregate_manifest.json`
- samples: `42501`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[128, 128]`
- context hidden sizes: `[32]`
- modulation scale: `0.5`

## Outputs

- NPZ: `policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter0_ratepen10_limit2_phase_modulated_20260704/student.npz`
- ONNX: `policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter0_ratepen10_limit2_phase_modulated_20260704/candidate.onnx`

## Fit Metrics

- MAE: `0.020880`
- p95 abs error: `0.059004`
- max abs error: `1.691553`
- target-rate p95: `1.344511` rad/s
- target-rate max: `3.386143` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000025`
