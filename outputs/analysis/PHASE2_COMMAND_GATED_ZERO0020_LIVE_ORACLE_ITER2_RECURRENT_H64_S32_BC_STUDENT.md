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

- manifest: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2/live_oracle_dagger_aggregate_manifest.json`
- sequences: `16`
- samples: `11555`
- hidden_dim: `64`
- sequence_length: `32`

## Fit Metrics

- MAE: `0.004680`
- p95 abs error: `0.015230`
- max abs error: `0.193689`
- target-rate p95: `1.215406` rad/s
- target-rate max: `2.398595` rad/s

## ONNX Verification

- steps checked: `64`
- max action error: `0.00000051`
- max hidden error: `0.00000052`

## Eval Command

```bash
tools/run_candidate_seed_sweep.py \
  --policies recurrent=outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_recurrent_h64_s32_bc_student/candidate.onnx \
  --policy-obs-input-name obs \
  --policy-action-output-name continuous_actions \
  --policy-state-input-names h_in \
  --policy-state-output-names h_out \
  --task flat_terrain_backlash --bridge-mode fitted --command-x 0.08 --duration 15 --seeds 0-7 --run
```
