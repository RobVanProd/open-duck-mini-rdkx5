# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_TERMINATED`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/source_vx_selector_trace_dagger1_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `fitted`
- fit_json: `outputs/analysis/actuator_response_fit.json`
- dataset_id: `65eefb498dca9822`
- samples: `5166`
- entries: `16`
- source_files: `16`
- max_source_fraction: `0.0968`
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
- train_rmse: `0.0252`
- train_mae: `0.0177`
- train_p95_abs_error: `0.0516`
- train_max_abs_error: `0.2852`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `0.1647`
- consecutive_pair_count: `5150`

### MLP Settings

- hidden_sizes: `[128, 128]`
- steps: `4000`
- batch_size: `512`
- learning_rate: `0.001`
- pair_count: `5150`
- target_rate_scale: `0.0`
- target_rate_limit_rad_s: `3.75`
- obs_noise_std: `0.0`
- obs_consistency_scale: `0.0`

| step | loss |
|---:|---:|
| 1 | 0.544061 |
| 400 | 0.002885 |
| 800 | 0.001675 |
| 1200 | 0.001370 |
| 1600 | 0.001064 |
| 2000 | 0.000956 |
| 2400 | 0.000827 |
| 2800 | 0.000769 |
| 3200 | 0.000691 |
| 3600 | 0.000726 |
| 4000 | 0.000617 |

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4666 | 500 | 0.0248 | 0.0738 | 0.4054 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4666 | 500 | 0.0249 | 0.0784 | 0.3227 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4666 | 500 | 0.0253 | 0.0765 | 0.2423 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4666 | 500 | 0.0260 | 0.0809 | 0.2910 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4666 | 500 | 0.0260 | 0.0822 | 0.3197 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4666 | 500 | 0.0276 | 0.0883 | 0.3430 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4666 | 500 | 0.0262 | 0.0830 | 0.2961 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4666 | 500 | 0.0252 | 0.0798 | 0.2746 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5004 | 162 | 0.0580 | 0.1629 | 0.4046 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4874 | 292 | 0.0573 | 0.1661 | 0.5655 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5073 | 93 | 0.0505 | 0.1538 | 0.4026 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 4935 | 231 | 0.0592 | 0.1717 | 0.4064 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5064 | 102 | 0.0529 | 0.1456 | 0.4155 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5087 | 79 | 0.0632 | 0.1819 | 0.5634 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5049 | 117 | 0.0522 | 0.1517 | 0.4526 |
| source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 5076 | 90 | 0.0559 | 0.1574 | 0.3534 |

## Closed-Loop Smoke

status: `HOLD_BC_REPLAY_TERMINATED`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `mlp`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 500 | duration_complete | 0.0503 | 0.6291 | 0.1505 | 0.0933 | 0.1520 | 2.1240 | 0.1823 |
| seed_001 | 500 | duration_complete | 0.0463 | 0.5783 | 0.1626 | 0.0953 | 0.1556 | 2.1036 | 0.1824 |
| seed_002 | 500 | duration_complete | 0.0521 | 0.6506 | 0.1538 | 0.0985 | 0.1509 | 2.1206 | 0.1840 |
| seed_003 | 500 | duration_complete | 0.0459 | 0.5743 | 0.1487 | 0.0997 | 0.1557 | 2.0691 | 0.1801 |
| seed_004 | 500 | duration_complete | 0.0487 | 0.6085 | 0.1501 | 0.1015 | 0.1506 | 2.1186 | 0.1838 |
| seed_005 | 102 | fall_or_progress_failure | -0.1535 | -1.9188 | 0.1522 | 1.1071 | 0.0487 | 1.8427 | 0.1708 |
| seed_006 | 500 | duration_complete | 0.0445 | 0.5566 | 0.1609 | 0.0992 | 0.1557 | 2.0850 | 0.1833 |
| seed_007 | 500 | duration_complete | 0.0477 | 0.5960 | 0.1614 | 0.0963 | 0.1559 | 2.1257 | 0.1808 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3343 | 8.4906 | 0.0000 |
| seed_001 | 0.3351 | 8.4145 | 0.0000 |
| seed_002 | 0.3349 | 8.4826 | 0.0000 |
| seed_003 | 0.3327 | 8.2763 | 0.0000 |
| seed_004 | 0.3356 | 8.4744 | 0.0000 |
| seed_005 | 0.3271 | 7.3708 | 0.0000 |
| seed_006 | 0.3353 | 8.3402 | 0.0000 |
| seed_007 | 0.3346 | 8.5028 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
