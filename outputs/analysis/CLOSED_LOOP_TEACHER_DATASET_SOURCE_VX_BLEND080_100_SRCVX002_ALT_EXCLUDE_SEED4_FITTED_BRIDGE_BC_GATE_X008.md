# Target Dataset BC Smoke

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/closed_loop_teacher_dataset_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `_seed4/`
- actuator_bridge_mode: `fitted`
- fit_json: `outputs/analysis/actuator_response_fit.json`
- dataset_id: `407af2cbe0ad69e1`
- samples: `6475`
- entries: `259`
- source_files: `16`
- max_source_fraction: `0.0772`
- warning: `False`
- alt_samples: `6000`
- alt_entries: `240`
- alt_source_files: `14`
- alt_best_alpha: `1.0`

## Supervised Fit

- model_kind: `source_vx_blend`
- knn_k: `5`
- blend_alpha: `0.8`
- dwell_blend_alpha: `1.0`
- dwell_trigger_ticks: `20`
- vx_blend_alpha: `1.0`
- vx_blend_threshold_m_s: `-0.02`
- source_vx_threshold_m_s: `0.02`
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

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `source_vx_blend`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 250 | duration_complete | 0.0507 | 0.6339 | 0.1460 | 0.0951 | 0.1520 | 2.3152 | 0.1830 |
| seed_001 | 250 | duration_complete | 0.0420 | 0.5254 | 0.1723 | 0.0926 | 0.1556 | 2.4031 | 0.1850 |
| seed_002 | 250 | duration_complete | 0.0514 | 0.6424 | 0.1527 | 0.0993 | 0.1509 | 2.2118 | 0.1805 |
| seed_003 | 250 | duration_complete | 0.0409 | 0.5117 | 0.1466 | 0.1088 | 0.1554 | 2.1978 | 0.1802 |
| seed_004 | 250 | duration_complete | 0.0456 | 0.5706 | 0.1401 | 0.0975 | 0.1506 | 2.3668 | 0.1871 |
| seed_005 | 250 | duration_complete | 0.0486 | 0.6073 | 0.1485 | 0.1585 | 0.1462 | 2.3112 | 0.1831 |
| seed_006 | 250 | duration_complete | 0.0392 | 0.4895 | 0.1577 | 0.0957 | 0.1557 | 2.4075 | 0.1866 |
| seed_007 | 250 | duration_complete | 0.0461 | 0.5761 | 0.1605 | 0.0976 | 0.1557 | 2.4033 | 0.1860 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3351 | 9.2447 | 0.0000 |
| seed_001 | 0.3350 | 9.5832 | 0.0000 |
| seed_002 | 0.3346 | 8.8286 | 0.0000 |
| seed_003 | 0.3342 | 8.7912 | 0.0000 |
| seed_004 | 0.3361 | 9.4527 | 0.0000 |
| seed_005 | 0.3351 | 9.2379 | 0.0000 |
| seed_006 | 0.3349 | 9.6065 | 0.0000 |
| seed_007 | 0.3352 | 9.5480 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
