# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_online_router_parent_pair_lateral_selected_manifest.json`
- samples: `3750`
- context indices: `[6, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]`
- trunk hidden sizes: `[768, 384, 192]`
- context hidden sizes: `[192, 192]`
- modulation scale: `0.75`

## Outputs

- NPZ: `outputs/analysis/phase2_parent_pair_lateral_rich_context_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_parent_pair_lateral_rich_context_student/candidate.onnx`

## Fit Metrics

- MAE: `0.002110`
- p95 abs error: `0.005281`
- max abs error: `0.026041`
- target-rate p95: `1.420386` rad/s
- target-rate max: `1.822195` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000027`
