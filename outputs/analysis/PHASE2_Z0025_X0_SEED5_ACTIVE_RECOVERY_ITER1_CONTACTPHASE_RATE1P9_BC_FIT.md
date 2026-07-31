# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0025_x0_seed5_active_recovery_relabel_iter1/live_oracle_dagger_aggregate_manifest.json`
- samples: `10643`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[128, 64]`
- context hidden sizes: `[32]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_z0025_x0_seed5_active_recovery_iter1_contactphase_rate1p9_bc_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_z0025_x0_seed5_active_recovery_iter1_contactphase_rate1p9_bc_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.015846`
- p95 abs error: `0.048198`
- max abs error: `0.741823`
- target-rate p95: `1.577307` rad/s
- target-rate max: `2.066789` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000034`
