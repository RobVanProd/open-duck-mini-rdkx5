# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_TERMINATED`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/source_vx_selector_trace_right_knee_rate_limited_4p0_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `fitted`
- fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
- dataset_id: `18356a4d75aabe60`
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
- train_rmse: `0.0319`
- train_mae: `0.0211`
- train_p95_abs_error: `0.0669`
- train_max_abs_error: `0.3235`
- pred_action_saturation_pct: `0.0036`
- sample_to_parameter_ratio: `2.8011`
- consecutive_pair_count: `3992`

### Exact Blend ONNX

- exported_onnx: `outputs/analysis/source_vx_selector_trace_rk_limited_4p0_blend080_exact_onnx_candidate/candidate.onnx`
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
| source_vx_selector_trace_right_knee_rate_limited_4p0_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0218 | 0.0691 | 0.3287 |
| source_vx_selector_trace_right_knee_rate_limited_4p0_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0215 | 0.0679 | 0.4159 |
| source_vx_selector_trace_right_knee_rate_limited_4p0_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0222 | 0.0693 | 0.3349 |
| source_vx_selector_trace_right_knee_rate_limited_4p0_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0224 | 0.0723 | 0.3411 |
| source_vx_selector_trace_right_knee_rate_limited_4p0_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0226 | 0.0748 | 0.3035 |
| source_vx_selector_trace_right_knee_rate_limited_4p0_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0247 | 0.0813 | 0.3431 |
| source_vx_selector_trace_right_knee_rate_limited_4p0_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0229 | 0.0747 | 0.3817 |
| source_vx_selector_trace_right_knee_rate_limited_4p0_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 3500 | 500 | 0.0223 | 0.0706 | 0.4396 |

## Closed-Loop Smoke

status: `HOLD_BC_REPLAY_TERMINATED`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `blend`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 500 | duration_complete | 0.0501 | 0.6263 | 0.1599 | 0.1032 | 0.1520 | 2.1082 | 0.1811 |
| seed_001 | 500 | duration_complete | 0.0468 | 0.5851 | 0.1640 | 0.0980 | 0.1556 | 2.2236 | 0.1841 |
| seed_002 | 500 | duration_complete | 0.0501 | 0.6264 | 0.1626 | 0.0992 | 0.1509 | 2.1886 | 0.1812 |
| seed_003 | 500 | duration_complete | 0.0432 | 0.5403 | 0.1580 | 0.1024 | 0.1549 | 2.1283 | 0.1811 |
| seed_004 | 500 | duration_complete | 0.0501 | 0.6266 | 0.1630 | 0.0979 | 0.1506 | 2.1481 | 0.1830 |
| seed_005 | 64 | fall_or_progress_failure | -0.2199 | -2.7489 | 0.1732 | 1.1876 | 0.0787 | 1.6047 | 0.1649 |
| seed_006 | 500 | duration_complete | 0.0460 | 0.5751 | 0.1592 | 0.0978 | 0.1557 | 2.1993 | 0.1832 |
| seed_007 | 500 | duration_complete | 0.0480 | 0.6003 | 0.1692 | 0.0988 | 0.1559 | 2.2064 | 0.1832 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3336 | 8.4329 | 0.0000 |
| seed_001 | 0.3339 | 8.8943 | 0.0000 |
| seed_002 | 0.3339 | 8.7502 | 0.0000 |
| seed_003 | 0.3341 | 8.5133 | 0.0000 |
| seed_004 | 0.3341 | 8.5924 | 0.0000 |
| seed_005 | 0.3284 | 6.3814 | 0.0000 |
| seed_006 | 0.3334 | 8.7974 | 0.0000 |
| seed_007 | 0.3339 | 8.8255 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
