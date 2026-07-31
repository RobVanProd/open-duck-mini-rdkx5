# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_z005_live_oracle_terrain_support_iter0_aggregate_manifest.json`
- samples: `12806`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.5`

## Outputs

- NPZ: `outputs/analysis/phase2_z005_live_oracle_iter0_phase_mod_bc_candidate/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_z005_live_oracle_iter0_phase_mod_bc_candidate/candidate.onnx`

## Fit Metrics

- MAE: `0.006227`
- p95 abs error: `0.018830`
- max abs error: `0.436818`
- target-rate p95: `1.783167` rad/s
- target-rate max: `2.163395` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000021`
