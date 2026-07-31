# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2/live_oracle_dagger_aggregate_manifest.json`
- samples: `11555`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[512, 256, 128]`
- context hidden sizes: `[64, 64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_phase_contact_modulated_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_phase_contact_modulated_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.002776`
- p95 abs error: `0.009653`
- max abs error: `0.167928`
- target-rate p95: `1.232130` rad/s
- target-rate max: `2.352783` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000002`
- max abs error: `0.00000006`
