# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0026_seed5_initial_support_live_oracle_iter0/live_oracle_dagger_aggregate_manifest.json`
- samples: `6123`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[128, 128]`
- context hidden sizes: `[32]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_z0026_seed5_initial_support_live_oracle_iter0_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_z0026_seed5_initial_support_live_oracle_iter0_student/candidate.onnx`

## Fit Metrics

- MAE: `0.007024`
- p95 abs error: `0.022539`
- max abs error: `0.389182`
- target-rate p95: `1.751672` rad/s
- target-rate max: `2.279135` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000041`
