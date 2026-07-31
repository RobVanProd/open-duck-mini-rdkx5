# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_TERMINATED`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/closed_loop_teacher_dataset_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `_seed4/`
- dataset_id: `407af2cbe0ad69e1`
- samples: `6000`
- entries: `240`
- source_files: `14`
- max_source_fraction: `0.0833`
- warning: `False`

## Supervised Fit

- model_kind: `vx_blend`
- knn_k: `5`
- blend_alpha: `0.8`
- dwell_blend_alpha: `1.0`
- dwell_trigger_ticks: `20`
- vx_blend_alpha: `1.0`
- vx_blend_threshold_m_s: `-0.02`
- best_alpha: `1.0`
- train_rmse: `0.0196`
- train_mae: `0.0136`
- train_p95_abs_error: `0.0382`
- train_max_abs_error: `0.4121`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `4.2017`
- consecutive_pair_count: `2180`

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5550 | 450 | 0.0198 | 0.0552 | 1.3526 |
| published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5500 | 500 | 0.0132 | 0.0362 | 0.0871 |
| published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5575 | 425 | 0.0169 | 0.0558 | 0.2743 |
| published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5575 | 425 | 0.0114 | 0.0314 | 0.0762 |
| published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5525 | 475 | 0.0149 | 0.0417 | 0.2165 |
| published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5550 | 450 | 0.0166 | 0.0444 | 0.2626 |
| published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5625 | 375 | 0.0137 | 0.0378 | 0.0796 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5575 | 425 | 0.0148 | 0.0429 | 0.2665 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5600 | 400 | 0.0125 | 0.0337 | 0.1019 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5650 | 350 | 0.0209 | 0.0659 | 0.9843 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5525 | 475 | 0.0127 | 0.0352 | 0.0790 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5525 | 475 | 0.0157 | 0.0450 | 0.3338 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5550 | 450 | 0.0155 | 0.0478 | 0.2150 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5675 | 325 | 0.0126 | 0.0358 | 0.1010 |

## Closed-Loop Smoke

status: `HOLD_BC_REPLAY_TERMINATED`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `vx_blend`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 250 | duration_complete | 0.0721 | 0.9006 | 0.1911 | 0.0559 | 0.1520 | 2.4960 | 0.1220 |
| seed_001 | 250 | duration_complete | 0.0700 | 0.8756 | 0.2133 | 0.0577 | 0.1560 | 2.4777 | 0.1211 |
| seed_002 | 250 | duration_complete | 0.0732 | 0.9155 | 0.1869 | 0.0580 | 0.1510 | 2.4527 | 0.1213 |
| seed_003 | 124 | fall_or_progress_failure | -0.1431 | -1.7887 | 0.1174 | 0.9274 | 0.0695 | 2.4824 | 0.1162 |
| seed_004 | 250 | duration_complete | 0.0756 | 0.9444 | 0.2019 | 0.0800 | 0.1506 | 2.5048 | 0.1217 |
| seed_005 | 250 | duration_complete | 0.0729 | 0.9113 | 0.1878 | 0.1283 | 0.1465 | 2.4582 | 0.1239 |
| seed_006 | 250 | duration_complete | 0.0688 | 0.8594 | 0.2159 | 0.0627 | 0.1559 | 2.4639 | 0.1230 |
| seed_007 | 250 | duration_complete | 0.0740 | 0.9248 | 0.2046 | 0.0552 | 0.1559 | 2.4961 | 0.1200 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3327 | 9.9103 | 0.0000 |
| seed_001 | 0.3328 | 9.8920 | 0.0000 |
| seed_002 | 0.3331 | 9.7906 | 0.0000 |
| seed_003 | 0.3321 | 9.9296 | 0.0000 |
| seed_004 | 0.3332 | 9.9873 | 0.0000 |
| seed_005 | 0.3334 | 9.8212 | 0.0000 |
| seed_006 | 0.3322 | 9.8388 | 0.0000 |
| seed_007 | 0.3330 | 9.9842 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
