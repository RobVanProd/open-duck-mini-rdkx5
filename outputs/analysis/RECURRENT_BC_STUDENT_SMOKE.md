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

- manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_003/live_oracle_dagger_aggregate_manifest.json`
- sequences: `18`
- samples: `11500`
- hidden_dim: `32`
- sequence_length: `16`

## Fit Metrics

- MAE: `0.197966`
- p95 abs error: `0.493650`
- max abs error: `1.588997`
- target-rate p95: `4.425967` rad/s
- target-rate max: `18.663213` rad/s

## ONNX Verification

- steps checked: `32`
- max action error: `0.00000071`
- max hidden error: `0.00000085`

## Eval Command

```bash
tools/run_candidate_seed_sweep.py \
  --policies recurrent=outputs/analysis/recurrent_bc_student_smoke/candidate.onnx \
  --policy-obs-input-name obs \
  --policy-action-output-name continuous_actions \
  --policy-state-input-names h_in \
  --policy-state-output-names h_out \
  --task flat_terrain_backlash --bridge-mode fitted --command-x 0.08 --duration 15 --seeds 0-7 --run
```
