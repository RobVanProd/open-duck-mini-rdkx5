# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_live_oracle_right_swing_iter1/live_oracle_dagger_aggregate_manifest.json`
- samples: `3250`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.75`

## Outputs

- NPZ: `outputs/analysis/phase2_live_oracle_right_swing_iter1_phasecmd_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_live_oracle_right_swing_iter1_phasecmd_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.006895`
- p95 abs error: `0.018921`
- max abs error: `0.403698`
- target-rate p95: `1.497695` rad/s
- target-rate max: `3.924863` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000018`
- max abs error: `0.00000036`
