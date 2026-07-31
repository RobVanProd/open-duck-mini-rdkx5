# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_TERMINATED`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/source_vx_selector_fitted_bridge_trace_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `fitted`
- fit_json: `outputs/analysis/actuator_response_fit.json`
- dataset_id: `de4935ec7672ceea`
- samples: `4000`
- entries: `8`
- source_files: `8`
- max_source_fraction: `0.1250`
- warning: `False`

## Supervised Fit

- model_kind: `mlp`
- knn_k: `5`
- blend_alpha: `0.75`
- dwell_blend_alpha: `1.0`
- dwell_trigger_ticks: `20`
- vx_blend_alpha: `1.0`
- vx_blend_threshold_m_s: `0.02`
- source_vx_threshold_m_s: `0.02`
- best_alpha: `0.01`
- train_rmse: `0.0235`
- train_mae: `0.0167`
- train_p95_abs_error: `0.0463`
- train_max_abs_error: `0.2578`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `0.1275`
- consecutive_pair_count: `3992`

### MLP Settings

- hidden_sizes: `[128, 128]`
- steps: `3000`
- batch_size: `512`
- learning_rate: `0.001`
- pair_count: `3992`
- target_rate_scale: `0.0`
- target_rate_limit_rad_s: `3.75`
- obs_noise_std: `0.0`
- obs_consistency_scale: `0.0`

| step | loss |
|---:|---:|
| 1 | 0.592739 |
| 300 | 0.002048 |
| 600 | 0.001437 |
| 900 | 0.001005 |
| 1200 | 0.000882 |
| 1500 | 0.000816 |
| 1800 | 0.000657 |
| 2100 | 0.000643 |
| 2400 | 0.000540 |
| 2700 | 0.000506 |
| 3000 | 0.000548 |

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0221 | 0.0709 | 0.3287 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0218 | 0.0692 | 0.4159 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0225 | 0.0707 | 0.3349 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0226 | 0.0735 | 0.3411 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0229 | 0.0758 | 0.3679 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0249 | 0.0833 | 0.3431 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0231 | 0.0761 | 0.4804 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0227 | 0.0729 | 0.4396 |

## Closed-Loop Smoke

status: `HOLD_BC_REPLAY_TERMINATED`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `mlp`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 162 | fall_or_progress_failure | -0.1024 | -1.2799 | 0.1316 | 0.8119 | 0.0545 | 4.5262 | 0.1374 |
| seed_001 | 292 | fall_or_progress_failure | -0.0513 | -0.6412 | 0.1925 | 0.4693 | 0.0676 | 4.3248 | 0.1347 |
| seed_002 | 93 | fall_or_progress_failure | -0.1642 | -2.0520 | 0.2906 | 1.0255 | 0.0625 | 3.2478 | 0.1204 |
| seed_003 | 231 | fall_or_progress_failure | -0.0803 | -1.0032 | 0.1632 | 0.5571 | 0.0763 | 4.1091 | 0.1394 |
| seed_004 | 102 | fall_or_progress_failure | -0.1499 | -1.8735 | 0.1255 | 1.0228 | 0.0720 | 3.8750 | 0.1466 |
| seed_005 | 79 | fall_or_progress_failure | -0.2006 | -2.5070 | 0.1993 | 1.2144 | 0.0485 | 4.2994 | 0.1560 |
| seed_006 | 117 | fall_or_progress_failure | -0.1566 | -1.9572 | 0.1722 | 0.9585 | 0.0580 | 4.2882 | 0.1179 |
| seed_007 | 90 | fall_or_progress_failure | -0.1875 | -2.3437 | 0.2007 | 1.0918 | 0.0626 | 4.3493 | 0.1385 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.2769 | 18.1804 | 0.6173 |
| seed_001 | 0.2739 | 17.4151 | 0.5137 |
| seed_002 | 0.3018 | 12.9912 | 0.7680 |
| seed_003 | 0.2780 | 16.2919 | 0.7112 |
| seed_004 | 0.2754 | 15.4797 | 0.2801 |
| seed_005 | 0.2846 | 16.9095 | 0.0904 |
| seed_006 | 0.2786 | 17.4031 | 0.3663 |
| seed_007 | 0.2772 | 17.4321 | 0.2381 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
