# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_TERMINATED`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/filtered_source_vx_selector_dagger6_recovery_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `fitted`
- fit_json: `outputs/analysis/actuator_response_fit.json`
- dataset_id: `003ff2b109874358`
- samples: `19628`
- entries: `43`
- source_files: `35`
- max_source_fraction: `0.0509`
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
- train_rmse: `0.0278`
- train_mae: `0.0185`
- train_p95_abs_error: `0.0562`
- train_max_abs_error: `0.3350`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `0.6256`
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
- saved_npz: `outputs/analysis/source_vx_selector_trace_dagger6_recovery_mlp128_rate_reg_candidate/candidate_mlp.npz`
- exported_onnx: `outputs/analysis/source_vx_selector_trace_dagger6_recovery_mlp128_rate_reg_candidate/candidate.onnx`
- onnx_verify_max_abs_error: `0.0000`

| step | loss |
|---:|---:|
| 1 | 0.970859 |
| 500 | 0.002412 |
| 1000 | 0.001436 |
| 1500 | 0.001142 |
| 2000 | 0.001163 |
| 2500 | 0.000966 |
| 3000 | 0.001007 |
| 3500 | 0.000842 |
| 4000 | 0.000915 |
| 4500 | 0.000809 |
| 5000 | 0.000863 |

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 18628 | 1000 | 0.0315 | 0.0991 | 0.4505 |
| seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19564 | 64 | 0.1014 | 0.2905 | 0.6598 |
| seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 18628 | 1000 | 0.0298 | 0.0896 | 0.3199 |
| seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 18628 | 1000 | 0.0289 | 0.0887 | 0.2948 |
| seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 18628 | 1000 | 0.0301 | 0.0955 | 0.4349 |
| seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 18628 | 1000 | 0.0294 | 0.0912 | 0.3454 |
| seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 18628 | 1000 | 0.0290 | 0.0880 | 0.2877 |
| seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19564 | 64 | 0.0751 | 0.2180 | 0.8638 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_016.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0234 | 0.0730 | 0.5016 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_017.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0228 | 0.0725 | 0.4046 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_018.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0230 | 0.0718 | 0.2888 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_022.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0241 | 0.0759 | 0.4037 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_024.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0249 | 0.0774 | 0.2577 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_027.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0247 | 0.0787 | 0.3298 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_029.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0236 | 0.0756 | 0.3219 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_031.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0226 | 0.0716 | 0.3436 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_008.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0232 | 0.0735 | 0.3507 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_010.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0226 | 0.0710 | 0.2337 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_011.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0231 | 0.0717 | 0.3291 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0241 | 0.0733 | 0.2969 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0238 | 0.0704 | 0.3303 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0245 | 0.0727 | 0.3117 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0249 | 0.0768 | 0.2482 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0244 | 0.0754 | 0.3528 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0265 | 0.0828 | 0.3745 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0247 | 0.0767 | 0.3574 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0235 | 0.0726 | 0.3191 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0188 | 0.0549 | 0.2067 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0178 | 0.0523 | 0.1857 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0186 | 0.0532 | 0.1856 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0208 | 0.0597 | 0.2222 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0190 | 0.0556 | 0.2104 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0189 | 0.0549 | 0.1650 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0187 | 0.0549 | 0.2043 |
| source_vx_selector_trace_dagger2_rate_reg_standard_relabel_blend_x008_10s_traces/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 19128 | 500 | 0.0211 | 0.0598 | 0.2116 |

## Closed-Loop Smoke

status: `HOLD_BC_REPLAY_TERMINATED`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `mlp`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 500 | duration_complete | 0.0323 | 0.4037 | 0.1048 | 0.0555 | 0.1536 | 2.2872 | 0.1787 |
| seed_001 | 32 | fall_or_progress_failure | 0.0104 | 0.1296 | 1.2437 | 0.1838 | 0.0789 | 2.0855 | 0.1743 |
| seed_002 | 500 | duration_complete | 0.0329 | 0.4108 | 0.1100 | 0.0621 | 0.1525 | 2.2564 | 0.1791 |
| seed_003 | 500 | duration_complete | 0.0278 | 0.3473 | 0.1085 | 0.0590 | 0.1586 | 2.2833 | 0.1791 |
| seed_004 | 500 | duration_complete | 0.0315 | 0.3942 | 0.1133 | 0.0699 | 0.1515 | 2.2832 | 0.1787 |
| seed_005 | 500 | duration_complete | 0.0338 | 0.4228 | 0.1059 | 0.1459 | 0.1469 | 2.2577 | 0.1791 |
| seed_006 | 500 | duration_complete | 0.0267 | 0.3338 | 0.1230 | 0.0660 | 0.1587 | 2.2947 | 0.1799 |
| seed_007 | 33 | fall_or_progress_failure | 0.0285 | 0.3559 | 1.1495 | 0.0741 | 0.0796 | 1.9969 | 0.1570 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3363 | 9.1271 | 0.0000 |
| seed_001 | 0.3140 | 8.3419 | 0.0000 |
| seed_002 | 0.3362 | 9.0132 | 0.0000 |
| seed_003 | 0.3365 | 9.1331 | 0.0000 |
| seed_004 | 0.3368 | 9.1327 | 0.0000 |
| seed_005 | 0.3359 | 9.0065 | 0.0000 |
| seed_006 | 0.3363 | 9.1787 | 0.0000 |
| seed_007 | 0.3076 | 7.9874 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
