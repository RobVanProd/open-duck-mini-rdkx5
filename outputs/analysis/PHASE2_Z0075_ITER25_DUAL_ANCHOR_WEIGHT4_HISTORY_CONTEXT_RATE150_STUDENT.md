# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0075_iter25_dual_anchor_weight4_aggregate_manifest.json`
- samples: `68719`
- context indices: `[6, 7, 8, 9, 10, 11, 12, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[256, 128]`
- modulation scale: `0.75`

## Outputs

- NPZ: `policy/candidates/phase2_z0075_iter25_dual_anchor_weight4_history_context_rate150_20260704/candidate_mlp.npz`
- ONNX: `policy/candidates/phase2_z0075_iter25_dual_anchor_weight4_history_context_rate150_20260704/candidate.onnx`

## Fit Metrics

- MAE: `0.009110`
- p95 abs error: `0.030871`
- max abs error: `0.561910`
- target-rate p95: `1.361899` rad/s
- target-rate max: `9.124381` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000021`
