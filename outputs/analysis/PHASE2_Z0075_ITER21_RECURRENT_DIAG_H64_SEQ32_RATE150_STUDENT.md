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

- manifest: `outputs/analysis/phase2_z0075_iter21_seed67_w2_seed1_plus_seed2_merged_manifest.json`
- sequences: `98`
- samples: `53834`
- hidden_dim: `64`
- sequence_length: `32`

## Fit Metrics

- MAE: `0.012817`
- p95 abs error: `0.040449`
- max abs error: `0.816932`
- target-rate p95: `1.338052` rad/s
- target-rate max: `9.128114` rad/s

## ONNX Verification

- steps checked: `128`
- max action error: `0.00000029`
- max hidden error: `0.00000074`

## Eval Command

```bash
tools/run_candidate_seed_sweep.py \
  --policies recurrent=policy/candidates/phase2_z0075_iter21_recurrent_diag_h64_seq32_rate150_20260704/candidate.onnx \
  --policy-obs-input-name obs \
  --policy-action-output-name continuous_actions \
  --policy-state-input-names h_in \
  --policy-state-output-names h_out \
  --task flat_terrain_backlash --bridge-mode fitted --command-x 0.08 --duration 15 --seeds 0-7 --run
```
