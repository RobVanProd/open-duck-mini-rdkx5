# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0075_iter14_gain095_seed0_pass_merged_manifest.json`
- samples: `53849`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_z0075_iter14_gain095_seed0_pass_rate150_candidate/candidate_mlp.npz`
- ONNX: `policy/candidates/phase2_z0075_iter14_gain095_seed0_pass_rate150_20260704/candidate.onnx`

## Fit Metrics

- MAE: `0.010193`
- p95 abs error: `0.032136`
- max abs error: `0.502740`
- target-rate p95: `1.364286` rad/s
- target-rate max: `3.595845` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000024`
