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
- train_rmse: `0.0227`
- train_mae: `0.0156`
- train_p95_abs_error: `0.0434`
- train_max_abs_error: `0.2904`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `0.0425`
- consecutive_pair_count: `9243`

### MLP Settings

- hidden_sizes: `[512, 256, 128]`
- steps: `5000`
- batch_size: `512`
- learning_rate: `0.001`
- pair_count: `9243`
- target_rate_scale: `0.1`
- target_rate_limit_rad_s: `3.75`
- obs_noise_std: `0.0`
- obs_consistency_scale: `0.0`
- saved_npz: `outputs/analysis/source_vx_selector_trace_dagger3_mlp512_256_128_rate_reg_candidate/candidate_mlp.npz`
- exported_onnx: `outputs/analysis/source_vx_selector_trace_dagger3_mlp512_256_128_rate_reg_candidate/candidate.onnx`
- onnx_verify_max_abs_error: `0.0000`

| step | loss |
|---:|---:|
| 1 | 0.661191 |
| 500 | 0.001438 |
| 1000 | 0.001047 |
| 1500 | 0.000804 |
| 2000 | 0.000698 |
| 2500 | 0.000669 |
| 3000 | 0.000664 |
| 3500 | 0.000609 |
| 4000 | 0.000561 |
| 4500 | 0.000568 |
| 5000 | 0.000497 |

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
| seed_000 | 500 | duration_complete | 0.0442 | 0.5530 | 0.1425 | 0.0979 | 0.1520 | 2.2122 | 0.1852 |
| seed_001 | 500 | duration_complete | 0.0385 | 0.4808 | 0.1452 | 0.0933 | 0.1556 | 2.2145 | 0.1841 |
| seed_002 | 500 | duration_complete | 0.0437 | 0.5461 | 0.1377 | 0.1020 | 0.1509 | 2.2056 | 0.1837 |
| seed_003 | 500 | duration_complete | 0.0341 | 0.4257 | 0.1275 | 0.1031 | 0.1553 | 2.2007 | 0.1828 |
| seed_004 | 500 | duration_complete | 0.0387 | 0.4842 | 0.1309 | 0.0959 | 0.1506 | 2.1929 | 0.1844 |
| seed_005 | 500 | duration_complete | 0.0430 | 0.5370 | 0.1393 | 0.1149 | 0.1461 | 2.2117 | 0.1866 |
| seed_006 | 500 | duration_complete | 0.0362 | 0.4528 | 0.1452 | 0.0942 | 0.1557 | 2.2436 | 0.1844 |
| seed_007 | 500 | duration_complete | 0.0380 | 0.4754 | 0.1403 | 0.0960 | 0.1559 | 2.2272 | 0.1842 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3331 | 8.8488 | 0.0000 |
| seed_001 | 0.3332 | 8.8579 | 0.0000 |
| seed_002 | 0.3332 | 8.8226 | 0.0000 |
| seed_003 | 0.3330 | 8.8026 | 0.0000 |
| seed_004 | 0.3339 | 8.7716 | 0.0000 |
| seed_005 | 0.3337 | 8.8296 | 0.0000 |
| seed_006 | 0.3334 | 8.9742 | 0.0000 |
| seed_007 | 0.3334 | 8.9088 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
