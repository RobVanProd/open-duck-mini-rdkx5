# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_full8_router_tneg1p8_bc_trace_manifest_seed56_weighted.json`
- samples: `12000`
- context indices: `[6, 97, 98, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[128, 64]`
- modulation scale: `0.75`

## Outputs

- NPZ: `outputs/analysis/phase2_full8_router_tneg1p8_phase_contact_modulated_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_full8_router_tneg1p8_phase_contact_modulated_student/candidate.onnx`

## Fit Metrics

- MAE: `0.002042`
- p95 abs error: `0.006017`
- max abs error: `0.029472`
- target-rate p95: `1.259359` rad/s
- target-rate max: `1.837669` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000003`
- max abs error: `0.00000005`
