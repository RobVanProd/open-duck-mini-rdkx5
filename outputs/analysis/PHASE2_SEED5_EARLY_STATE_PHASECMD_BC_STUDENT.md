# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_seed5_early_state_weighted_aggregate_manifest.json`
- samples: `3043`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.75`

## Outputs

- NPZ: `outputs/analysis/phase2_seed5_early_state_phasecmd_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_seed5_early_state_phasecmd_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.006533`
- p95 abs error: `0.019863`
- max abs error: `0.299842`
- target-rate p95: `1.460243` rad/s
- target-rate max: `4.136330` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000015`
- max abs error: `0.00000030`
