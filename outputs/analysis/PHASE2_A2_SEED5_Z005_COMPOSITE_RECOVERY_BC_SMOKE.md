# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_a2_seed5_z005_composite_recovery_bc_manifest.json`
- samples: `141`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[128, 64]`
- context hidden sizes: `[32]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_a2_seed5_z005_composite_recovery_bc_smoke_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_a2_seed5_z005_composite_recovery_bc_smoke_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.002018`
- p95 abs error: `0.005435`
- max abs error: `0.015053`
- target-rate p95: `0.738701` rad/s
- target-rate max: `1.869311` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000028`
