# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z00245_support_recovery_dagger_iter1_soft_alpha035/live_oracle_dagger_aggregate_manifest.json`
- samples: `6118`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[128, 64]`
- context hidden sizes: `[32]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_z00245_support_recovery_dagger_iter1_soft_alpha035_contactphase_rate1p5_bc_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_z00245_support_recovery_dagger_iter1_soft_alpha035_contactphase_rate1p5_bc_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.032898`
- p95 abs error: `0.101650`
- max abs error: `0.830888`
- target-rate p95: `1.318220` rad/s
- target-rate max: `1.735654` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000027`
