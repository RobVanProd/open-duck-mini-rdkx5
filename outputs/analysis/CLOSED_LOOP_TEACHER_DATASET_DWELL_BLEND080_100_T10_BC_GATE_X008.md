# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_LOW_FORWARD_MOTION`

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

- model_kind: `dwell_blend`
- knn_k: `5`
- blend_alpha: `0.8`
- dwell_blend_alpha: `1.0`
- dwell_trigger_ticks: `10`
- best_alpha: `1.0`
- train_rmse: `0.0226`
- train_mae: `0.0152`
- train_p95_abs_error: `0.0435`
- train_max_abs_error: `0.5298`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `4.5343`
- consecutive_pair_count: `2342`

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

status: `HOLD_BC_REPLAY_LOW_FORWARD_MOTION`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `dwell_blend`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 250 | duration_complete | 0.0622 | 0.7777 | 0.1964 | 0.0673 | 0.1519 | 2.4505 | 0.1196 |
| seed_001 | 250 | duration_complete | 0.0001 | 0.0008 | 0.1094 | 0.0553 | 0.1559 | 0.3204 | 0.0311 |
| seed_002 | 250 | duration_complete | 0.0648 | 0.8106 | 0.1952 | 0.0586 | 0.1511 | 2.4710 | 0.1204 |
| seed_003 | 250 | duration_complete | 0.0418 | 0.5227 | 0.1713 | 0.1435 | 0.1535 | 2.3833 | 0.1179 |
| seed_004 | 250 | duration_complete | 0.0070 | 0.0871 | 0.0708 | 0.0571 | 0.1509 | 0.3205 | 0.0314 |
| seed_005 | 250 | duration_complete | 0.0643 | 0.8043 | 0.1845 | 0.1256 | 0.1462 | 2.4494 | 0.1210 |
| seed_006 | 250 | duration_complete | 0.0567 | 0.7093 | 0.1997 | 0.0609 | 0.1556 | 2.4188 | 0.1202 |
| seed_007 | 250 | duration_complete | 0.0023 | 0.0292 | 0.1529 | 0.0480 | 0.1558 | 0.3147 | 0.0312 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3313 | 9.8022 | 0.0000 |
| seed_001 | 0.4580 | 1.2797 | 0.0000 |
| seed_002 | 0.3312 | 9.8838 | 0.0000 |
| seed_003 | 0.3314 | 9.5009 | 0.0000 |
| seed_004 | 0.4590 | 1.2525 | 0.0000 |
| seed_005 | 0.3314 | 9.7469 | 0.0000 |
| seed_006 | 0.3309 | 9.6753 | 0.0000 |
| seed_007 | 0.4582 | 1.2556 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
