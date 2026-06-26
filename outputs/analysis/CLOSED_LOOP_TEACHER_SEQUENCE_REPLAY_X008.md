# Target Sequence Replay Smoke

status: `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION`

This is an offline sequence-preservation diagnostic over curated target windows.
It replays target action tables in closed-loop sim; it is not PPO, BC training, or a deployable policy.

## Dataset

- manifest: `outputs/analysis/closed_loop_teacher_dataset_manifest.json`
- dataset_id: `407af2cbe0ad69e1`
- manifest_status: `PASS_TARGET_DATASET_MANIFEST_READY`
- policy_set: `aggregate`
- periodic_seam_correction: `True`
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
| aggregate_phase_table_seam_corrected | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_000 | 250 | duration_complete | 0.0032 | 0.0400 | 0.0293 | 0.0278 | 0.1519 | 0.2660 | 0.0378 |
| aggregate_phase_table_seam_corrected | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_001 | 250 | duration_complete | 0.0012 | 0.0145 | 0.0594 | 0.0217 | 0.1559 | 0.2660 | 0.0374 |
| aggregate_phase_table_seam_corrected | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_002 | 250 | duration_complete | 0.0050 | 0.0622 | 0.0090 | 0.0220 | 0.1509 | 0.2660 | 0.0377 |
| aggregate_phase_table_seam_corrected | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_003 | 250 | duration_complete | -0.0108 | -0.1348 | 0.0277 | 0.1213 | 0.1547 | 0.2660 | 0.0376 |
| aggregate_phase_table_seam_corrected | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_004 | 250 | duration_complete | 0.0064 | 0.0806 | 0.0251 | 0.0389 | 0.1508 | 0.2660 | 0.0378 |
| aggregate_phase_table_seam_corrected | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_005 | 250 | duration_complete | 0.0111 | 0.1384 | 0.0301 | 0.1347 | 0.1462 | 0.2660 | 0.0383 |
| aggregate_phase_table_seam_corrected | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_006 | 250 | duration_complete | 0.0017 | 0.0215 | 0.0924 | 0.0394 | 0.1556 | 0.2660 | 0.0380 |
| aggregate_phase_table_seam_corrected | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_007 | 250 | duration_complete | 0.0016 | 0.0199 | 0.0621 | 0.0219 | 0.1559 | 0.2660 | 0.0378 |

### Phase Adapter Summary

| policy | seed | holds/s | skips/s | contact_mismatch_pct | phase_bins |
|---|---|---:|---:|---:|---:|
| aggregate_phase_table_seam_corrected | seed_000 | 0.0000 | 0.0000 | 1.6064 | 25 |
| aggregate_phase_table_seam_corrected | seed_001 | 0.0000 | 0.0000 | 2.4096 | 25 |
| aggregate_phase_table_seam_corrected | seed_002 | 0.0000 | 0.0000 | 1.6064 | 25 |
| aggregate_phase_table_seam_corrected | seed_003 | 0.0000 | 0.0000 | 1.6064 | 25 |
| aggregate_phase_table_seam_corrected | seed_004 | 0.0000 | 0.0000 | 2.0080 | 25 |
| aggregate_phase_table_seam_corrected | seed_005 | 0.0000 | 0.0000 | 1.6064 | 25 |
| aggregate_phase_table_seam_corrected | seed_006 | 0.0000 | 0.0000 | 5.6225 | 25 |
| aggregate_phase_table_seam_corrected | seed_007 | 0.0000 | 0.0000 | 3.2129 | 25 |

### Policy Table Summary

| policy | source | prefix_len | window_len | entry_count | status |
|---|---|---:|---:|---:|---|
| aggregate_phase_table_seam_corrected | aggregate | 1 | 25 | 259 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` |

## Interpretation

- Passing this smoke would justify a sequence/phase-aware imitation learner.
- Failing this smoke means target timing alone is not enough; do not launch PPO from these windows.
- This diagnostic preserves rollout timing; it does not test a memoryless obs-to-action clone.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
