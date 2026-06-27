# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_LOW_FORWARD_MOTION`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/closed_loop_teacher_dataset_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `_seed7/`
- dataset_id: `407af2cbe0ad69e1`
- samples: `5775`
- entries: `231`
- source_files: `14`
- max_source_fraction: `0.0866`
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
- train_rmse: `0.0230`
- train_mae: `0.0155`
- train_p95_abs_error: `0.0449`
- train_max_abs_error: `0.5159`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `4.0441`
- consecutive_pair_count: `2058`

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5325 | 450 | 0.0209 | 0.0570 | 1.4106 |
| published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5275 | 500 | 0.0144 | 0.0409 | 0.0962 |
| published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5350 | 425 | 0.0177 | 0.0596 | 0.2652 |
| published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5350 | 425 | 0.0121 | 0.0329 | 0.0820 |
| published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5350 | 425 | 0.0224 | 0.0723 | 0.3420 |
| published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5300 | 475 | 0.0158 | 0.0450 | 0.1804 |
| published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5325 | 450 | 0.0180 | 0.0501 | 0.2450 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5350 | 425 | 0.0163 | 0.0480 | 0.3084 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5375 | 400 | 0.0140 | 0.0372 | 0.1229 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5425 | 350 | 0.0217 | 0.0636 | 0.9360 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5300 | 475 | 0.0141 | 0.0398 | 0.1004 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed4/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5725 | 50 | 0.0614 | 0.1647 | 0.3606 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5300 | 475 | 0.0168 | 0.0489 | 0.2637 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5325 | 450 | 0.0169 | 0.0499 | 0.2307 |

## Closed-Loop Smoke

status: `HOLD_BC_REPLAY_LOW_FORWARD_MOTION`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `vx_blend`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 250 | duration_complete | 0.0714 | 0.8921 | 0.1987 | 0.0570 | 0.1519 | 2.4608 | 0.1211 |
| seed_001 | 250 | duration_complete | 0.0010 | 0.0126 | 0.1184 | 0.0419 | 0.1559 | 0.3376 | 0.0320 |
| seed_002 | 250 | duration_complete | 0.0745 | 0.9311 | 0.1967 | 0.0608 | 0.1511 | 2.4716 | 0.1228 |
| seed_003 | 250 | duration_complete | 0.0522 | 0.6521 | 0.1799 | 0.1175 | 0.1534 | 2.4294 | 0.1200 |
| seed_004 | 250 | duration_complete | 0.0076 | 0.0946 | 0.0639 | 0.0679 | 0.1506 | 0.3621 | 0.0311 |
| seed_005 | 250 | duration_complete | 0.0744 | 0.9304 | 0.1997 | 0.1226 | 0.1462 | 2.5539 | 0.1234 |
| seed_006 | 250 | duration_complete | 0.0655 | 0.8189 | 0.2179 | 0.0601 | 0.1556 | 2.4568 | 0.1221 |
| seed_007 | 250 | duration_complete | 0.0025 | 0.0313 | 0.1528 | 0.0454 | 0.1558 | 0.3386 | 0.0314 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3327 | 9.8412 | 0.0000 |
| seed_001 | 0.4577 | 1.3381 | 0.0000 |
| seed_002 | 0.3328 | 9.8833 | 0.0000 |
| seed_003 | 0.3322 | 9.7176 | 0.0000 |
| seed_004 | 0.4587 | 1.4482 | 0.0000 |
| seed_005 | 0.3325 | 10.1421 | 0.0000 |
| seed_006 | 0.3325 | 9.8270 | 0.0000 |
| seed_007 | 0.4587 | 1.3497 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
