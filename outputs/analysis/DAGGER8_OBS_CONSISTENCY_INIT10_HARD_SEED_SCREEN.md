# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_TERMINATED`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/filtered_source_vx_selector_dagger7_targeted_recovery_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `fitted`
- fit_json: `outputs/analysis/actuator_response_fit.json`
- dataset_id: `181a3a616e02ad16`
- samples: `22778`
- entries: `143`
- source_files: `35`
- max_source_fraction: `0.0731`
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
- best_alpha: `1.0`
- train_rmse: `0.0268`
- train_mae: `0.0177`
- train_p95_abs_error: `0.0541`
- train_max_abs_error: `0.3316`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `0.7260`
- consecutive_pair_count: `16529`

### MLP Settings

- hidden_sizes: `[128, 128]`
- steps: `5000`
- batch_size: `512`
- learning_rate: `0.001`
- pair_count: `16529`
- target_rate_scale: `0.1`
- target_rate_limit_rad_s: `3.75`
- obs_noise_std: `0.02`
- obs_consistency_scale: `0.1`
- saved_npz: `None`
- exported_onnx: `None`
- onnx_verify_max_abs_error: `NA`

| step | loss |
|---:|---:|
| 1 | 1.050452 |
| 500 | 0.002413 |
| 1000 | 0.001521 |
| 1500 | 0.001081 |
| 2000 | 0.001050 |
| 2500 | 0.000792 |
| 3000 | 0.000868 |
| 3500 | 0.000918 |
| 4000 | 0.000689 |
| 4500 | 0.000665 |
| 5000 | 0.000740 |

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 21778 | 1000 | 0.0323 | 0.0995 | 0.4599 |
| seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 21164 | 1614 | 0.0654 | 0.1837 | 0.6954 |
| seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 21778 | 1000 | 0.0309 | 0.0952 | 0.3227 |
| seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 21778 | 1000 | 0.0299 | 0.0919 | 0.3689 |
| seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 21778 | 1000 | 0.0308 | 0.0956 | 0.3977 |
| seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 21778 | 1000 | 0.0305 | 0.0950 | 0.3192 |
| seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 21778 | 1000 | 0.0300 | 0.0904 | 0.3049 |
| seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 21114 | 1664 | 0.0620 | 0.1602 | 0.8029 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_016.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0249 | 0.0763 | 0.4358 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_017.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0246 | 0.0773 | 0.4004 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_018.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0248 | 0.0767 | 0.2887 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_022.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0253 | 0.0789 | 0.3371 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_024.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0261 | 0.0825 | 0.2514 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_027.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0265 | 0.0827 | 0.5135 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_029.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0252 | 0.0796 | 0.3670 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_031.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0245 | 0.0796 | 0.3617 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_008.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0245 | 0.0755 | 0.3761 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_010.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0243 | 0.0743 | 0.2597 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_011.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0248 | 0.0759 | 0.3599 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0256 | 0.0786 | 0.2838 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0253 | 0.0770 | 0.3019 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0261 | 0.0791 | 0.3020 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0265 | 0.0826 | 0.2465 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0261 | 0.0802 | 0.3613 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0281 | 0.0888 | 0.3941 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0265 | 0.0831 | 0.3833 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0250 | 0.0762 | 0.3370 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0203 | 0.0597 | 0.2132 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0197 | 0.0582 | 0.2828 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0205 | 0.0597 | 0.2509 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0227 | 0.0649 | 0.2202 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0206 | 0.0605 | 0.2242 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0209 | 0.0611 | 0.2206 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0203 | 0.0589 | 0.2153 |
| source_vx_selector_trace_dagger2_rate_reg_standard_relabel_blend_x008_10s_traces/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 22278 | 500 | 0.0228 | 0.0638 | 0.2150 |

## Closed-Loop Smoke

status: `HOLD_BC_REPLAY_TERMINATED`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `mlp`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_001 | 32 | fall_or_progress_failure | 0.0133 | 0.1667 | 1.2096 | 0.1622 | 0.0813 | 2.2257 | 0.1657 |
| seed_007 | 33 | fall_or_progress_failure | 0.0144 | 0.1795 | 1.2194 | 0.0667 | 0.0702 | 2.2719 | 0.1361 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_001 | 0.3151 | 8.8176 | 0.0000 |
| seed_007 | 0.2959 | 9.0877 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
