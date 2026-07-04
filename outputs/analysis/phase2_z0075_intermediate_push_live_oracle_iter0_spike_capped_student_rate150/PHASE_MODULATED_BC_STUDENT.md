# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter0_spike_capped/live_oracle_dagger_spike_capped_aggregate_manifest.json`
- samples: `42501`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[128, 128]`
- context hidden sizes: `[32]`
- modulation scale: `0.5`

## Outputs

- NPZ: `policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter0_spike_capped_phase_modulated_rate150_20260704/student.npz`
- ONNX: `policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter0_spike_capped_phase_modulated_rate150_20260704/candidate.onnx`

## Fit Metrics

- MAE: `0.011763`
- p95 abs error: `0.037640`
- max abs error: `0.786255`
- target-rate p95: `1.306787` rad/s
- target-rate max: `2.179695` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000018`
