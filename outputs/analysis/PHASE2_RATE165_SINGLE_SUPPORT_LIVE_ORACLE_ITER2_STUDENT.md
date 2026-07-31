# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_plan/live_oracle_dagger_aggregate_manifest.json`
- samples: `28500`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_rate165_single_support_live_oracle_iter2_student/candidate.onnx`

## Fit Metrics

- MAE: `0.007755`
- p95 abs error: `0.021781`
- max abs error: `0.312893`
- target-rate p95: `1.425471` rad/s
- target-rate max: `1.893847` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000013`
- max abs error: `0.00000027`
