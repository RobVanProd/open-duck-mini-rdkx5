# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0075_iter21_balanced_seed67_weight2_plus_seed1_merged_manifest.json`
- samples: `53750`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_z0075_iter21_balanced_seed67_weight2_plus_seed1_rate150_student/candidate_mlp.npz`
- ONNX: `policy/candidates/phase2_z0075_iter21_balanced_seed67_weight2_plus_seed1_rate150_20260704/candidate.onnx`

## Fit Metrics

- MAE: `0.011351`
- p95 abs error: `0.034742`
- max abs error: `0.607201`
- target-rate p95: `1.353386` rad/s
- target-rate max: `10.719099` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000018`
- max abs error: `0.00000030`
