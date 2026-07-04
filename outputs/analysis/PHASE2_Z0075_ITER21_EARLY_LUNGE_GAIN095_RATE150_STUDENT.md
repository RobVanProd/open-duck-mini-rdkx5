# Target Dataset BC Smoke

status: `HOLD_BC_FIT_NO_CLOSED_LOOP`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_merged_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `vanilla`
- fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit_corrected_knee.json`
- dataset_id: `ff13b355004422e9`
- samples: `53130`
- entries: `88`
- source_files: `77`
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
- train_rmse: `0.0192`
- train_mae: `0.0130`
- train_p95_abs_error: `0.0362`
- train_max_abs_error: `0.6286`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `0.2839`
- consecutive_pair_count: `46735`

### MLP Settings

- hidden_sizes: `[512, 256]`
- steps: `7000`
- batch_size: `512`
- learning_rate: `0.001`
- pair_count: `46735`
- target_rate_scale: `0.1`
- target_rate_limit_rad_s: `1.5`
- obs_noise_std: `0.0`
- obs_consistency_scale: `0.0`
- saved_npz: `outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_rate150_candidate/candidate_mlp.npz`
- exported_onnx: `policy/candidates/phase2_z0075_iter21_early_lunge_gain095_rate150_20260704/candidate.onnx`
- onnx_verify_max_abs_error: `0.0000`

| step | loss |
|---:|---:|
| 1 | 0.710367 |
| 700 | 0.001868 |
| 1400 | 0.000589 |
| 2100 | 0.000568 |
| 2800 | 0.000681 |
| 3500 | 0.000380 |
| 4200 | 0.000454 |
| 4900 | 0.000395 |
| 5600 | 0.000448 |
| 6300 | 0.000505 |
| 7000 | 0.000424 |

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0136 | 0.0354 | 0.1914 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0136 | 0.0354 | 0.1914 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0136 | 0.0354 | 0.1914 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0136 | 0.0354 | 0.1914 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0136 | 0.0354 | 0.1914 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0136 | 0.0354 | 0.1914 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0136 | 0.0354 | 0.1914 |
| outputs/analysis/phase2_phase1_rate175_z0026_x008_source_trace/phase1/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0136 | 0.0354 | 0.1914 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x0/rollouts_x0/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0138 | 0.0350 | 0.1399 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0138 | 0.0350 | 0.1399 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0189 | 0.0516 | 0.1881 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0189 | 0.0516 | 0.1881 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0189 | 0.0516 | 0.1881 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0189 | 0.0516 | 0.1881 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0189 | 0.0516 | 0.1881 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0189 | 0.0516 | 0.1881 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0189 | 0.0516 | 0.1881 |
| phase2_rate165_single_support_live_oracle_iter2_plan/relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0189 | 0.0516 | 0.1881 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x0/rollouts_x0/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0274 | 0.0685 | 0.3797 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0274 | 0.0685 | 0.3797 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0131 | 0.0343 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0131 | 0.0343 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0131 | 0.0343 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0131 | 0.0343 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0131 | 0.0343 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0131 | 0.0343 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0131 | 0.0343 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter0_run/relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0131 | 0.0343 | 0.1882 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x0/rollouts_x0/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0207 | 0.0533 | 0.1403 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0207 | 0.0533 | 0.1403 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0215 | 0.0603 | 0.3031 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0215 | 0.0603 | 0.3031 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0215 | 0.0603 | 0.3031 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0215 | 0.0603 | 0.3031 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0215 | 0.0603 | 0.3031 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0215 | 0.0603 | 0.3031 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0215 | 0.0603 | 0.3031 |
| phase2_z0026_corrected_source_live_oracle_iter1_run/relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0215 | 0.0603 | 0.3031 |
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_000/push_000_6e6c2d394c022b4d.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53069 | 61 | 0.0226 | 0.0679 | 0.2291 |
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_002/push_009_e969257189933035.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53088 | 42 | 0.0218 | 0.0581 | 0.1319 |
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_006/push_010_712c01db7c0c749d.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53066 | 64 | 0.0207 | 0.0626 | 0.1327 |
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_006/push_011_420a187c0ff36573.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53122 | 8 | 0.0411 | 0.1002 | 0.1332 |
| phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_rate150_seed0_trace/iter2_recovery_rate150/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52442 | 688 | 0.0217 | 0.0593 | 0.3295 |
| phase2_z0075_iter10_spike_local_recovery/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53050 | 80 | 0.0209 | 0.0604 | 0.2778 |
| phase2_z0075_iter10_spike_local_recovery/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53050 | 80 | 0.0204 | 0.0647 | 0.1967 |
| phase2_z0075_iter10_spike_local_recovery/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53050 | 80 | 0.0182 | 0.0497 | 0.1138 |
| phase2_z0075_iter10_spike_local_recovery/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53034 | 96 | 0.0200 | 0.0561 | 0.4827 |
| phase2_z0075_iter10_spike_local_recovery/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53050 | 80 | 0.0236 | 0.0765 | 0.2975 |
| phase2_z0075_iter10_spike_local_recovery/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53084 | 46 | 0.0483 | 0.1644 | 0.2710 |
| phase2_z0075_iter10_spike_local_recovery/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53033 | 97 | 0.0295 | 0.1020 | 0.3945 |
| phase2_z0075_iter21_early_lunge_gain095_relabel/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53099 | 31 | 0.0524 | 0.1704 | 0.3111 |
| phase2_z0075_iter2_seed7_pass_control_weighted/phase2_z0075_iter2_recovery_rate150_seed7_trace_control/iter2_recovery_rate150/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0136 | 0.0348 | 0.3028 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52637 | 493 | 0.0215 | 0.0609 | 0.2471 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52974 | 156 | 0.0286 | 0.0853 | 0.5729 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52681 | 449 | 0.0230 | 0.0630 | 0.7406 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52407 | 723 | 0.0214 | 0.0604 | 0.3773 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 53084 | 46 | 0.0581 | 0.1703 | 0.4818 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52885 | 245 | 0.0253 | 0.0778 | 0.3974 |
| relabel_x0/rollouts_x0/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0111 | 0.0254 | 0.5630 |
| relabel_x008/rollouts_x008/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0270 | 0.0838 | 0.7232 |
| relabel_x008/rollouts_x008/student/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52629 | 501 | 0.0246 | 0.0682 | 0.6816 |
| rollouts_x0/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 50880 | 2250 | 0.0076 | 0.0195 | 0.3390 |
| rollouts_x0/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 50880 | 2250 | 0.0080 | 0.0190 | 0.5904 |
| rollouts_x0/student/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0049 | 0.0129 | 0.1396 |
| rollouts_x0/student/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0049 | 0.0129 | 0.1396 |
| rollouts_x0/student/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0049 | 0.0129 | 0.1396 |
| rollouts_x0/student/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0049 | 0.0129 | 0.1396 |
| rollouts_x0/student/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0049 | 0.0129 | 0.1396 |
| rollouts_x0/student/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0049 | 0.0129 | 0.1396 |
| rollouts_x008/student/seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 51630 | 1500 | 0.0240 | 0.0717 | 0.3532 |
| rollouts_x008/student/seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 51820 | 1310 | 0.0217 | 0.0606 | 0.8445 |
| rollouts_x008/student/seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 51737 | 1393 | 0.0280 | 0.0891 | 0.5732 |
| rollouts_x008/student/seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52295 | 835 | 0.0219 | 0.0668 | 0.3994 |
| rollouts_x008/student/seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 51902 | 1228 | 0.0242 | 0.0713 | 0.7684 |
| rollouts_x008/student/seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52332 | 798 | 0.0228 | 0.0655 | 0.9236 |
| rollouts_x008/student/seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 52380 | 750 | 0.0180 | 0.0496 | 0.1598 |
| rollouts_x008/student/seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 51630 | 1500 | 0.0248 | 0.0688 | 0.8786 |

## Closed-Loop Smoke

status: `HOLD_BC_ROLLOUT_NOT_RUN`

Closed-loop replay was skipped by request.

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
