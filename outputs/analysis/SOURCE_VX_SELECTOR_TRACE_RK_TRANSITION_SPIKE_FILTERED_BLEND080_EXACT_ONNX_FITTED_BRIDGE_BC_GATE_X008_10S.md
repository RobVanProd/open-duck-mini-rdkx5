# Target Dataset BC Smoke

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/source_vx_selector_trace_rk_transition_spike_filtered_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `fitted`
- fit_json: `outputs/analysis/actuator_response_fit.json`
- dataset_id: `69c1466221e946cc`
- samples: `3124`
- entries: `8`
- source_files: `8`
- max_source_fraction: `0.1271`
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
- train_mae: `0.0217`
- train_p95_abs_error: `0.0695`
- train_max_abs_error: `0.3168`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `2.1877`
- consecutive_pair_count: `2883`

### Exact Blend ONNX

- exported_onnx: `outputs/analysis/source_vx_selector_trace_rk_transition_spike_filtered_blend080_exact_onnx_candidate/candidate.onnx`
- input_name: `obs`
- output_name: `continuous_actions`
- knn_samples: `3124`
- knn_k: `5`
- blend_alpha: `0.8`
- onnx_verify_samples_checked: `32`
- onnx_verify_max_abs_error: `0.00000012`
- onnx_verify_p95_abs_error: `0.00000006`

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 2732 | 392 | 0.0230 | 0.0751 | 0.3617 |
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 2737 | 387 | 0.0228 | 0.0717 | 0.3768 |
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 2729 | 395 | 0.0230 | 0.0717 | 0.3752 |
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 2736 | 388 | 0.0234 | 0.0776 | 0.3350 |
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 2731 | 393 | 0.0229 | 0.0748 | 0.2512 |
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 2738 | 386 | 0.0260 | 0.0866 | 0.3964 |
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 2738 | 386 | 0.0240 | 0.0788 | 0.4726 |
| source_vx_selector_trace_rk_transition_spike_filtered_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 2727 | 397 | 0.0235 | 0.0758 | 0.3994 |

## Closed-Loop Smoke

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `blend`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 500 | duration_complete | 0.0473 | 0.5913 | 0.1520 | 0.0979 | 0.1520 | 2.1574 | 0.1832 |
| seed_001 | 500 | duration_complete | 0.0428 | 0.5346 | 0.1658 | 0.0963 | 0.1556 | 2.1318 | 0.1839 |
| seed_002 | 500 | duration_complete | 0.0495 | 0.6188 | 0.1562 | 0.0966 | 0.1509 | 2.1257 | 0.1814 |
| seed_003 | 500 | duration_complete | 0.0385 | 0.4806 | 0.1457 | 0.0997 | 0.1545 | 2.1790 | 0.1833 |
| seed_004 | 500 | duration_complete | 0.0481 | 0.6011 | 0.1592 | 0.0971 | 0.1506 | 2.1790 | 0.1838 |
| seed_005 | 500 | duration_complete | 0.0463 | 0.5786 | 0.1588 | 0.1550 | 0.1462 | 2.0712 | 0.1819 |
| seed_006 | 500 | duration_complete | 0.0426 | 0.5328 | 0.1604 | 0.0969 | 0.1557 | 2.1366 | 0.1853 |
| seed_007 | 500 | duration_complete | 0.0450 | 0.5622 | 0.1592 | 0.0956 | 0.1559 | 2.1268 | 0.1837 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3338 | 8.6048 | 0.0000 |
| seed_001 | 0.3338 | 8.5272 | 0.0000 |
| seed_002 | 0.3339 | 8.5026 | 0.0000 |
| seed_003 | 0.3337 | 8.7161 | 0.0000 |
| seed_004 | 0.3338 | 8.7162 | 0.0000 |
| seed_005 | 0.3338 | 8.2847 | 0.0000 |
| seed_006 | 0.3336 | 8.5465 | 0.0000 |
| seed_007 | 0.3341 | 8.5071 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
