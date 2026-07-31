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
| seed_016 | 500 | duration_complete | 0.0320 | 0.4005 | 0.1588 | 0.0753 | 0.1594 | 2.3115 | 0.1809 |
| seed_017 | 500 | duration_complete | 0.0316 | 0.3947 | 0.1254 | 0.0623 | 0.1549 | 2.2873 | 0.1793 |
| seed_018 | 500 | duration_complete | 0.0375 | 0.4686 | 0.1225 | 0.0581 | 0.1534 | 2.2718 | 0.1815 |
| seed_019 | 24 | fall_or_progress_failure | 0.0254 | 0.3170 | 1.3117 | 0.1187 | 0.0726 | 2.4829 | 0.2269 |
| seed_020 | 27 | fall_or_progress_failure | 0.1082 | 1.3528 | 1.3347 | 0.3611 | 0.0720 | 2.2961 | 0.1975 |
| seed_021 | 500 | duration_complete | 0.0286 | 0.3581 | 0.1285 | 0.0606 | 0.1540 | 2.3224 | 0.1791 |
| seed_022 | 500 | duration_complete | 0.0322 | 0.4028 | 0.1188 | 0.0575 | 0.1549 | 2.3043 | 0.1818 |
| seed_023 | 500 | duration_complete | 0.0264 | 0.3305 | 0.1391 | 0.0944 | 0.1546 | 2.2873 | 0.1807 |
| seed_024 | 500 | duration_complete | 0.0378 | 0.4724 | 0.1147 | 0.0546 | 0.1542 | 2.3020 | 0.1791 |
| seed_025 | 23 | fall_or_progress_failure | -0.3532 | -4.4149 | 1.0781 | 0.5745 | 0.1132 | 2.1369 | 0.1228 |
| seed_026 | 33 | fall_or_progress_failure | 0.0183 | 0.2285 | 1.1957 | 0.0914 | 0.0745 | 2.7151 | 0.1709 |
| seed_027 | 500 | duration_complete | 0.0315 | 0.3939 | 0.1537 | 0.0638 | 0.1579 | 2.2873 | 0.1815 |
| seed_028 | 45 | fall_or_progress_failure | -0.0141 | -0.1766 | 1.1394 | 0.1523 | 0.0718 | 2.2375 | 0.1723 |
| seed_029 | 500 | duration_complete | 0.0315 | 0.3937 | 0.1311 | 0.0592 | 0.1559 | 2.2894 | 0.1806 |
| seed_030 | 500 | duration_complete | 0.0292 | 0.3646 | 0.1373 | 0.0611 | 0.1571 | 2.3278 | 0.1828 |
| seed_031 | 500 | duration_complete | 0.0324 | 0.4055 | 0.1228 | 0.0614 | 0.1556 | 2.2983 | 0.1793 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_016 | 0.3360 | 9.2348 | 0.0000 |
| seed_017 | 0.3362 | 9.1493 | 0.0000 |
| seed_018 | 0.3357 | 9.0052 | 0.0000 |
| seed_019 | 0.3203 | 9.9316 | 0.0000 |
| seed_020 | 0.3167 | 9.1844 | 0.0000 |
| seed_021 | 0.3368 | 9.2570 | 0.0000 |
| seed_022 | 0.3362 | 9.2122 | 0.0000 |
| seed_023 | 0.3367 | 9.0998 | 0.0000 |
| seed_024 | 0.3349 | 9.1468 | 0.0000 |
| seed_025 | 0.3237 | 8.2689 | 0.0000 |
| seed_026 | 0.3298 | 10.8605 | 0.0000 |
| seed_027 | 0.3355 | 9.1129 | 0.0000 |
| seed_028 | 0.3298 | 8.9717 | 0.0000 |
| seed_029 | 0.3360 | 9.0774 | 0.0000 |
| seed_030 | 0.3368 | 9.2862 | 0.0000 |
| seed_031 | 0.3359 | 9.1077 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
