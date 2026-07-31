# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_live_oracle_right_swing_iter1_selective_aggregate_manifest.json`
- samples: `2750`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.75`

## Outputs

- NPZ: `outputs/analysis/phase2_live_oracle_right_swing_iter1_selective_phasecmd_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_live_oracle_right_swing_iter1_selective_phasecmd_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.005507`
- p95 abs error: `0.015834`
- max abs error: `0.274426`
- target-rate p95: `1.497163` rad/s
- target-rate max: `4.232570` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000017`
- max abs error: `0.00000036`
