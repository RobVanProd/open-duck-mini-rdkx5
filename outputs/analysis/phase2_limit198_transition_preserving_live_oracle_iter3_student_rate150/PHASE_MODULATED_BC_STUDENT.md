# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json`
- samples: `40500`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[128, 128]`
- context hidden sizes: `[32]`
- modulation scale: `0.5`

## Outputs

- NPZ: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/student.npz`
- ONNX: `policy/candidates/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_20260703/candidate.onnx`

## Fit Metrics

- MAE: `0.008739`
- p95 abs error: `0.028857`
- max abs error: `0.316246`
- target-rate p95: `1.364055` rad/s
- target-rate max: `1.569699` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000021`
