# Target Dataset BC Smoke

status: `HOLD_BC_REPLAY_TERMINATED`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/filtered_source_vx_selector_dagger5_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `fitted`
- fit_json: `outputs/analysis/actuator_response_fit.json`
- dataset_id: `d446ac98f0000514`
- samples: `13500`
- entries: `27`
- source_files: `27`
- max_source_fraction: `0.0370`
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
- train_rmse: `0.0244`
- train_mae: `0.0159`
- train_p95_abs_error: `0.0487`
- train_max_abs_error: `0.3100`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `0.4303`
- consecutive_pair_count: `13473`

### MLP Settings

- hidden_sizes: `[128, 128]`
- steps: `5000`
- batch_size: `512`
- learning_rate: `0.001`
- pair_count: `13473`
- target_rate_scale: `0.1`
- target_rate_limit_rad_s: `3.75`
- obs_noise_std: `0.0`
- obs_consistency_scale: `0.0`
- saved_npz: `outputs/analysis/source_vx_selector_trace_dagger5_filtered_mlp128_rate_reg_candidate/candidate_mlp.npz`
- exported_onnx: `outputs/analysis/source_vx_selector_trace_dagger5_filtered_mlp128_rate_reg_candidate/candidate.onnx`
- onnx_verify_max_abs_error: `0.0000`

| step | loss |
|---:|---:|
| 1 | 1.031854 |
| 500 | 0.002088 |
| 1000 | 0.001275 |
| 1500 | 0.001019 |
| 2000 | 0.000857 |
| 2500 | 0.000818 |
| 3000 | 0.000696 |
| 3500 | 0.000663 |
| 4000 | 0.000661 |
| 4500 | 0.000635 |
| 5000 | 0.000607 |

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_016.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0217 | 0.0681 | 0.5595 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_017.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0212 | 0.0704 | 0.3940 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_018.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0216 | 0.0701 | 0.3007 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_022.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0224 | 0.0731 | 0.3455 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_024.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0231 | 0.0752 | 0.2615 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_027.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0231 | 0.0755 | 0.3208 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_029.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0223 | 0.0724 | 0.5138 |
| source_vx_selector_expansion_seeds16_31_fitted_10s_traces/seed_031.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0214 | 0.0693 | 0.4089 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_008.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0216 | 0.0696 | 0.3349 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_010.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0210 | 0.0681 | 0.2293 |
| source_vx_selector_expansion_seeds8_15_fitted_10s_traces/seed_011.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0214 | 0.0687 | 0.3338 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0229 | 0.0715 | 0.2896 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0226 | 0.0709 | 0.3523 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0231 | 0.0710 | 0.3318 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0232 | 0.0727 | 0.2405 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0231 | 0.0747 | 0.3895 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0255 | 0.0829 | 0.3720 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0236 | 0.0745 | 0.3681 |
| source_vx_selector_fitted_bridge_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0223 | 0.0700 | 0.2905 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0184 | 0.0545 | 0.2078 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0173 | 0.0508 | 0.2159 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0177 | 0.0511 | 0.1806 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0198 | 0.0557 | 0.2092 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0180 | 0.0531 | 0.2034 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0180 | 0.0510 | 0.1745 |
| source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0179 | 0.0523 | 0.2207 |
| source_vx_selector_trace_dagger2_rate_reg_standard_relabel_blend_x008_10s_traces/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 13000 | 500 | 0.0208 | 0.0597 | 0.2330 |

## Closed-Loop Smoke

status: `HOLD_BC_REPLAY_TERMINATED`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`
model_kind: `mlp`

| seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| seed_000 | 500 | duration_complete | 0.0258 | 0.3219 | 0.1051 | 0.0550 | 0.1536 | 2.1749 | 0.1747 |
| seed_001 | 33 | fall_or_progress_failure | 0.0052 | 0.0648 | 1.1620 | 0.1578 | 0.0817 | 1.9438 | 0.1210 |
| seed_002 | 500 | duration_complete | 0.0308 | 0.3850 | 0.1118 | 0.0615 | 0.1525 | 2.2161 | 0.1786 |
| seed_003 | 500 | duration_complete | 0.0241 | 0.3007 | 0.1136 | 0.0578 | 0.1583 | 2.2437 | 0.1761 |
| seed_004 | 500 | duration_complete | 0.0264 | 0.3301 | 0.1084 | 0.0659 | 0.1515 | 2.1849 | 0.1766 |
| seed_005 | 95 | fall_or_progress_failure | -0.1500 | -1.8755 | 0.1269 | 1.0372 | 0.0742 | 1.8817 | 0.1580 |
| seed_006 | 500 | duration_complete | 0.0225 | 0.2809 | 0.1191 | 0.0654 | 0.1587 | 2.2193 | 0.1759 |
| seed_007 | 33 | fall_or_progress_failure | 0.0277 | 0.3458 | 1.1782 | 0.0452 | 0.0776 | 1.8496 | 0.1487 |

### Rollout Action Summary

| seed | action_abs_mean | action_delta_p95_per_s | action_saturation_pct |
|---|---:|---:|---:|
| seed_000 | 0.3301 | 8.6995 | 0.0000 |
| seed_001 | 0.2782 | 7.7193 | 0.0000 |
| seed_002 | 0.3335 | 8.8645 | 0.0000 |
| seed_003 | 0.3324 | 8.9775 | 0.0000 |
| seed_004 | 0.3331 | 8.7394 | 0.0000 |
| seed_005 | 0.3231 | 7.6360 | 0.0000 |
| seed_006 | 0.3343 | 8.8770 | 0.0000 |
| seed_007 | 0.2875 | 7.3982 | 0.0000 |

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
