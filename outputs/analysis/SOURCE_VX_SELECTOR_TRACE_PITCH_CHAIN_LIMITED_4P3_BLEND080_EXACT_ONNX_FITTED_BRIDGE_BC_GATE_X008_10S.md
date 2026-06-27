# Target Dataset BC Smoke

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `fitted`
- fit_json: `outputs/analysis/actuator_response_fit.json`
- dataset_id: `3aedbacc4a592fc8`
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
- train_p95_abs_error: `0.0671`
- train_max_abs_error: `0.3316`
- pred_action_saturation_pct: `0.0036`
- sample_to_parameter_ratio: `2.8011`
- consecutive_pair_count: `3992`

### Exact Blend ONNX

- exported_onnx: `outputs/analysis/source_vx_selector_trace_pitch_chain_limited_4p3_blend080_exact_onnx_candidate/candidate.onnx`
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
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0219 | 0.0700 | 0.3102 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0215 | 0.0682 | 0.4159 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0222 | 0.0699 | 0.3356 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0224 | 0.0728 | 0.3411 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0226 | 0.0742 | 0.3385 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0247 | 0.0811 | 0.3431 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0229 | 0.0743 | 0.3871 |
| source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0223 | 0.0709 | 0.4396 |

## Closed-Loop Smoke

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `blend`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 500 | duration_complete | 0.0505 | 0.6311 | 0.1566 | 0.0971 | 0.1520 | 2.1444 | 0.1821 |
| seed_001 | 500 | duration_complete | 0.0463 | 0.5789 | 0.1722 | 0.0965 | 0.1556 | 2.2237 | 0.1837 |
| seed_002 | 500 | duration_complete | 0.0522 | 0.6531 | 0.1584 | 0.0980 | 0.1509 | 2.1754 | 0.1825 |
| seed_003 | 500 | duration_complete | 0.0430 | 0.5380 | 0.1567 | 0.1036 | 0.1549 | 2.1730 | 0.1820 |
| seed_004 | 500 | duration_complete | 0.0491 | 0.6138 | 0.1501 | 0.0995 | 0.1506 | 2.1444 | 0.1834 |
| seed_005 | 500 | duration_complete | 0.0519 | 0.6482 | 0.1561 | 0.1249 | 0.1462 | 2.1226 | 0.1818 |
| seed_006 | 500 | duration_complete | 0.0444 | 0.5554 | 0.1634 | 0.0983 | 0.1557 | 2.1939 | 0.1835 |
| seed_007 | 500 | duration_complete | 0.0462 | 0.5774 | 0.1568 | 0.0997 | 0.1559 | 2.1946 | 0.1838 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3342 | 8.5776 | 0.0000 |
| seed_001 | 0.3338 | 8.8949 | 0.0000 |
| seed_002 | 0.3342 | 8.7001 | 0.0000 |
| seed_003 | 0.3341 | 8.6919 | 0.0000 |
| seed_004 | 0.3345 | 8.5776 | 0.0000 |
| seed_005 | 0.3338 | 8.4903 | 0.0000 |
| seed_006 | 0.3344 | 8.7756 | 0.0000 |
| seed_007 | 0.3343 | 8.7784 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
