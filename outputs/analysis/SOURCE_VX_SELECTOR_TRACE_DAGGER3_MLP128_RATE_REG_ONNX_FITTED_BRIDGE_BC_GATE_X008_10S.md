# Target Dataset BC Smoke

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/source_vx_selector_trace_dagger3_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `fitted`
- fit_json: `outputs/analysis/actuator_response_fit.json`
- dataset_id: `80ea809b021b6b9a`
- samples: `9268`
- entries: `25`
- source_files: `25`
- max_source_fraction: `0.0539`
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
- train_rmse: `0.0256`
- train_mae: `0.0169`
- train_p95_abs_error: `0.0518`
- train_max_abs_error: `0.2948`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `0.2954`
- consecutive_pair_count: `9243`

### MLP Settings

- hidden_sizes: `[128, 128]`
- steps: `5000`
- batch_size: `512`
- learning_rate: `0.001`
- pair_count: `9243`
- target_rate_scale: `0.1`
- target_rate_limit_rad_s: `3.75`
- obs_noise_std: `0.0`
- obs_consistency_scale: `0.0`
- saved_npz: `outputs/analysis/source_vx_selector_trace_dagger3_mlp128_rate_reg_candidate/candidate_mlp.npz`
- exported_onnx: `outputs/analysis/source_vx_selector_trace_dagger3_mlp128_rate_reg_candidate/candidate.onnx`
- onnx_verify_max_abs_error: `0.0000`

| step | loss |
|---:|---:|
| 1 | 1.095397 |
| 500 | 0.003022 |
| 1000 | 0.001720 |
| 1500 | 0.001167 |
| 2000 | 0.001069 |
| 2500 | 0.000893 |
| 3000 | 0.000832 |
| 3500 | 0.000864 |
| 4000 | 0.000703 |
| 4500 | 0.000671 |
| 5000 | 0.000591 |

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0240 | 0.0738 | 0.4041 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0241 | 0.0757 | 0.3275 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0246 | 0.0769 | 0.2525 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0253 | 0.0790 | 0.2600 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0250 | 0.0787 | 0.3160 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0267 | 0.0868 | 0.3604 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0254 | 0.0805 | 0.2689 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0242 | 0.0760 | 0.2721 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0185 | 0.0547 | 0.2306 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0182 | 0.0559 | 0.1973 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0184 | 0.0548 | 0.2251 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0206 | 0.0611 | 0.2092 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0189 | 0.0562 | 0.2320 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9166 | 102 | 0.0440 | 0.1244 | 0.3941 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0190 | 0.0553 | 0.2004 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0188 | 0.0557 | 0.2609 |
| source_vx_selector_trace_dagger2_rate_reg_standard_relabel_blend_x008_10s_traces/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8768 | 500 | 0.0195 | 0.0570 | 0.1643 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9106 | 162 | 0.0590 | 0.1678 | 0.4249 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 8976 | 292 | 0.0593 | 0.1702 | 0.5548 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9175 | 93 | 0.0522 | 0.1570 | 0.4656 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9037 | 231 | 0.0612 | 0.1770 | 0.4411 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9166 | 102 | 0.0542 | 0.1521 | 0.4219 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9189 | 79 | 0.0634 | 0.1862 | 0.5712 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9151 | 117 | 0.0535 | 0.1560 | 0.4483 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9178 | 90 | 0.0572 | 0.1686 | 0.3750 |

## Closed-Loop Smoke

status: `PASS_BC_FIT_SMOKE_FORWARD_REPLAY`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `mlp`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 500 | duration_complete | 0.0462 | 0.5775 | 0.1384 | 0.0975 | 0.1520 | 2.1480 | 0.1854 |
| seed_001 | 500 | duration_complete | 0.0412 | 0.5156 | 0.1562 | 0.1012 | 0.1556 | 2.2029 | 0.1862 |
| seed_002 | 500 | duration_complete | 0.0471 | 0.5893 | 0.1443 | 0.1020 | 0.1509 | 2.1998 | 0.1852 |
| seed_003 | 500 | duration_complete | 0.0396 | 0.4945 | 0.1325 | 0.1021 | 0.1555 | 2.2081 | 0.1858 |
| seed_004 | 500 | duration_complete | 0.0442 | 0.5522 | 0.1360 | 0.0981 | 0.1506 | 2.1881 | 0.1868 |
| seed_005 | 500 | duration_complete | 0.0320 | 0.3999 | 0.1322 | 0.1787 | 0.1462 | 2.1186 | 0.1857 |
| seed_006 | 500 | duration_complete | 0.0413 | 0.5163 | 0.1481 | 0.0977 | 0.1557 | 2.2015 | 0.1850 |
| seed_007 | 500 | duration_complete | 0.0436 | 0.5448 | 0.1479 | 0.0994 | 0.1559 | 2.2193 | 0.1858 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3350 | 8.5920 | 0.0000 |
| seed_001 | 0.3353 | 8.8116 | 0.0000 |
| seed_002 | 0.3351 | 8.7990 | 0.0000 |
| seed_003 | 0.3348 | 8.8323 | 0.0000 |
| seed_004 | 0.3355 | 8.7523 | 0.0000 |
| seed_005 | 0.3351 | 8.4742 | 0.0000 |
| seed_006 | 0.3351 | 8.8061 | 0.0000 |
| seed_007 | 0.3352 | 8.8770 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
