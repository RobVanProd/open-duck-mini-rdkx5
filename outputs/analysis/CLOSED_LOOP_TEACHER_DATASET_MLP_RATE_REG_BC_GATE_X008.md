# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_TERMINATED`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/closed_loop_teacher_dataset_manifest.json`
- dataset_id: `407af2cbe0ad69e1`
- samples: `6475`
- entries: `259`
- source_files: `16`
- max_source_fraction: `0.0772`
- warning: `False`

## Supervised Fit

- model_kind: `mlp`
- best_alpha: `1.0`
- train_rmse: `0.0355`
- train_mae: `0.0245`
- train_p95_abs_error: `0.0702`
- train_max_abs_error: `0.4307`
- pred_action_saturation_pct: `0.0055`
- sample_to_parameter_ratio: `0.5583`
- consecutive_pair_count: `2342`

### MLP Settings

- hidden_sizes: `[64, 64]`
- steps: `1000`
- batch_size: `512`
- learning_rate: `0.001`
- pair_count: `2342`
- target_rate_scale: `0.1`
- target_rate_limit_rad_s: `3.75`

| step | loss |
|---:|---:|
| 1 | 1.057136 |
| 100 | 0.012279 |
| 200 | 0.006080 |
| 300 | 0.003789 |
| 400 | 0.003469 |
| 500 | 0.002154 |
| 600 | 0.002028 |
| 700 | 0.001829 |
| 800 | 0.001568 |
| 900 | 0.001285 |
| 1000 | 0.001370 |

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 6025 | 450 | 0.0207 | 0.0571 | 1.4106 |
| published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5975 | 500 | 0.0139 | 0.0395 | 0.0918 |
| published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 6050 | 425 | 0.0177 | 0.0583 | 0.2764 |
| published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 6050 | 425 | 0.0119 | 0.0324 | 0.0796 |
| published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 6050 | 425 | 0.0225 | 0.0722 | 0.3437 |
| published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 6000 | 475 | 0.0157 | 0.0443 | 0.1812 |
| published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 6025 | 450 | 0.0175 | 0.0488 | 0.2426 |
| published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 6100 | 375 | 0.0145 | 0.0412 | 0.0868 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 6050 | 425 | 0.0162 | 0.0483 | 0.3077 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 6075 | 400 | 0.0139 | 0.0367 | 0.1180 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 6125 | 350 | 0.0216 | 0.0639 | 0.9256 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 6000 | 475 | 0.0137 | 0.0390 | 0.0991 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed4/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 6425 | 50 | 0.0626 | 0.1668 | 0.3824 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 6000 | 475 | 0.0167 | 0.0478 | 0.2725 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 6025 | 450 | 0.0166 | 0.0491 | 0.2383 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 6150 | 325 | 0.0136 | 0.0376 | 0.1192 |

## Closed-Loop Smoke

status: `HOLD_BC_REPLAY_TERMINATED`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `mlp`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 250 | duration_complete | 0.0138 | 0.1729 | 0.1585 | 0.0992 | 0.1519 | 5.2400 | 0.1288 |
| seed_001 | 250 | duration_complete | 0.0010 | 0.0131 | 0.2085 | 0.1064 | 0.1557 | 5.2400 | 0.1288 |
| seed_002 | 250 | duration_complete | 0.0195 | 0.2443 | 0.1955 | 0.1469 | 0.1511 | 5.2400 | 0.1285 |
| seed_003 | 66 | fall_or_progress_failure | -0.3138 | -3.9220 | 0.1180 | 1.2657 | 0.0450 | 5.2400 | 0.1230 |
| seed_004 | 250 | duration_complete | 0.0235 | 0.2942 | 0.1755 | 0.1165 | 0.1507 | 5.2400 | 0.1291 |
| seed_005 | 55 | fall_or_progress_failure | -0.2716 | -3.3944 | 0.1894 | 1.2593 | 0.0570 | 5.2400 | 0.1350 |
| seed_006 | 56 | fall_or_progress_failure | -0.3102 | -3.8779 | 0.3040 | 1.2582 | 0.0667 | 5.2400 | 0.1352 |
| seed_007 | 250 | duration_complete | 0.0078 | 0.0975 | 0.2053 | 0.1374 | 0.1531 | 5.2400 | 0.1310 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.2745 | 38.5091 | 0.8571 |
| seed_001 | 0.2766 | 38.5477 | 0.5714 |
| seed_002 | 0.2762 | 37.1800 | 0.6571 |
| seed_003 | 0.2626 | 41.3268 | 0.6494 |
| seed_004 | 0.2771 | 37.7127 | 0.6000 |
| seed_005 | 0.2710 | 31.6359 | 0.6494 |
| seed_006 | 0.2804 | 40.2165 | 0.6378 |
| seed_007 | 0.2644 | 34.7051 | 0.4000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
