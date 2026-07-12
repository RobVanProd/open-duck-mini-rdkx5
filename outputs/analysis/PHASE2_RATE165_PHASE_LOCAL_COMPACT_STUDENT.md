# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter1_run/live_oracle_dagger_aggregate_manifest.json`
- samples: `21000`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_rate165_phase_local_compact_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_rate165_phase_local_compact_student/candidate.onnx`

## Fit Metrics

- MAE: `0.014994`
- p95 abs error: `0.044799`
- max abs error: `0.995813`
- target-rate p95: `1.290893` rad/s
- target-rate max: `2.162907` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000015`
- max abs error: `0.00000035`
