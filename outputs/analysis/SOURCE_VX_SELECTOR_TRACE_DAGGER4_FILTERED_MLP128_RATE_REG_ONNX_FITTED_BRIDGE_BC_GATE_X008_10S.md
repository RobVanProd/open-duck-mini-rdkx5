# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_TERMINATED`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/filtered_source_vx_selector_dagger4_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `fitted`
- fit_json: `outputs/analysis/actuator_response_fit.json`
- dataset_id: `3c574b376101bd3f`
- samples: `9500`
- entries: `19`
- source_files: `19`
- max_source_fraction: `0.0526`
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
- best_alpha: `0.01`
- train_rmse: `0.0234`
- train_mae: `0.0153`
- train_p95_abs_error: `0.0462`
- train_max_abs_error: `0.2664`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `0.3028`
- consecutive_pair_count: `9481`

### MLP Settings

- hidden_sizes: `[128, 128]`
- steps: `5000`
- batch_size: `512`
- learning_rate: `0.001`
- pair_count: `9481`
- target_rate_scale: `0.1`
- target_rate_limit_rad_s: `3.75`
- obs_noise_std: `0.0`
- obs_consistency_scale: `0.0`
- saved_npz: `outputs/analysis/source_vx_selector_trace_dagger4_filtered_mlp128_rate_reg_candidate/candidate_mlp.npz`
- exported_onnx: `outputs/analysis/source_vx_selector_trace_dagger4_filtered_mlp128_rate_reg_candidate/candidate.onnx`
- onnx_verify_max_abs_error: `0.0000`

| step | loss |
|---:|---:|
| 1 | 0.948897 |
| 500 | 0.001814 |
| 1000 | 0.001214 |
| 1500 | 0.000911 |
| 2000 | 0.000756 |
| 2500 | 0.000644 |
| 3000 | 0.000725 |
| 3500 | 0.000574 |
| 4000 | 0.000596 |
| 4500 | 0.000568 |
| 5000 | 0.000565 |

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_008.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0235 | 0.0747 | 0.3185 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_010.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0230 | 0.0720 | 0.2578 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_011.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0231 | 0.0740 | 0.3324 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0223 | 0.0707 | 0.2863 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0222 | 0.0701 | 0.3839 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0226 | 0.0693 | 0.3384 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0227 | 0.0720 | 0.2487 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0226 | 0.0726 | 0.3870 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0249 | 0.0816 | 0.3457 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0231 | 0.0743 | 0.4347 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0219 | 0.0690 | 0.2798 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0174 | 0.0515 | 0.2169 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0165 | 0.0486 | 0.2410 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0169 | 0.0493 | 0.1790 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0188 | 0.0539 | 0.2108 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0172 | 0.0510 | 0.2003 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0172 | 0.0489 | 0.1867 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0170 | 0.0506 | 0.2037 |
| source_vx_selector_trace_dagger2_rate_reg_standard_relabel_blend_x008_10s_traces/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 9000 | 500 | 0.0201 | 0.0573 | 0.1779 |

## Closed-Loop Smoke

status: `HOLD_BC_REPLAY_TERMINATED`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `mlp`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 500 | duration_complete | 0.0009 | 0.0108 | 0.0220 | 0.0148 | 0.1536 | 0.4611 | 0.0473 |
| seed_001 | 33 | fall_or_progress_failure | 0.0210 | 0.2630 | 1.1572 | 0.1864 | 0.0769 | 2.2112 | 0.1112 |
| seed_002 | 500 | duration_complete | 0.0318 | 0.3974 | 0.1094 | 0.0526 | 0.1525 | 2.1749 | 0.1850 |
| seed_003 | 500 | duration_complete | 0.0206 | 0.2577 | 0.1094 | 0.0566 | 0.1584 | 2.0427 | 0.1727 |
| seed_004 | 500 | duration_complete | 0.0269 | 0.3366 | 0.1028 | 0.0585 | 0.1515 | 2.1451 | 0.1851 |
| seed_005 | 500 | duration_complete | 0.0305 | 0.3809 | 0.1073 | 0.1412 | 0.1468 | 2.1443 | 0.1847 |
| seed_006 | 500 | duration_complete | 0.0213 | 0.2658 | 0.0985 | 0.0567 | 0.1586 | 2.1416 | 0.1847 |
| seed_007 | 34 | fall_or_progress_failure | 0.0143 | 0.1794 | 1.1147 | 0.0326 | 0.0859 | 2.0115 | 0.1697 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.2626 | 1.8435 | 0.0000 |
| seed_001 | 0.2834 | 8.8447 | 0.0000 |
| seed_002 | 0.3339 | 8.6996 | 0.0000 |
| seed_003 | 0.3270 | 8.1707 | 0.0000 |
| seed_004 | 0.3341 | 8.5805 | 0.0000 |
| seed_005 | 0.3332 | 8.5888 | 0.0000 |
| seed_006 | 0.3336 | 8.5664 | 0.0000 |
| seed_007 | 0.2825 | 8.0460 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
