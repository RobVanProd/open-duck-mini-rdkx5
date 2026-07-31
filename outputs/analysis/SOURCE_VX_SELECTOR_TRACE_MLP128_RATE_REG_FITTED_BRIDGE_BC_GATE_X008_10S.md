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
- train_rmse: `0.0340`
- train_mae: `0.0208`
- train_p95_abs_error: `0.0645`
- train_max_abs_error: `0.3228`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `0.1275`
- consecutive_pair_count: `3992`

### MLP Settings

- hidden_sizes: `[128, 128]`
- steps: `3000`
- batch_size: `512`
- learning_rate: `0.001`
- pair_count: `3992`
- target_rate_scale: `0.1`
- target_rate_limit_rad_s: `2.5`
- obs_noise_std: `0.0`
- obs_consistency_scale: `0.0`

| step | loss |
|---:|---:|
| 1 | 1.406142 |
| 300 | 0.003277 |
| 600 | 0.002506 |
| 900 | 0.001928 |
| 1200 | 0.001855 |
| 1500 | 0.001690 |
| 1800 | 0.001500 |
| 2100 | 0.001269 |
| 2400 | 0.001335 |
| 2700 | 0.001374 |
| 3000 | 0.001371 |

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
| seed_000 | 340 | fall_or_progress_failure | -0.0428 | -0.5352 | 0.1387 | 0.4037 | 0.0668 | 3.9808 | 0.1389 |
| seed_001 | 198 | fall_or_progress_failure | -0.0840 | -1.0499 | 0.1791 | 0.6901 | 0.0555 | 3.9625 | 0.1346 |
| seed_002 | 434 | fall_or_progress_failure | -0.0371 | -0.4631 | 0.1195 | 0.3168 | 0.0489 | 3.8331 | 0.1283 |
| seed_003 | 500 | duration_complete | -0.0047 | -0.0589 | 0.1286 | 0.1520 | 0.1509 | 3.9812 | 0.1333 |
| seed_004 | 353 | fall_or_progress_failure | -0.0420 | -0.5253 | 0.1445 | 0.3556 | 0.0573 | 4.3412 | 0.1465 |
| seed_005 | 79 | fall_or_progress_failure | -0.1963 | -2.4535 | 0.1591 | 1.2246 | 0.0471 | 3.6588 | 0.1437 |
| seed_006 | 198 | fall_or_progress_failure | -0.0866 | -1.0824 | 0.1656 | 0.6951 | 0.0599 | 4.0074 | 0.1329 |
| seed_007 | 99 | fall_or_progress_failure | -0.1665 | -2.0815 | 0.2236 | 1.0923 | 0.0564 | 4.4620 | 0.1293 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.2740 | 15.9331 | 0.3361 |
| seed_001 | 0.2659 | 15.9116 | 0.2165 |
| seed_002 | 0.2714 | 15.3428 | 0.2962 |
| seed_003 | 0.2677 | 15.9284 | 0.3429 |
| seed_004 | 0.2753 | 17.3900 | 0.0809 |
| seed_005 | 0.2777 | 14.4749 | 0.2712 |
| seed_006 | 0.2688 | 16.0613 | 0.2165 |
| seed_007 | 0.2645 | 18.0786 | 0.1443 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
