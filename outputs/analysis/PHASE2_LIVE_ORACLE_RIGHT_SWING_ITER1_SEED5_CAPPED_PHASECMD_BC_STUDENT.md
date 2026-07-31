# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_live_oracle_right_swing_iter1_seed5_capped_aggregate_manifest.json`
- samples: `3000`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.75`

## Outputs

- NPZ: `outputs/analysis/phase2_live_oracle_right_swing_iter1_seed5_capped_phasecmd_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_live_oracle_right_swing_iter1_seed5_capped_phasecmd_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.006694`
- p95 abs error: `0.018419`
- max abs error: `0.344159`
- target-rate p95: `1.455453` rad/s
- target-rate max: `4.006499` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000018`
- max abs error: `0.00000030`
