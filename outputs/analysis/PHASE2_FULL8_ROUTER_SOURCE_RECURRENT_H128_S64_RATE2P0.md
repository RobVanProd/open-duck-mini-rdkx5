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

- manifest: `outputs/analysis/phase2_full8_router_source_selected_manifest.json`
- sequences: `8`
- samples: `6000`
- hidden_dim: `128`
- sequence_length: `64`

## Fit Metrics

- MAE: `0.009001`
- p95 abs error: `0.022976`
- max abs error: `0.141781`
- target-rate p95: `1.455623` rad/s
- target-rate max: `2.315070` rad/s

## ONNX Verification

- steps checked: `128`
- max action error: `0.00000056`
- max hidden error: `0.00000124`

## Eval Command

```bash
tools/run_candidate_seed_sweep.py \
  --policies recurrent=outputs/analysis/phase2_full8_router_source_recurrent_h128_s64_rate2p0/candidate.onnx \
  --policy-obs-input-name obs \
  --policy-action-output-name continuous_actions \
  --policy-state-input-names h_in \
  --policy-state-output-names h_out \
  --task flat_terrain_backlash --bridge-mode fitted --command-x 0.08 --duration 15 --seeds 0-7 --run
```
