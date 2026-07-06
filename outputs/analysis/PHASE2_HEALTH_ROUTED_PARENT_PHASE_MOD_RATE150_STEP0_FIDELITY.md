# Phase-Modulated PPO Warm-Start Step-0 Export Fidelity

status: `PASS_PHASE_MODULATED_PPO_WARMSTART_STEP0_EXPORT_FIDELITY`

This is an offline PPO-param construction and export check. It did not
run PPO updates, SSH, deploy, run robot tests, grounded replay, or
change robot runtime behavior.

## Inputs

- BC NPZ: `outputs/analysis/phase2_health_routed_pass_parent_phase_mod_rate150_student/candidate_mlp.npz`
- BC NPZ sha256: `1e22aa3c06a451e3ee4da32e58c6b45b881cdf87ea8ed8738c541b6dccb3e9c8`
- reference ONNX: `policy/candidates/phase2_health_routed_parent_phase_mod_rate150_20260706/candidate.onnx`
- reference ONNX sha256: `5cadefcb3582043eb989a0e7c65ea9e2702a0815ba46c9ffe1c70b1f68f1db8f`
- manifest: `outputs/analysis/phase2_health_routed_parent_manifest.json`

## Outputs

- checkpoint: `outputs/analysis/phase2_health_routed_parent_phase_mod_rate150_step0_checkpoint`
- checkpoint absolute path: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_health_routed_parent_phase_mod_rate150_step0_checkpoint`
- exported ONNX: `outputs/analysis/phase2_health_routed_parent_phase_mod_rate150_step0.onnx`
- exported ONNX sha256: `5d41eab6945f7e64e5b3d9c15ab38ba388ba38e616fd5c04bbf46f5b9237d626`

## Architecture

- policy network kind: `phase_modulated`
- trunk hidden sizes: `[512, 256]`
- context hidden sizes: `[64]`
- context indices: `[6, 99, 100]`
- activation: `swish`
- modulation scale: `0.5`
- output mode: `tanh_normal_logits_with_phase_modulated_loc`

## Fidelity

- samples checked: `3750`
- MAE: `0.00000000`
- p95 abs error: `0.00000000`
- max abs error: `0.00000000`

## Decision

If this passes, the exported PPO step-0 policy reproduces the
phase-modulated parent ONNX at the action level while preserving a
restorable PPO checkpoint shape. The next gate is the standard
corrected-bridge x=0.08 and x=0.0 full8 sweep from this exported ONNX
before any domain-randomized PPO updates.
