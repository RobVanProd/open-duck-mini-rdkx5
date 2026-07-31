# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_000/live_oracle_dagger_x008_manifest.json`
- samples: `6000`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/live_oracle_phase_modulated_iter0_x008_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/live_oracle_phase_modulated_iter0_x008_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.010803`
- p95 abs error: `0.032824`
- max abs error: `0.190804`
- target-rate p95: `2.228043` rad/s
- target-rate max: `3.990272` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000027`
