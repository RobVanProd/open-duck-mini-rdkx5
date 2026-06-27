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
- train_rmse: `0.0269`
- train_mae: `0.0175`
- train_p95_abs_error: `0.0539`
- train_max_abs_error: `0.3612`
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
- obs_noise_std: `0.0`
- obs_consistency_scale: `0.0`
- saved_npz: `outputs/analysis/source_vx_selector_trace_dagger7_targeted_recovery_mlp128_rate_reg_candidate/candidate_mlp.npz`
- exported_onnx: `outputs/analysis/source_vx_selector_trace_dagger7_targeted_recovery_mlp128_rate_reg_candidate/candidate.onnx`
- onnx_verify_max_abs_error: `0.0000`

| step | loss |
|---:|---:|
| 1 | 0.902024 |
| 500 | 0.002379 |
| 1000 | 0.001443 |
| 1500 | 0.001229 |
| 2000 | 0.001052 |
| 2500 | 0.000978 |
| 3000 | 0.000814 |
| 3500 | 0.000788 |
| 4000 | 0.000780 |
| 4500 | 0.000781 |
| 5000 | 0.000669 |

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
| seed_000 | 500 | duration_complete | 0.0268 | 0.3350 | 0.1089 | 0.0554 | 0.1536 | 2.2407 | 0.1796 |
| seed_001 | 32 | fall_or_progress_failure | 0.0109 | 0.1358 | 1.1716 | 0.1767 | 0.0871 | 2.3473 | 0.1709 |
| seed_002 | 500 | duration_complete | 0.0303 | 0.3792 | 0.1115 | 0.0609 | 0.1525 | 2.2717 | 0.1808 |
| seed_003 | 500 | duration_complete | 0.0270 | 0.3369 | 0.1168 | 0.0583 | 0.1584 | 2.2442 | 0.1809 |
| seed_004 | 500 | duration_complete | 0.0272 | 0.3406 | 0.1172 | 0.0653 | 0.1515 | 2.2059 | 0.1814 |
| seed_005 | 500 | duration_complete | 0.0313 | 0.3914 | 0.1081 | 0.1513 | 0.1469 | 2.2494 | 0.1828 |
| seed_006 | 500 | duration_complete | 0.0228 | 0.2852 | 0.1148 | 0.0615 | 0.1584 | 2.2543 | 0.1827 |
| seed_007 | 32 | fall_or_progress_failure | 0.0261 | 0.3257 | 1.1298 | 0.0465 | 0.0883 | 2.1980 | 0.1532 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3352 | 8.9628 | 0.0000 |
| seed_001 | 0.3198 | 9.3892 | 0.0000 |
| seed_002 | 0.3351 | 9.0712 | 0.0000 |
| seed_003 | 0.3352 | 8.9767 | 0.0000 |
| seed_004 | 0.3360 | 8.8237 | 0.0000 |
| seed_005 | 0.3351 | 8.9885 | 0.0000 |
| seed_006 | 0.3355 | 9.0172 | 0.0000 |
| seed_007 | 0.3037 | 8.7919 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
