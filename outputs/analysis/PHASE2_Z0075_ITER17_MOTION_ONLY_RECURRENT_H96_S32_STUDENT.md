# Recurrent BC Student

status: `PASS_RECURRENT_BC_FIT_SMOKE`

Offline stateful behavior-cloning diagnostic. It did not train PPO, deploy, SSH, run robot tests, or change robot runtime behavior.

## Contract

```text
inputs:  obs[1,101], h_in[1,H]
outputs: continuous_actions[1,14], h_out[1,H]
```

This ONNX is not robot-deployable without a runtime hidden-state adapter.

## Inputs

- manifest: `outputs/analysis/phase2_z0075_iter17_motion_only_recurrent_manifest.json`
- sequences: `51`
- samples: `32073`
- hidden_dim: `96`
- sequence_length: `32`

## Fit Metrics

- MAE: `0.014685`
- p95 abs error: `0.041933`
- max abs error: `0.684440`
- target-rate p95: `1.460732` rad/s
- target-rate max: `5.068715` rad/s

## ONNX Verification

- steps checked: `128`
- max action error: `0.00000058`
- max hidden error: `0.00000101`

## Eval Command

```bash
tools/run_candidate_seed_sweep.py \
  --policies recurrent=outputs/analysis/phase2_z0075_iter17_motion_only_recurrent_h96_s32_candidate/candidate.onnx \
  --policy-obs-input-name obs \
  --policy-action-output-name continuous_actions \
  --policy-state-input-names h_in \
  --policy-state-output-names h_out \
  --task flat_terrain_backlash --bridge-mode fitted --command-x 0.08 --duration 15 --seeds 0-7 --run
```
