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

- manifest: `outputs/analysis/phase2_terrain_safe_hard_step_bc_manifest.json`
- sequences: `4`
- samples: `400`
- hidden_dim: `64`
- sequence_length: `32`

## Fit Metrics

- MAE: `0.015138`
- p95 abs error: `0.040416`
- max abs error: `0.159731`
- target-rate p95: `2.198696` rad/s
- target-rate max: `3.856978` rad/s

## ONNX Verification

- steps checked: `64`
- max action error: `0.00000048`
- max hidden error: `0.00000079`

## Eval Command

```bash
tools/run_candidate_seed_sweep.py \
  --policies recurrent=outputs/analysis/phase2_terrain_safe_hard_step_recurrent_bc_student/candidate_recurrent.onnx \
  --policy-obs-input-name obs \
  --policy-action-output-name continuous_actions \
  --policy-state-input-names h_in \
  --policy-state-output-names h_out \
  --task flat_terrain_backlash --bridge-mode fitted --command-x 0.08 --duration 15 --seeds 0-7 --run
```
