# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter1_x0seed5/live_oracle_dagger_aggregate_manifest.json`
- samples: `12043`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.75`

## Outputs

- NPZ: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter1_x0seed5_contactphase_rate1p9_bc_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter1_x0seed5_contactphase_rate1p9_bc_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.010209`
- p95 abs error: `0.031287`
- max abs error: `0.841390`
- target-rate p95: `1.623082` rad/s
- target-rate max: `2.956879` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000030`
