# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/live_oracle_dagger_phase_student/z0025_x0_seed5_softzero_iter2_run/live_oracle_dagger_aggregate_manifest.json`
- samples: `12043`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_z0025_live_oracle_seed5_softzero_iter2_contactphase_rate1p9_bc_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_z0025_live_oracle_seed5_softzero_iter2_contactphase_rate1p9_bc_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.008747`
- p95 abs error: `0.028583`
- max abs error: `0.473628`
- target-rate p95: `1.746516` rad/s
- target-rate max: `2.001389` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000013`
- max abs error: `0.00000030`
