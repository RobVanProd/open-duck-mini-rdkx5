# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_TERMINATED`

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

status: `HOLD_BC_REPLAY_TERMINATED`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `source_vx_blend`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_008 | 500 | duration_complete | 0.0315 | 0.3941 | 0.1124 | 0.0594 | 0.1487 | 2.2927 | 0.1820 |
| seed_009 | 34 | fall_or_progress_failure | -0.4207 | -5.2590 | 0.0452 | 1.4243 | 0.0615 | 1.6411 | 0.1577 |
| seed_010 | 500 | duration_complete | 0.0336 | 0.4204 | 0.1237 | 0.0607 | 0.1514 | 2.2931 | 0.1830 |
| seed_011 | 500 | duration_complete | 0.0322 | 0.4020 | 0.1638 | 0.0709 | 0.1587 | 2.2668 | 0.1821 |
| seed_012 | 37 | fall_or_progress_failure | -0.3917 | -4.8958 | 0.1934 | 1.3979 | 0.0629 | 1.7810 | 0.1611 |
| seed_013 | 22 | fall_or_progress_failure | 0.0185 | 0.2317 | 1.4450 | 0.2191 | 0.0854 | 2.3521 | 0.1954 |
| seed_014 | 37 | fall_or_progress_failure | -0.0770 | -0.9624 | 1.1052 | 0.2023 | 0.0752 | 2.4277 | 0.1547 |
| seed_015 | 21 | fall_or_progress_failure | -0.0201 | -0.2512 | 1.3741 | 0.0942 | 0.0673 | 1.9475 | 0.1678 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_008 | 0.3372 | 9.1090 | 0.0000 |
| seed_009 | 0.3158 | 6.3338 | 0.0000 |
| seed_010 | 0.3367 | 9.1493 | 0.0000 |
| seed_011 | 0.3352 | 9.0333 | 0.0000 |
| seed_012 | 0.3193 | 7.4135 | 0.0000 |
| seed_013 | 0.3314 | 9.2871 | 0.0000 |
| seed_014 | 0.3223 | 9.7110 | 0.0000 |
| seed_015 | 0.3259 | 7.7901 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
