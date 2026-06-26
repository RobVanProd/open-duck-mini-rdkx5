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

- model_kind: `knn`
- knn_k: `5`
- blend_alpha: `0.75`
- dwell_blend_alpha: `1.0`
- dwell_trigger_ticks: `20`
- vx_blend_alpha: `1.0`
- vx_blend_threshold_m_s: `0.02`
- source_vx_threshold_m_s: `0.02`
- best_alpha: `0.01`
- train_rmse: `0.0326`
- train_mae: `0.0214`
- train_p95_abs_error: `0.0681`
- train_max_abs_error: `0.4096`
- pred_action_saturation_pct: `0.0036`
- sample_to_parameter_ratio: `2.8011`
- consecutive_pair_count: `3992`

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
model_kind: `knn`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 500 | duration_complete | 0.0493 | 0.6164 | 0.1512 | 0.0966 | 0.1520 | 2.2165 | 0.1809 |
| seed_001 | 500 | duration_complete | 0.0450 | 0.5630 | 0.1695 | 0.0953 | 0.1556 | 2.2906 | 0.1835 |
| seed_002 | 500 | duration_complete | 0.0504 | 0.6295 | 0.1498 | 0.1004 | 0.1509 | 2.2161 | 0.1823 |
| seed_003 | 500 | duration_complete | 0.0430 | 0.5377 | 0.1533 | 0.1000 | 0.1549 | 2.1739 | 0.1821 |
| seed_004 | 500 | duration_complete | 0.0483 | 0.6032 | 0.1476 | 0.1010 | 0.1506 | 2.2096 | 0.1843 |
| seed_005 | 146 | fall_or_progress_failure | -0.1068 | -1.3352 | 0.1399 | 0.9017 | 0.0521 | 1.9342 | 0.1766 |
| seed_006 | 500 | duration_complete | 0.0449 | 0.5615 | 0.1582 | 0.0971 | 0.1557 | 2.2409 | 0.1831 |
| seed_007 | 500 | duration_complete | 0.0471 | 0.5893 | 0.1628 | 0.1002 | 0.1559 | 2.2584 | 0.1832 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3350 | 8.8648 | 0.0000 |
| seed_001 | 0.3352 | 9.1479 | 0.0000 |
| seed_002 | 0.3352 | 8.8630 | 0.0000 |
| seed_003 | 0.3347 | 8.6956 | 0.0000 |
| seed_004 | 0.3354 | 8.8386 | 0.0000 |
| seed_005 | 0.3325 | 7.6050 | 0.0000 |
| seed_006 | 0.3351 | 8.9635 | 0.0000 |
| seed_007 | 0.3352 | 9.0335 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
