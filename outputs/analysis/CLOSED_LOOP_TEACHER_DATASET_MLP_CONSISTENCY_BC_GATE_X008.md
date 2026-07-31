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
- train_rmse: `0.0278`
- train_mae: `0.0193`
- train_p95_abs_error: `0.0542`
- train_max_abs_error: `0.3883`
- pred_action_saturation_pct: `0.0110`
- sample_to_parameter_ratio: `0.5583`
- consecutive_pair_count: `2342`

### MLP Settings

- hidden_sizes: `[64, 64]`
- steps: `1000`
- batch_size: `512`
- learning_rate: `0.001`
- pair_count: `2342`
- target_rate_scale: `0.0`
- target_rate_limit_rad_s: `3.75`
- obs_noise_std: `0.02`
- obs_consistency_scale: `1.0`

| step | loss |
|---:|---:|
| 1 | 0.539272 |
| 100 | 0.008877 |
| 200 | 0.004192 |
| 300 | 0.002988 |
| 400 | 0.002158 |
| 500 | 0.001818 |
| 600 | 0.001379 |
| 700 | 0.001140 |
| 800 | 0.000905 |
| 900 | 0.000798 |
| 1000 | 0.000980 |

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
| seed_000 | 250 | duration_complete | 0.0169 | 0.2118 | 0.1549 | 0.0860 | 0.1520 | 5.2400 | 0.1336 |
| seed_001 | 250 | duration_complete | 0.0053 | 0.0665 | 0.1553 | 0.0896 | 0.1553 | 5.2400 | 0.1168 |
| seed_002 | 250 | duration_complete | 0.0095 | 0.1193 | 0.1302 | 0.0901 | 0.1510 | 5.2400 | 0.1201 |
| seed_003 | 70 | fall_or_progress_failure | -0.2318 | -2.8978 | 0.3538 | 1.2229 | 0.0609 | 5.2400 | 0.1474 |
| seed_004 | 250 | duration_complete | 0.0230 | 0.2876 | 0.1625 | 0.1125 | 0.1508 | 5.2400 | 0.1264 |
| seed_005 | 122 | fall_or_progress_failure | -0.1262 | -1.5776 | 0.1942 | 0.9647 | 0.0497 | 5.2400 | 0.1373 |
| seed_006 | 171 | fall_or_progress_failure | -0.1001 | -1.2513 | 0.1882 | 0.8034 | 0.0403 | 5.2400 | 0.1243 |
| seed_007 | 250 | duration_complete | 0.0203 | 0.2533 | 0.2108 | 0.1147 | 0.1555 | 5.2400 | 0.1282 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.2836 | 38.0178 | 0.5429 |
| seed_001 | 0.2994 | 45.9512 | 0.3714 |
| seed_002 | 0.2840 | 44.5685 | 0.4571 |
| seed_003 | 0.2928 | 31.0661 | 0.4082 |
| seed_004 | 0.2879 | 43.8380 | 0.7143 |
| seed_005 | 0.2786 | 30.5719 | 0.4098 |
| seed_006 | 0.2830 | 42.2425 | 0.5430 |
| seed_007 | 0.2858 | 41.4550 | 0.5429 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
