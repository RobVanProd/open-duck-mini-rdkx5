# Target Dataset BC Smoke

status: `HOLD_BC_FIT_NO_CLOSED_LOOP`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/phase2_z0075_iter23_startup_window_lhp_limit_merged_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `vanilla`
- fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit_corrected_knee.json`
- dataset_id: `90d0e6c9afd5eef7`
- samples: `53136`
- entries: `89`
- source_files: `78`
- max_source_fraction: `0.0423`
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
- train_rmse: `0.0190`
- train_mae: `0.0124`
- train_p95_abs_error: `0.0362`
- train_max_abs_error: `0.6466`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `0.2839`
- consecutive_pair_count: `46740`

### MLP Settings

- hidden_sizes: `[512, 256]`
- steps: `7000`
- batch_size: `512`
- learning_rate: `0.001`
- pair_count: `46740`
- target_rate_scale: `0.1`
- target_rate_limit_rad_s: `1.5`
- obs_noise_std: `0.0`
- obs_consistency_scale: `0.0`
- saved_npz: `outputs/analysis/phase2_z0075_iter23_startup_window_lhp_limit_rate150_candidate/candidate_mlp.npz`
- exported_onnx: `policy/candidates/phase2_z0075_iter23_startup_window_lhp_limit_rate150_20260704/candidate.onnx`
- onnx_verify_max_abs_error: `0.0000`

| step | loss |
|---:|---:|
| 1 | 0.686562 |
| 700 | 0.001362 |
| 1400 | 0.000565 |
| 2100 | 0.000474 |
| 2800 | 0.001128 |
| 3500 | 0.000489 |
| 4200 | 0.000523 |
| 4900 | 0.000525 |
| 5600 | 0.000388 |
| 6300 | 0.000455 |
| 7000 | 0.000401 |

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0136 | 0.0354 | 0.1915 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0136 | 0.0354 | 0.1915 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0136 | 0.0354 | 0.1915 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0136 | 0.0354 | 0.1915 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0136 | 0.0354 | 0.1915 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0136 | 0.0354 | 0.1915 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0136 | 0.0354 | 0.1915 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0136 | 0.0354 | 0.1915 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x0/rollouts_x0/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0138 | 0.0350 | 0.1399 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0138 | 0.0350 | 0.1399 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0189 | 0.0517 | 0.1882 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0189 | 0.0517 | 0.1882 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0189 | 0.0517 | 0.1882 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0189 | 0.0517 | 0.1882 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0189 | 0.0517 | 0.1882 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0189 | 0.0517 | 0.1882 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0189 | 0.0517 | 0.1882 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0189 | 0.0517 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x0/rollouts_x0/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0274 | 0.0685 | 0.3797 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0274 | 0.0685 | 0.3797 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0131 | 0.0342 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0131 | 0.0342 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0131 | 0.0342 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0131 | 0.0342 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0131 | 0.0342 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0131 | 0.0342 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0131 | 0.0342 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0131 | 0.0342 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x0/rollouts_x0/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0207 | 0.0534 | 0.1403 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0207 | 0.0534 | 0.1403 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0216 | 0.0603 | 0.3031 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0216 | 0.0603 | 0.3031 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0216 | 0.0603 | 0.3031 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0216 | 0.0603 | 0.3031 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0216 | 0.0603 | 0.3031 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0216 | 0.0603 | 0.3031 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0216 | 0.0603 | 0.3031 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0216 | 0.0603 | 0.3031 |
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_000/push_000_6e6c2d394c022b4d.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53075 | 61 | 0.0226 | 0.0679 | 0.2291 |
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_002/push_009_e969257189933035.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53094 | 42 | 0.0218 | 0.0581 | 0.1320 |
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_006/push_010_712c01db7c0c749d.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53072 | 64 | 0.0207 | 0.0626 | 0.1328 |
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_006/push_011_420a187c0ff36573.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53128 | 8 | 0.0411 | 0.1004 | 0.1333 |
| phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_rate150_seed0_trace/iter2_recovery_rate150/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52448 | 688 | 0.0217 | 0.0593 | 0.3293 |
| phase2_z0075_iter10_spike_local_recovery/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53056 | 80 | 0.0209 | 0.0605 | 0.2777 |
| phase2_z0075_iter10_spike_local_recovery/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53056 | 80 | 0.0204 | 0.0647 | 0.1964 |
| phase2_z0075_iter10_spike_local_recovery/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53056 | 80 | 0.0182 | 0.0497 | 0.1138 |
| phase2_z0075_iter10_spike_local_recovery/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53040 | 96 | 0.0200 | 0.0560 | 0.4827 |
| phase2_z0075_iter10_spike_local_recovery/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53056 | 80 | 0.0236 | 0.0764 | 0.2974 |
| phase2_z0075_iter10_spike_local_recovery/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53090 | 46 | 0.0483 | 0.1646 | 0.2711 |
| phase2_z0075_iter10_spike_local_recovery/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53039 | 97 | 0.0295 | 0.1019 | 0.3945 |
| phase2_z0075_iter21_early_lunge_gain095_relabel/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53105 | 31 | 0.0524 | 0.1704 | 0.3111 |
| phase2_z0075_iter23_startup_window_lhp_limit_relabel/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53130 | 6 | 0.0313 | 0.0929 | 0.1312 |
| phase2_z0075_iter2_seed7_pass_control_weighted/phase2_z0075_iter2_recovery_rate150_seed7_trace_control/iter2_recovery_rate150/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0136 | 0.0348 | 0.3024 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52643 | 493 | 0.0215 | 0.0609 | 0.2471 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52980 | 156 | 0.0286 | 0.0853 | 0.5732 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52687 | 449 | 0.0230 | 0.0630 | 0.7409 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52413 | 723 | 0.0214 | 0.0604 | 0.3774 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53090 | 46 | 0.0581 | 0.1704 | 0.4816 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52891 | 245 | 0.0253 | 0.0779 | 0.3975 |
| relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0111 | 0.0254 | 0.5641 |
| relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0270 | 0.0837 | 0.7239 |
| relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52635 | 501 | 0.0246 | 0.0682 | 0.6818 |
| rollouts_x0/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 50886 | 2250 | 0.0076 | 0.0195 | 0.3389 |
| rollouts_x0/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 50886 | 2250 | 0.0080 | 0.0190 | 0.5915 |
| rollouts_x0/student/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0049 | 0.0129 | 0.1396 |
| rollouts_x0/student/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0049 | 0.0129 | 0.1396 |
| rollouts_x0/student/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0049 | 0.0129 | 0.1396 |
| rollouts_x0/student/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0049 | 0.0129 | 0.1396 |
| rollouts_x0/student/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0049 | 0.0129 | 0.1396 |
| rollouts_x0/student/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0049 | 0.0129 | 0.1396 |
| rollouts_x008/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 51636 | 1500 | 0.0240 | 0.0717 | 0.3532 |
| rollouts_x008/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 51826 | 1310 | 0.0217 | 0.0606 | 0.8443 |
| rollouts_x008/student/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 51743 | 1393 | 0.0280 | 0.0890 | 0.5736 |
| rollouts_x008/student/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52301 | 835 | 0.0219 | 0.0668 | 0.3993 |
| rollouts_x008/student/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 51908 | 1228 | 0.0242 | 0.0713 | 0.7683 |
| rollouts_x008/student/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52338 | 798 | 0.0228 | 0.0655 | 0.9238 |
| rollouts_x008/student/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52386 | 750 | 0.0180 | 0.0495 | 0.1598 |
| rollouts_x008/student/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 51636 | 1500 | 0.0248 | 0.0687 | 0.8785 |

## Closed-Loop Smoke

status: `HOLD_BC_ROLLOUT_NOT_RUN`

Closed-loop replay was skipped by request.

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
