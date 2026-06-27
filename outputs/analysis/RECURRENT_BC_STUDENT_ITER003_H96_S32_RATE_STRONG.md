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
- hidden_dim: `96`
- sequence_length: `32`

## Fit Metrics

- MAE: `0.045471`
- p95 abs error: `0.128499`
- max abs error: `1.290286`
- target-rate p95: `2.040496` rad/s
- target-rate max: `5.606293` rad/s

## ONNX Verification

- steps checked: `128`
- max action error: `0.00000056`
- max hidden error: `0.00000094`

## Eval Command

```bash
tools/run_candidate_seed_sweep.py \
  --policies recurrent=outputs/analysis/recurrent_bc_student_iter003_h96_s32_rate_strong/candidate.onnx \
  --policy-obs-input-name obs \
  --policy-action-output-name continuous_actions \
  --policy-state-input-names h_in \
  --policy-state-output-names h_out \
  --task flat_terrain_backlash --bridge-mode fitted --command-x 0.08 --duration 15 --seeds 0-7 --run
```
