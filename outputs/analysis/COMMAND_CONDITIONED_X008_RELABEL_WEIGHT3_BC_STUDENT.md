# Target Dataset BC Smoke

status: `HOLD_BC_FIT_NO_CLOSED_LOOP`

This is a tiny offline behavior-cloning smoke over curated target windows.
It is not PPO training and does not produce a deployable policy.

## Dataset

- manifest: `outputs/analysis/command_conditioned_x008_relabel_weighted_manifest.json`
- include_source_regex: `None`
- exclude_source_regex: `None`
- alt_include_source_regex: `None`
- alt_exclude_source_regex: `None`
- actuator_bridge_mode: `vanilla`
- fit_json: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/actuator_response_fit.json`
- dataset_id: `547172c400c25c49`
- samples: `11250`
- entries: `21`
- source_files: `16`
- max_source_fraction: `0.1111`
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
- train_rmse: `0.0189`
- train_mae: `0.0136`
- train_p95_abs_error: `0.0364`
- train_max_abs_error: `0.3827`
- pred_action_saturation_pct: `0.0000`
- sample_to_parameter_ratio: `0.0515`
- consecutive_pair_count: `9732`

### MLP Settings

- hidden_sizes: `[512, 256, 128]`
- steps: `5000`
- batch_size: `512`
- learning_rate: `0.001`
- pair_count: `9732`
- target_rate_scale: `0.2`
- target_rate_limit_rad_s: `2.25`
- obs_noise_std: `0.0`
- obs_consistency_scale: `0.0`
- saved_npz: `outputs/analysis/command_conditioned_x008_relabel_weight3_candidate/candidate_mlp.npz`
- exported_onnx: `outputs/analysis/command_conditioned_x008_relabel_weight3_candidate/candidate.onnx`
- onnx_verify_max_abs_error: `0.0000`

| step | loss |
|---:|---:|
| 1 | 1.000333 |
| 500 | 0.000792 |
| 1000 | 0.001058 |
| 1500 | 0.000508 |
| 2000 | 0.000663 |
| 2500 | 0.000302 |
| 3000 | 0.000516 |
| 3500 | 0.000418 |
| 4000 | 0.000455 |
| 4500 | 0.000497 |
| 5000 | 0.000392 |

### Source Holdout (ridge baseline)

| held_out_source | status | train_samples | test_samples | mae | p95_abs_error | max_abs_error |
|---|---|---:|---:|---:|---:|---:|
| seed_000/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10250 | 1000 | 0.0106 | 0.0353 | 0.1462 |
| seed_001/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10000 | 1250 | 0.0140 | 0.0461 | 0.2062 |
| seed_002/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10750 | 500 | 0.0057 | 0.0149 | 0.1513 |
| seed_003/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10000 | 1250 | 0.0139 | 0.0460 | 0.1795 |
| seed_004/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10750 | 500 | 0.0058 | 0.0153 | 0.1307 |
| seed_005/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10250 | 1000 | 0.0127 | 0.0450 | 0.2233 |
| seed_006/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10750 | 500 | 0.0062 | 0.0158 | 0.2926 |
| seed_007/trace.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10000 | 1250 | 0.0141 | 0.0468 | 0.2123 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_000.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10750 | 500 | 0.0224 | 0.0685 | 0.2576 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_001.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10750 | 500 | 0.0226 | 0.0720 | 0.2602 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_002.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10750 | 500 | 0.0225 | 0.0696 | 0.2363 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_003.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10750 | 500 | 0.0225 | 0.0687 | 0.2364 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_004.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10750 | 500 | 0.0236 | 0.0736 | 0.2392 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_005.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10750 | 500 | 0.0243 | 0.0773 | 0.2578 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_006.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10750 | 500 | 0.0234 | 0.0742 | 0.2886 |
| source_vx_pitch_chain_rate_limited_2p25_traces/seed_007.jsonl | `PASS_SOURCE_HOLDOUT_EVALUATED` | 10750 | 500 | 0.0233 | 0.0711 | 0.2522 |

## Closed-Loop Smoke

status: `HOLD_BC_ROLLOUT_NOT_RUN`

Closed-loop replay was skipped by request.

## Gate

- This smoke only checks whether the compact target dataset is usable for a tiny supervised fit.
- A pass is permission to design a reviewed imitation/pretraining experiment, not permission to deploy.
- Review source distribution and held-out-source errors before any larger imitation/pretraining run.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
