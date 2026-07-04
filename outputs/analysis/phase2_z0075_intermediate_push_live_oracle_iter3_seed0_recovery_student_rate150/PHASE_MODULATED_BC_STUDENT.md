# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_aggregate_manifest.json`
- samples: `51175`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_rate150_20260704/student.npz`
- ONNX: `policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_rate150_20260704/candidate.onnx`

## Fit Metrics

- MAE: `0.009558`
- p95 abs error: `0.028781`
- max abs error: `0.403406`
- target-rate p95: `1.369416` rad/s
- target-rate max: `4.487093` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000024`
