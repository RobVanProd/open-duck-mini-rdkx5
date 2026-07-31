# Target Dataset BC Smoke

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/source_vx_selector_trace_dagger2_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `fitted`
- fit_json: `outputs/analysis/actuator_response_fit.json`
- dataset_id: `29210cfbb880ecb9`
- samples: `8768`
- entries: `24`
- source_files: `24`
- max_source_fraction: `0.0570`
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
- best_alpha: `1e-06`
- train_rmse: `0.0228`
- train_mae: `0.0157`
- train_p95_abs_error: `0.0467`
- train_max_abs_error: `0.2781`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `0.2795`
- consecutive_pair_count: `8744`

### MLP Settings

- hidden_sizes: `[128, 128]`
- steps: `5000`
- batch_size: `512`
- learning_rate: `0.001`
- pair_count: `8744`
- target_rate_scale: `0.0`
- target_rate_limit_rad_s: `3.75`
- obs_noise_std: `0.0`
- obs_consistency_scale: `0.0`

| step | loss |
|---:|---:|
| 1 | 0.544255 |
| 500 | 0.002611 |
| 1000 | 0.001316 |
| 1500 | 0.000880 |
| 2000 | 0.000832 |
| 2500 | 0.000731 |
| 3000 | 0.000641 |
| 3500 | 0.000709 |
| 4000 | 0.000534 |
| 4500 | 0.000534 |
| 5000 | 0.000489 |

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8268 | 500 | 0.0241 | 0.0736 | 0.4018 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8268 | 500 | 0.0241 | 0.0757 | 0.3247 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8268 | 500 | 0.0246 | 0.0771 | 0.2512 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8268 | 500 | 0.0253 | 0.0798 | 0.2595 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8268 | 500 | 0.0251 | 0.0788 | 0.3160 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8268 | 500 | 0.0267 | 0.0866 | 0.3591 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8268 | 500 | 0.0254 | 0.0810 | 0.2669 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8268 | 500 | 0.0244 | 0.0767 | 0.2706 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8268 | 500 | 0.0186 | 0.0550 | 0.2324 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8268 | 500 | 0.0183 | 0.0566 | 0.1985 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8268 | 500 | 0.0185 | 0.0549 | 0.2269 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8268 | 500 | 0.0207 | 0.0610 | 0.2093 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8268 | 500 | 0.0190 | 0.0561 | 0.2253 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8666 | 102 | 0.0438 | 0.1241 | 0.3946 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8268 | 500 | 0.0190 | 0.0552 | 0.2015 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8268 | 500 | 0.0189 | 0.0560 | 0.2626 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8606 | 162 | 0.0589 | 0.1674 | 0.4188 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8476 | 292 | 0.0591 | 0.1696 | 0.5548 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8675 | 93 | 0.0521 | 0.1573 | 0.4631 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8537 | 231 | 0.0611 | 0.1767 | 0.4387 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8666 | 102 | 0.0541 | 0.1515 | 0.4194 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8689 | 79 | 0.0632 | 0.1855 | 0.5681 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8651 | 117 | 0.0533 | 0.1556 | 0.4486 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8678 | 90 | 0.0576 | 0.1697 | 0.3757 |

## Closed-Loop Smoke

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `mlp`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 500 | duration_complete | 0.0483 | 0.6037 | 0.1596 | 0.1029 | 0.1520 | 2.1400 | 0.1797 |
| seed_001 | 500 | duration_complete | 0.0429 | 0.5362 | 0.1660 | 0.1007 | 0.1556 | 2.1570 | 0.1801 |
| seed_002 | 500 | duration_complete | 0.0495 | 0.6182 | 0.1513 | 0.1022 | 0.1509 | 2.1382 | 0.1783 |
| seed_003 | 500 | duration_complete | 0.0422 | 0.5276 | 0.1537 | 0.1062 | 0.1552 | 2.1341 | 0.1770 |
| seed_004 | 500 | duration_complete | 0.0463 | 0.5789 | 0.1559 | 0.1025 | 0.1506 | 2.1601 | 0.1789 |
| seed_005 | 500 | duration_complete | 0.0484 | 0.6052 | 0.1536 | 0.1223 | 0.1462 | 2.1536 | 0.1813 |
| seed_006 | 500 | duration_complete | 0.0417 | 0.5208 | 0.1607 | 0.1006 | 0.1557 | 2.1174 | 0.1807 |
| seed_007 | 500 | duration_complete | 0.0444 | 0.5549 | 0.1562 | 0.1019 | 0.1559 | 2.1413 | 0.1782 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3345 | 8.5601 | 0.0000 |
| seed_001 | 0.3346 | 8.6279 | 0.0000 |
| seed_002 | 0.3346 | 8.5528 | 0.0000 |
| seed_003 | 0.3343 | 8.5366 | 0.0000 |
| seed_004 | 0.3348 | 8.6405 | 0.0000 |
| seed_005 | 0.3348 | 8.6050 | 0.0000 |
| seed_006 | 0.3345 | 8.4698 | 0.0000 |
| seed_007 | 0.3343 | 8.5651 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
