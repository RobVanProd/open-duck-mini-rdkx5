# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_LOW_FORWARD_MOTION`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/target_dataset_manifest_dynamic_roll_lateral_fix.json`
- dataset_id: `0ff1f1c3750dbfb1`
- samples: `3500`
- entries: `70`
- source_files: `2`
- max_source_fraction: `0.8571`
- warning: `True`

## Supervised Fit

- best_alpha: `1e-06`
- train_rmse: `0.0003`
- train_mae: `0.0000`
- train_p95_abs_error: `0.0001`
- train_max_abs_error: `0.0571`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `2.4510`

### Source Holdout

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 500 | 3000 | 0.0000 | 0.0000 | 0.0735 |
| seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3000 | 500 | 0.0000 | 0.0001 | 0.0018 |

## Closed-Loop Smoke

status: `HOLD_BC_REPLAY_LOW_FORWARD_MOTION`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `knn`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 200 | duration_complete | 0.0064 | 0.1607 | 0.0650 | 0.2732 | 0.1465 | 0.3906 | 0.0744 |
| seed_002 | 200 | duration_complete | 0.0084 | 0.2099 | 0.0472 | 0.2658 | 0.1471 | 0.3876 | 0.0731 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.1386 | 1.5625 | 0.0000 |
| seed_002 | 0.1379 | 1.5503 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Source skew remains a warning because most curated windows come from one seed.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
