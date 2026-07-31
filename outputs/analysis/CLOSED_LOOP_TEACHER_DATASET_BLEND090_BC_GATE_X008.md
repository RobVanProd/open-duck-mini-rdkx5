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

- model_kind: `blend`
- knn_k: `5`
- blend_alpha: `0.9`
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
model_kind: `blend`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 250 | duration_complete | 0.0687 | 0.8582 | 0.1882 | 0.0595 | 0.1519 | 2.4390 | 0.1206 |
| seed_001 | 250 | duration_complete | 0.0007 | 0.0088 | 0.1079 | 0.0427 | 0.1559 | 0.2972 | 0.0321 |
| seed_002 | 250 | duration_complete | 0.0709 | 0.8862 | 0.1847 | 0.0620 | 0.1509 | 2.4404 | 0.1229 |
| seed_003 | 77 | fall_or_progress_failure | -0.2486 | -3.1080 | 0.1162 | 1.1835 | 0.0619 | 2.5133 | 0.1165 |
| seed_004 | 250 | duration_complete | 0.0073 | 0.0909 | 0.0634 | 0.0649 | 0.1506 | 0.3575 | 0.0311 |
| seed_005 | 250 | duration_complete | 0.0717 | 0.8958 | 0.1807 | 0.1178 | 0.1462 | 2.4806 | 0.1237 |
| seed_006 | 250 | duration_complete | 0.0634 | 0.7925 | 0.1945 | 0.0575 | 0.1556 | 2.4556 | 0.1222 |
| seed_007 | 250 | duration_complete | 0.0025 | 0.0310 | 0.1421 | 0.0425 | 0.1558 | 0.2981 | 0.0313 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3316 | 9.7559 | 0.0000 |
| seed_001 | 0.4572 | 1.1582 | 0.0000 |
| seed_002 | 0.3311 | 9.7617 | 0.0000 |
| seed_003 | 0.3326 | 9.9845 | 0.0000 |
| seed_004 | 0.4577 | 1.4291 | 0.0000 |
| seed_005 | 0.3313 | 9.9225 | 0.0000 |
| seed_006 | 0.3312 | 9.8222 | 0.0000 |
| seed_007 | 0.4578 | 1.1648 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
