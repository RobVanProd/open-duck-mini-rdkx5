# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_TERMINATED`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/target_dataset_manifest_dynamic_roll_lateral_fix_robust_modes.json`
- dataset_id: `47153f26ab48ef14`
- samples: `450`
- entries: `9`
- source_files: `2`
- max_source_fraction: `0.6667`
- warning: `False`

## Supervised Fit

- best_alpha: `1e-06`
- train_rmse: `0.0000`
- train_mae: `0.0000`
- train_p95_abs_error: `0.0000`
- train_max_abs_error: `0.0000`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `0.3151`

### Source Holdout

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 300 | 150 | 0.0000 | 0.0000 | 0.0000 |
| seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 150 | 300 | 0.0000 | 0.0000 | 0.0000 |

## Closed-Loop Smoke

status: `HOLD_BC_REPLAY_TERMINATED`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `linear`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 73 | fall_or_progress_failure | -0.2415 | -6.0379 | 0.1931 | 1.1625 | 0.0542 | 0.0000 | 0.0333 |
| seed_002 | 200 | duration_complete | -0.0041 | -0.1029 | 0.0391 | 0.1244 | 0.1527 | 0.0000 | 0.0254 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.0457 | 0.0001 | 0.0000 |
| seed_002 | 0.0457 | 0.0000 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Source skew remains a warning because most curated windows come from one seed.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
