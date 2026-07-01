# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z005_seed5_recovery_enhanced_source_manifest.json`
- samples: `7556`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_z005_seed5_recovery_enhanced_phase_mod_bc_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_z005_seed5_recovery_enhanced_phase_mod_bc_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.005185`
- p95 abs error: `0.015453`
- max abs error: `0.377182`
- target-rate p95: `1.727071` rad/s
- target-rate max: `3.305939` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000027`
