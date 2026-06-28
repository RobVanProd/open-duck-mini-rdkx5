# Phase-Modulated BC Student

status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

Offline behavior cloning with a shared trunk and command/phase modulation.
No robot tests, SSH, deploy, runtime behavior changes, or PPO training were performed.

## Inputs

- manifest: `outputs/analysis/phase2_seed4_weighted_knee_ankle_leftknee_limit_command_seed4x25_manifest.json`
- samples: `750`
- context indices: `[6, 99, 100]`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- modulation scale: `0.75`

## Outputs

- NPZ: `outputs/analysis/phase2_seed4_weighted_knee_ankle_leftknee_limit_phasecmd_seed4x25_bc_student/candidate_mlp.npz`
- ONNX: `outputs/analysis/phase2_seed4_weighted_knee_ankle_leftknee_limit_phasecmd_seed4x25_bc_student/candidate.onnx`

## Fit Metrics

- MAE: `0.001992`
- p95 abs error: `0.005491`
- max abs error: `0.011753`
- target-rate p95: `1.687814` rad/s
- target-rate max: `2.889130` rad/s

## ONNX Verification

- samples checked: `64`
- p95 abs error: `0.00000012`
- max abs error: `0.00000024`
