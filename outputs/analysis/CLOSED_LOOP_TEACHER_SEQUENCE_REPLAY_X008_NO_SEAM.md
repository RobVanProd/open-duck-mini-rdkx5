# Target Sequence Replay Smoke

status: `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION`

This is an offline sequence-preservation diagnostic over curated target windows.
It replays target action tables in closed-loop sim; it is not PPO, BC training, or a deployable policy.

## Dataset

- manifest: `outputs/analysis/closed_loop_teacher_dataset_manifest.json`
- dataset_id: `407af2cbe0ad69e1`
- manifest_status: `PASS_TARGET_DATASET_MANIFEST_READY`
- policy_set: `aggregate`
- periodic_seam_correction: `False`
- soft_prior_config: `None`
- phase_adapter: `fixed_time`
- trace_dir: `None`
- sequence_policies: `1`
- command_x: `0.0800`
- duration_s: `5.0000`
- seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`

## Gates

- min_mean_vx_m_s: `0.0200`
- max_vy_abs_p95_m_s: `0.1200`
- max_body_pitch_abs_p95_rad: `0.2500`
- min_base_height_m: `0.1000`
- max_sent_velocity_p95_rad_s: `3.7500`

## Closed-Loop Sequence Replay

status: `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`

| policy | status | seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| aggregate_phase_table | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_000 | 250 | duration_complete | 0.0033 | 0.0416 | 0.0288 | 0.0314 | 0.1519 | 0.2853 | 0.0382 |
| aggregate_phase_table | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_001 | 250 | duration_complete | 0.0014 | 0.0173 | 0.0655 | 0.0224 | 0.1559 | 0.2853 | 0.0382 |
| aggregate_phase_table | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_002 | 250 | duration_complete | 0.0052 | 0.0653 | 0.0127 | 0.0256 | 0.1509 | 0.2853 | 0.0383 |
| aggregate_phase_table | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_003 | 250 | duration_complete | -0.0105 | -0.1316 | 0.0263 | 0.1178 | 0.1543 | 0.2853 | 0.0382 |
| aggregate_phase_table | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_004 | 250 | duration_complete | 0.0067 | 0.0838 | 0.0197 | 0.0460 | 0.1508 | 0.2853 | 0.0383 |
| aggregate_phase_table | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_005 | 250 | duration_complete | 0.0113 | 0.1413 | 0.0327 | 0.1351 | 0.1462 | 0.2853 | 0.0391 |
| aggregate_phase_table | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_006 | 250 | duration_complete | 0.0019 | 0.0244 | 0.0924 | 0.0416 | 0.1556 | 0.2853 | 0.0389 |
| aggregate_phase_table | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_007 | 250 | duration_complete | 0.0018 | 0.0229 | 0.0648 | 0.0252 | 0.1559 | 0.2853 | 0.0384 |

### Phase Adapter Summary

| policy | seed | holds/s | skips/s | contact_mismatch_pct | phase_bins |
|---|---|---:|---:|---:|---:|
| aggregate_phase_table | seed_000 | 0.0000 | 0.0000 | 1.6064 | 25 |
| aggregate_phase_table | seed_001 | 0.0000 | 0.0000 | 2.4096 | 25 |
| aggregate_phase_table | seed_002 | 0.0000 | 0.0000 | 1.6064 | 25 |
| aggregate_phase_table | seed_003 | 0.0000 | 0.0000 | 1.6064 | 25 |
| aggregate_phase_table | seed_004 | 0.0000 | 0.0000 | 2.0080 | 25 |
| aggregate_phase_table | seed_005 | 0.0000 | 0.0000 | 1.6064 | 25 |
| aggregate_phase_table | seed_006 | 0.0000 | 0.0000 | 5.6225 | 25 |
| aggregate_phase_table | seed_007 | 0.0000 | 0.0000 | 3.2129 | 25 |

### Policy Table Summary

| policy | source | prefix_len | window_len | entry_count | status |
|---|---|---:|---:|---:|---|
| aggregate_phase_table | aggregate | 1 | 25 | 259 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` |

## Interpretation

- Passing this smoke would justify a sequence/phase-aware imitation learner.
- Failing this smoke means target timing alone is not enough; do not launch PPO from these windows.
- This diagnostic preserves rollout timing; it does not test a memoryless obs-to-action clone.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
