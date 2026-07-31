# Target Sequence Replay Smoke

status: `HOLD_SEQUENCE_REPLAY_TERMINATED`

This is an offline sequence-preservation diagnostic over curated target windows.
It replays target action tables in closed-loop sim; it is not PPO, BC training, or a deployable policy.

## Dataset

- manifest: `outputs/analysis/relabelled_selector_replay_manifest.json`
- dataset_id: `6e08dbfe23f28419`
- manifest_status: `PASS_SELECTOR_REPLAY_MANIFEST_READY`
- policy_set: `per-entry`
- periodic_seam_correction: `False`
- soft_prior_config: `None`
- phase_adapter: `fixed_time`
- trace_dir: `outputs/analysis/relabelled_selector_replay_top3_5s_traces`
- sequence_policies: `3`
- command_x: `0.0800`
- duration_s: `5.0000`
- seeds: `[0, 1]`

## Gates

- min_mean_vx_m_s: `0.0400`
- max_vy_abs_p95_m_s: `0.2000`
- max_body_pitch_abs_p95_rad: `0.2500`
- min_base_height_m: `0.1000`
- max_sent_velocity_p95_rad_s: `3.7500`

## Closed-Loop Sequence Replay

status: `HOLD_SEQUENCE_REPLAY_TERMINATED`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`

| policy | status | seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 5e3ac8cda5c15017_trace_full_obs_footpos_38 | `HOLD_SEQUENCE_REPLAY_TERMINATED` | seed_000 | 250 | duration_complete | 0.0475 | 0.5935 | 0.1714 | 0.1134 | 0.1532 | 3.0404 | 0.1307 |
| 5e3ac8cda5c15017_trace_full_obs_footpos_38 | `HOLD_SEQUENCE_REPLAY_TERMINATED` | seed_001 | 36 | fall_or_progress_failure | -0.0690 | -0.8625 | 1.0380 | 0.3202 | 0.1004 | 4.9515 | 0.1603 |
| aec48152eb9eae44_trace_full_obs_footpos_15 | `HOLD_SEQUENCE_REPLAY_TERMINATED` | seed_000 | 250 | duration_complete | 0.0440 | 0.5502 | 0.1794 | 0.0825 | 0.1565 | 2.8397 | 0.1283 |
| aec48152eb9eae44_trace_full_obs_footpos_15 | `HOLD_SEQUENCE_REPLAY_TERMINATED` | seed_001 | 38 | fall_or_progress_failure | -0.0913 | -1.1418 | 1.0610 | 0.3678 | 0.0995 | 4.1847 | 0.1248 |
| c7a94febd1c20ec4_trace_full_obs_footpos_72 | `HOLD_SEQUENCE_REPLAY_TERMINATED` | seed_000 | 250 | duration_complete | 0.0465 | 0.5817 | 0.1618 | 0.0466 | 0.1559 | 2.5441 | 0.1240 |
| c7a94febd1c20ec4_trace_full_obs_footpos_72 | `HOLD_SEQUENCE_REPLAY_TERMINATED` | seed_001 | 33 | fall_or_progress_failure | -0.0822 | -1.0274 | 1.1032 | 0.3488 | 0.0966 | 3.1021 | 0.1245 |

### Phase Adapter Summary

| policy | seed | holds/s | skips/s | contact_mismatch_pct | phase_bins |
|---|---|---:|---:|---:|---:|
| 5e3ac8cda5c15017_trace_full_obs_footpos_38 | seed_000 | 0.0000 | 0.0000 | 18.3962 | 84 |
| 5e3ac8cda5c15017_trace_full_obs_footpos_38 | seed_001 | 0.0000 | 0.0000 | NA | 0 |
| aec48152eb9eae44_trace_full_obs_footpos_15 | seed_000 | 0.0000 | 0.0000 | 20.8333 | 96 |
| aec48152eb9eae44_trace_full_obs_footpos_15 | seed_001 | 0.0000 | 0.0000 | NA | 0 |
| c7a94febd1c20ec4_trace_full_obs_footpos_72 | seed_000 | 0.0000 | 0.0000 | 24.1573 | 78 |
| c7a94febd1c20ec4_trace_full_obs_footpos_72 | seed_001 | 0.0000 | 0.0000 | NA | 0 |

### Policy Table Summary

| policy | source | prefix_len | window_len | entry_count | status |
|---|---|---:|---:|---:|---|
| 5e3ac8cda5c15017_trace_full_obs_footpos_38_121 | trace_full_obs_footpos.jsonl | 38 | 84 | 1 | `HOLD_SEQUENCE_REPLAY_TERMINATED` |
| aec48152eb9eae44_trace_full_obs_footpos_154_249 | trace_full_obs_footpos.jsonl | 154 | 96 | 1 | `HOLD_SEQUENCE_REPLAY_TERMINATED` |
| c7a94febd1c20ec4_trace_full_obs_footpos_72_149 | trace_full_obs_footpos.jsonl | 72 | 78 | 1 | `HOLD_SEQUENCE_REPLAY_TERMINATED` |

## Interpretation

- Passing this smoke would justify a sequence/phase-aware imitation learner.
- Failing this smoke means target timing alone is not enough; do not launch PPO from these windows.
- This diagnostic preserves rollout timing; it does not test a memoryless obs-to-action clone.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
