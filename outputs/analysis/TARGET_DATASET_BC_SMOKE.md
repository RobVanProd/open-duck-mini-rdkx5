# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_LOW_FORWARD_MOTION`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/target_dataset_obs_manifest.json`
- dataset_id: `6c43c18e8f2b72ec`
- samples: `275`
- entries: `11`
- source_files: `2`
- max_source_fraction: `0.9091`
- warning: `True`

## Supervised Fit

- best_alpha: `1e-06`
- train_rmse: `0.0000`
- train_mae: `0.0000`
- train_p95_abs_error: `0.0000`
- train_max_abs_error: `0.0000`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `0.1926`

### Source Holdout

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 25 | 250 | 0.0913 | 0.3200 | 0.5580 |
| seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 250 | 25 | 0.0000 | 0.0000 | 0.0000 |

## Closed-Loop Smoke

status: `HOLD_BC_REPLAY_LOW_FORWARD_MOTION`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `linear`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 150 | duration_complete | -0.0023 | -0.0565 | 0.0908 | 0.0296 | 0.1536 | 0.0000 | 0.0367 |
| seed_002 | 150 | duration_complete | 0.0014 | 0.0340 | 0.0707 | 0.0368 | 0.1526 | 0.0001 | 0.0375 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.0001 | 0.0002 | 0.0000 |
| seed_002 | 0.0001 | 0.0002 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Source skew remains a warning because most curated windows come from one seed.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
