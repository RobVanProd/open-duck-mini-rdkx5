# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_TERMINATED`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/source_vx_selector_trace_right_knee_rate_limited_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `fitted`
- fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
- dataset_id: `d00ca78f667676e1`
- samples: `4000`
- entries: `8`
- source_files: `8`
- max_source_fraction: `0.1250`
- warning: `False`

## Supervised Fit

- model_kind: `blend`
- knn_k: `5`
- blend_alpha: `0.8`
- dwell_blend_alpha: `1.0`
- dwell_trigger_ticks: `20`
- vx_blend_alpha: `1.0`
- vx_blend_threshold_m_s: `0.02`
- source_vx_threshold_m_s: `0.02`
- best_alpha: `0.01`
- train_rmse: `0.0318`
- train_mae: `0.0211`
- train_p95_abs_error: `0.0667`
- train_max_abs_error: `0.3235`
- pred_action_saturation_pct: `0.0036`
- sample_to_parameter_ratio: `2.8011`
- consecutive_pair_count: `3992`

### Exact Blend ONNX

- exported_onnx: `outputs/analysis/source_vx_selector_trace_rk_limited_blend080_exact_onnx_candidate/candidate.onnx`
- input_name: `obs`
- output_name: `continuous_actions`
- knn_samples: `4000`
- knn_k: `5`
- blend_alpha: `0.8`
- onnx_verify_samples_checked: `32`
- onnx_verify_max_abs_error: `0.00000012`
- onnx_verify_p95_abs_error: `0.00000006`

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| source_vx_selector_trace_right_knee_rate_limited_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0218 | 0.0683 | 0.3287 |
| source_vx_selector_trace_right_knee_rate_limited_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0215 | 0.0676 | 0.4159 |
| source_vx_selector_trace_right_knee_rate_limited_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0221 | 0.0687 | 0.3349 |
| source_vx_selector_trace_right_knee_rate_limited_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0224 | 0.0718 | 0.3411 |
| source_vx_selector_trace_right_knee_rate_limited_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0226 | 0.0743 | 0.2961 |
| source_vx_selector_trace_right_knee_rate_limited_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0247 | 0.0821 | 0.3431 |
| source_vx_selector_trace_right_knee_rate_limited_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0228 | 0.0737 | 0.3817 |
| source_vx_selector_trace_right_knee_rate_limited_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0223 | 0.0706 | 0.4396 |

## Closed-Loop Smoke

status: `HOLD_BC_REPLAY_TERMINATED`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `blend`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 500 | duration_complete | 0.0503 | 0.6286 | 0.1642 | 0.0973 | 0.1520 | 2.1973 | 0.1805 |
| seed_001 | 500 | duration_complete | 0.0508 | 0.6348 | 0.1732 | 0.0986 | 0.1556 | 2.1357 | 0.1817 |
| seed_002 | 500 | duration_complete | 0.0521 | 0.6507 | 0.1607 | 0.1022 | 0.1509 | 2.1113 | 0.1810 |
| seed_003 | 500 | duration_complete | 0.0444 | 0.5550 | 0.1619 | 0.0998 | 0.1549 | 2.1502 | 0.1801 |
| seed_004 | 500 | duration_complete | 0.0508 | 0.6347 | 0.1562 | 0.0981 | 0.1506 | 2.1656 | 0.1815 |
| seed_005 | 69 | fall_or_progress_failure | -0.2103 | -2.6291 | 0.1624 | 1.2099 | 0.0649 | 1.9076 | 0.1748 |
| seed_006 | 500 | duration_complete | 0.0468 | 0.5854 | 0.1645 | 0.0981 | 0.1557 | 2.1848 | 0.1824 |
| seed_007 | 500 | duration_complete | 0.0490 | 0.6126 | 0.1614 | 0.1004 | 0.1559 | 2.2047 | 0.1813 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3337 | 8.7892 | 0.0000 |
| seed_001 | 0.3339 | 8.5430 | 0.0000 |
| seed_002 | 0.3338 | 8.4356 | 0.0000 |
| seed_003 | 0.3337 | 8.6006 | 0.0000 |
| seed_004 | 0.3339 | 8.6624 | 0.0000 |
| seed_005 | 0.3298 | 7.6219 | 0.0000 |
| seed_006 | 0.3334 | 8.7393 | 0.0000 |
| seed_007 | 0.3338 | 8.8189 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
