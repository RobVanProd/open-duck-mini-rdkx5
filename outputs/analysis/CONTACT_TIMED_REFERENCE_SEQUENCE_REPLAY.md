# Target Sequence Replay Smoke

status: `HOLD_SEQUENCE_REPLAY_TERMINATED`

This is an offline sequence-preservation diagnostic over curated target windows.
It replays target action tables in closed-loop sim; it is not PPO, BC training, or a deployable policy.

## Dataset

- manifest: `outputs/analysis/contact_timed_reference_snippets_manifest.json`
- dataset_id: `f479d5d7ee026710`
- manifest_status: `HOLD_SOURCE_FRAGMENTS_DOUBLE_SUPPORT`
- policy_set: `aggregate`
- periodic_seam_correction: `True`
- soft_prior_config: `None`
- phase_adapter: `state_match`
- trace_dir: `outputs/analysis/contact_timed_reference_sequence_replay_traces`
- sequence_policies: `1`
- command_x: `0.0400`
- duration_s: `3.0000`
- seeds: `[0, 2]`

## Gates

- min_mean_vx_m_s: `0.0200`
- max_vy_abs_p95_m_s: `0.1200`
- max_body_pitch_abs_p95_rad: `0.2500`
- min_base_height_m: `0.1000`
- max_sent_velocity_p95_rad_s: `3.7500`

## Closed-Loop Sequence Replay

status: `HOLD_SEQUENCE_REPLAY_TERMINATED`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`

| policy | status | seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| aggregate_phase_table_seam_corrected | `HOLD_SEQUENCE_REPLAY_TERMINATED` | seed_000 | 85 | fall_or_progress_failure | 0.1812 | 4.5311 | 0.1869 | 1.1645 | 0.0408 | 0.3656 | 0.0723 |
| aggregate_phase_table_seam_corrected | `HOLD_SEQUENCE_REPLAY_TERMINATED` | seed_002 | 150 | duration_complete | 0.0194 | 0.4851 | 0.0622 | 0.3589 | 0.1459 | 0.3551 | 0.0746 |

### Phase Adapter Summary

| policy | seed | holds/s | skips/s | contact_mismatch_pct | phase_bins |
|---|---|---:|---:|---:|---:|
| aggregate_phase_table_seam_corrected | seed_000 | 0.0000 | 0.0000 | 11.2500 | 50 |
| aggregate_phase_table_seam_corrected | seed_002 | 0.0000 | 0.0000 | 0.6897 | 50 |

### Policy Table Summary

| policy | source | prefix_len | window_len | entry_count | status |
|---|---|---:|---:|---:|---|
| aggregate_phase_table_seam_corrected | aggregate | 5 | 50 | 9 | `HOLD_SEQUENCE_REPLAY_TERMINATED` |

## Interpretation

- Passing this smoke would justify a sequence/phase-aware imitation learner.
- Failing this smoke means target timing alone is not enough; do not launch PPO from these windows.
- This diagnostic preserves rollout timing; it does not test a memoryless obs-to-action clone.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
