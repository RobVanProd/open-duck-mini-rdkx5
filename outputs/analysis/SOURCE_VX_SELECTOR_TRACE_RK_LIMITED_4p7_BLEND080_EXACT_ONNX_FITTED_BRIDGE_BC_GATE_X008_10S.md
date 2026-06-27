# Target Dataset BC Smoke

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/source_vx_selector_trace_right_knee_rate_limited_4p7_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `fitted`
- fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
- dataset_id: `80c1b243ae91154e`
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
- train_rmse: `0.0321`
- train_mae: `0.0212`
- train_p95_abs_error: `0.0674`
- train_max_abs_error: `0.3431`
- pred_action_saturation_pct: `0.0036`
- sample_to_parameter_ratio: `2.8011`
- consecutive_pair_count: `3992`

### Exact Blend ONNX

- exported_onnx: `outputs/analysis/source_vx_selector_trace_rk_limited_4p7_blend080_exact_onnx_candidate/candidate.onnx`
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
| source_vx_selector_trace_right_knee_rate_limited_4p7_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0219 | 0.0700 | 0.3287 |
| source_vx_selector_trace_right_knee_rate_limited_4p7_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0216 | 0.0684 | 0.4159 |
| source_vx_selector_trace_right_knee_rate_limited_4p7_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0223 | 0.0701 | 0.3349 |
| source_vx_selector_trace_right_knee_rate_limited_4p7_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0225 | 0.0729 | 0.3411 |
| source_vx_selector_trace_right_knee_rate_limited_4p7_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0227 | 0.0748 | 0.3521 |
| source_vx_selector_trace_right_knee_rate_limited_4p7_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0248 | 0.0823 | 0.3431 |
| source_vx_selector_trace_right_knee_rate_limited_4p7_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0229 | 0.0753 | 0.3834 |
| source_vx_selector_trace_right_knee_rate_limited_4p7_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0224 | 0.0718 | 0.4396 |

## Closed-Loop Smoke

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `blend`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 500 | duration_complete | 0.0521 | 0.6518 | 0.1630 | 0.0963 | 0.1520 | 2.1301 | 0.1821 |
| seed_001 | 500 | duration_complete | 0.0459 | 0.5742 | 0.1605 | 0.0953 | 0.1556 | 2.2123 | 0.1828 |
| seed_002 | 500 | duration_complete | 0.0495 | 0.6185 | 0.1589 | 0.0968 | 0.1509 | 2.1306 | 0.1820 |
| seed_003 | 500 | duration_complete | 0.0440 | 0.5504 | 0.1524 | 0.1019 | 0.1549 | 2.1869 | 0.1801 |
| seed_004 | 500 | duration_complete | 0.0478 | 0.5974 | 0.1555 | 0.0976 | 0.1506 | 2.1546 | 0.1823 |
| seed_005 | 500 | duration_complete | 0.0491 | 0.6135 | 0.1587 | 0.1330 | 0.1462 | 2.0730 | 0.1828 |
| seed_006 | 500 | duration_complete | 0.0441 | 0.5509 | 0.1608 | 0.0954 | 0.1557 | 2.1805 | 0.1834 |
| seed_007 | 500 | duration_complete | 0.0465 | 0.5812 | 0.1639 | 0.0975 | 0.1559 | 2.2247 | 0.1841 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3338 | 8.5206 | 0.0000 |
| seed_001 | 0.3343 | 8.8492 | 0.0000 |
| seed_002 | 0.3344 | 8.5168 | 0.0000 |
| seed_003 | 0.3343 | 8.7478 | 0.0000 |
| seed_004 | 0.3348 | 8.6185 | 0.0000 |
| seed_005 | 0.3339 | 8.2920 | 0.0000 |
| seed_006 | 0.3343 | 8.7219 | 0.0000 |
| seed_007 | 0.3343 | 8.8987 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
