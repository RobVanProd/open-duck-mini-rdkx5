# Target Dataset BC Smoke

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/source_vx_selector_fitted_bridge_trace_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `fitted`
- fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
- dataset_id: `de4935ec7672ceea`
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
- train_rmse: `0.0326`
- train_mae: `0.0214`
- train_p95_abs_error: `0.0681`
- train_max_abs_error: `0.4096`
- pred_action_saturation_pct: `0.0036`
- sample_to_parameter_ratio: `2.8011`
- consecutive_pair_count: `3992`

### Exact Blend ONNX

- exported_onnx: `outputs/analysis/source_vx_selector_trace_blend080_exact_onnx_candidate/candidate.onnx`
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
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0221 | 0.0709 | 0.3287 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0218 | 0.0692 | 0.4159 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0225 | 0.0707 | 0.3349 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0226 | 0.0735 | 0.3411 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0229 | 0.0758 | 0.3679 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0249 | 0.0833 | 0.3431 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0231 | 0.0761 | 0.4804 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0227 | 0.0729 | 0.4396 |

## Closed-Loop Smoke

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `blend`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 500 | duration_complete | 0.0492 | 0.6153 | 0.1552 | 0.0973 | 0.1520 | 2.0779 | 0.1814 |
| seed_001 | 500 | duration_complete | 0.0457 | 0.5713 | 0.1688 | 0.0941 | 0.1556 | 2.2039 | 0.1832 |
| seed_002 | 500 | duration_complete | 0.0502 | 0.6274 | 0.1597 | 0.0980 | 0.1509 | 2.1459 | 0.1805 |
| seed_003 | 500 | duration_complete | 0.0414 | 0.5170 | 0.1573 | 0.1031 | 0.1549 | 2.1147 | 0.1803 |
| seed_004 | 500 | duration_complete | 0.0452 | 0.5651 | 0.1411 | 0.0950 | 0.1506 | 2.1169 | 0.1826 |
| seed_005 | 500 | duration_complete | 0.0502 | 0.6279 | 0.1575 | 0.1262 | 0.1462 | 2.0973 | 0.1828 |
| seed_006 | 500 | duration_complete | 0.0442 | 0.5529 | 0.1570 | 0.0958 | 0.1557 | 2.1649 | 0.1843 |
| seed_007 | 500 | duration_complete | 0.0472 | 0.5896 | 0.1614 | 0.0975 | 0.1559 | 2.2134 | 0.1842 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3341 | 8.3116 | 0.0000 |
| seed_001 | 0.3345 | 8.8155 | 0.0000 |
| seed_002 | 0.3344 | 8.5810 | 0.0000 |
| seed_003 | 0.3345 | 8.4590 | 0.0000 |
| seed_004 | 0.3351 | 8.4676 | 0.0000 |
| seed_005 | 0.3344 | 8.3891 | 0.0000 |
| seed_006 | 0.3345 | 8.6597 | 0.0000 |
| seed_007 | 0.3348 | 8.8536 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
