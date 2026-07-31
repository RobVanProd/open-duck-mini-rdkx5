# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_TERMINATED`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/closed_loop_teacher_dataset_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `_seed(4|7)/`
- dataset_id: `407af2cbe0ad69e1`
- samples: `5300`
- entries: `212`
- source_files: `12`
- max_source_fraction: `0.0943`
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
- train_rmse: `0.0200`
- train_mae: `0.0138`
- train_p95_abs_error: `0.0391`
- train_max_abs_error: `0.3993`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `3.7115`
- consecutive_pair_count: `1896`

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4850 | 450 | 0.0199 | 0.0550 | 1.2958 |
| published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4800 | 500 | 0.0137 | 0.0379 | 0.0855 |
| published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4875 | 425 | 0.0168 | 0.0548 | 0.2639 |
| published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4875 | 425 | 0.0116 | 0.0316 | 0.0840 |
| published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4825 | 475 | 0.0150 | 0.0429 | 0.2196 |
| published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4850 | 450 | 0.0172 | 0.0469 | 0.2694 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4875 | 425 | 0.0148 | 0.0432 | 0.2652 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4900 | 400 | 0.0126 | 0.0340 | 0.1027 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4950 | 350 | 0.0208 | 0.0646 | 0.9718 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4825 | 475 | 0.0129 | 0.0362 | 0.0792 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4825 | 475 | 0.0157 | 0.0451 | 0.3268 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4850 | 450 | 0.0157 | 0.0478 | 0.2069 |

## Closed-Loop Smoke

status: `HOLD_BC_REPLAY_TERMINATED`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `vx_blend`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 250 | duration_complete | 0.0724 | 0.9044 | 0.1945 | 0.0586 | 0.1520 | 2.4656 | 0.1217 |
| seed_001 | 250 | duration_complete | 0.0713 | 0.8909 | 0.2161 | 0.0571 | 0.1560 | 2.5126 | 0.1209 |
| seed_002 | 250 | duration_complete | 0.0733 | 0.9165 | 0.1903 | 0.0571 | 0.1510 | 2.4552 | 0.1213 |
| seed_003 | 113 | fall_or_progress_failure | -0.1709 | -2.1360 | 0.1485 | 1.0305 | 0.0533 | 2.5036 | 0.1112 |
| seed_004 | 250 | duration_complete | 0.0742 | 0.9269 | 0.2005 | 0.0773 | 0.1506 | 2.4925 | 0.1234 |
| seed_005 | 250 | duration_complete | 0.0704 | 0.8803 | 0.1836 | 0.1287 | 0.1465 | 2.4887 | 0.1223 |
| seed_006 | 250 | duration_complete | 0.0692 | 0.8655 | 0.2287 | 0.0592 | 0.1559 | 2.4668 | 0.1207 |
| seed_007 | 250 | duration_complete | 0.0746 | 0.9329 | 0.2049 | 0.0558 | 0.1559 | 2.5214 | 0.1205 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3335 | 9.8437 | 0.0000 |
| seed_001 | 0.3331 | 10.0225 | 0.0000 |
| seed_002 | 0.3333 | 9.8207 | 0.0000 |
| seed_003 | 0.3324 | 9.9648 | 0.0000 |
| seed_004 | 0.3326 | 9.9467 | 0.0000 |
| seed_005 | 0.3332 | 9.9480 | 0.0000 |
| seed_006 | 0.3323 | 9.8568 | 0.0000 |
| seed_007 | 0.3335 | 10.0854 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
