# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_seed5_neighbor_recovery_aggregate_manifest.json`
- samples: `3086`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.75`

## Outputs

- NPZ: `outputs/analysis/phase2_seed5_neighbor_recovery_contactphase_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_seed5_neighbor_recovery_contactphase_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.007853`
- p95 abs error: `0.023375`
- max abs error: `0.358819`
- target-rate p95: `1.444770` rad/s
- target-rate max: `3.978167` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000015`
- max abs error: `0.00000030`
