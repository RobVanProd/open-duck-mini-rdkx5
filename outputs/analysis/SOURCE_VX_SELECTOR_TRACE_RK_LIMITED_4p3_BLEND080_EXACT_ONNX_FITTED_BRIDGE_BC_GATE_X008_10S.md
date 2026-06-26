# Target Dataset BC Smoke

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/source_vx_selector_trace_right_knee_rate_limited_4p3_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `fitted`
- fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
- dataset_id: `301851591b7988f1`
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
- train_rmse: `0.0320`
- train_mae: `0.0212`
- train_p95_abs_error: `0.0672`
- train_max_abs_error: `0.3316`
- pred_action_saturation_pct: `0.0036`
- sample_to_parameter_ratio: `2.8011`
- consecutive_pair_count: `3992`

### Exact Blend ONNX

- exported_onnx: `outputs/analysis/source_vx_selector_trace_rk_limited_4p3_blend080_exact_onnx_candidate/candidate.onnx`
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
| source_vx_selector_trace_right_knee_rate_limited_4p3_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0219 | 0.0696 | 0.3287 |
| source_vx_selector_trace_right_knee_rate_limited_4p3_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0215 | 0.0681 | 0.4159 |
| source_vx_selector_trace_right_knee_rate_limited_4p3_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0223 | 0.0700 | 0.3349 |
| source_vx_selector_trace_right_knee_rate_limited_4p3_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0224 | 0.0723 | 0.3411 |
| source_vx_selector_trace_right_knee_rate_limited_4p3_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0227 | 0.0748 | 0.3385 |
| source_vx_selector_trace_right_knee_rate_limited_4p3_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0248 | 0.0813 | 0.3431 |
| source_vx_selector_trace_right_knee_rate_limited_4p3_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0229 | 0.0749 | 0.3817 |
| source_vx_selector_trace_right_knee_rate_limited_4p3_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0224 | 0.0710 | 0.4396 |

## Closed-Loop Smoke

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `blend`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 500 | duration_complete | 0.0490 | 0.6123 | 0.1571 | 0.0973 | 0.1520 | 2.1727 | 0.1813 |
| seed_001 | 500 | duration_complete | 0.0462 | 0.5776 | 0.1670 | 0.0953 | 0.1556 | 2.2216 | 0.1821 |
| seed_002 | 500 | duration_complete | 0.0509 | 0.6365 | 0.1558 | 0.0994 | 0.1509 | 2.1485 | 0.1810 |
| seed_003 | 500 | duration_complete | 0.0426 | 0.5323 | 0.1538 | 0.1001 | 0.1549 | 2.1585 | 0.1805 |
| seed_004 | 500 | duration_complete | 0.0469 | 0.5860 | 0.1511 | 0.0993 | 0.1506 | 2.1733 | 0.1838 |
| seed_005 | 500 | duration_complete | 0.0513 | 0.6414 | 0.1621 | 0.1379 | 0.1462 | 2.0847 | 0.1822 |
| seed_006 | 500 | duration_complete | 0.0456 | 0.5702 | 0.1673 | 0.0976 | 0.1557 | 2.2159 | 0.1845 |
| seed_007 | 500 | duration_complete | 0.0468 | 0.5852 | 0.1629 | 0.1014 | 0.1559 | 2.2143 | 0.1824 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3343 | 8.6908 | 0.0000 |
| seed_001 | 0.3339 | 8.8866 | 0.0000 |
| seed_002 | 0.3342 | 8.5928 | 0.0000 |
| seed_003 | 0.3341 | 8.6338 | 0.0000 |
| seed_004 | 0.3346 | 8.6930 | 0.0000 |
| seed_005 | 0.3334 | 8.3390 | 0.0000 |
| seed_006 | 0.3341 | 8.8634 | 0.0000 |
| seed_007 | 0.3342 | 8.8570 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
