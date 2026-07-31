# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_health_routed_parent_live_compact_iter2/live_oracle_dagger_aggregate_manifest.json`
- samples: `8550`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_health_routed_parent_live_compact_iter2_phase_modulated/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_health_routed_parent_live_compact_iter2_phase_modulated/candidate.onnx`

## Fit Metrics

- MAE: `0.006018`
- p95 abs error: `0.016397`
- max abs error: `0.155846`
- target-rate p95: `1.383206` rad/s
- target-rate max: `2.054419` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000024`
