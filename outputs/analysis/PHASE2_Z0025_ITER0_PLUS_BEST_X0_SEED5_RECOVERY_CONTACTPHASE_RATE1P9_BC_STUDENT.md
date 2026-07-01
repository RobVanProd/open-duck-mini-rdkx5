# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0025_iter0_plus_best_x0_seed5_recovery_manifest.json`
- samples: `11250`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.75`

## Outputs

- NPZ: `outputs/analysis/phase2_z0025_iter0_plus_best_x0_seed5_recovery_contactphase_rate1p9_bc_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_z0025_iter0_plus_best_x0_seed5_recovery_contactphase_rate1p9_bc_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.008163`
- p95 abs error: `0.026618`
- max abs error: `0.706229`
- target-rate p95: `1.628798` rad/s
- target-rate max: `1.979118` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000018`
- max abs error: `0.00000036`
