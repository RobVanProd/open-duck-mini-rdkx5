# Target Sequence Replay Smoke

status: `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE`

This is an offline sequence-preservation diagnostic over curated target windows.
It replays target action tables in closed-loop sim; it is not PPO, BC training, or a deployable policy.

## Dataset

- manifest: `outputs/analysis/target_dataset_manifest_dynamic_roll_lateral_fix_robust_modes.json`
- dataset_id: `47153f26ab48ef14`
- manifest_status: `PASS_TARGET_DATASET_MANIFEST_READY`
- policy_set: `all`
- sequence_policies: `10`
- command_x: `0.0400`
- duration_s: `1.2000`
- seeds: `[0, 2]`

## Gates

- min_mean_vx_m_s: `0.0200`
- max_vy_abs_p95_m_s: `0.1200`
- max_body_pitch_abs_p95_rad: `0.2500`
- min_base_height_m: `0.1000`
- max_sent_velocity_p95_rad_s: `3.7500`

## Closed-Loop Sequence Replay

status: `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`

| policy | status | seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 049f91faaf0f89ce_seed_000_5_54 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_000 | 60 | duration_complete | 0.0305 | 0.7629 | 0.0993 | 0.2786 | 0.1466 | 0.5134 | 0.0786 |
| 049f91faaf0f89ce_seed_000_5_54 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_002 | 60 | duration_complete | 0.0382 | 0.9554 | 0.1512 | 0.2632 | 0.1471 | 0.5134 | 0.0824 |
| 13248f6e57891bfd_seed_002_5_54 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_000 | 60 | duration_complete | 0.0307 | 0.7677 | 0.1194 | 0.3291 | 0.1469 | 0.5105 | 0.0751 |
| 13248f6e57891bfd_seed_002_5_54 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_002 | 60 | duration_complete | 0.0387 | 0.9679 | 0.1515 | 0.2520 | 0.1482 | 0.5105 | 0.0770 |
| 3e685b9f6658c91f_seed_002_10_59 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_000 | 60 | duration_complete | 0.0287 | 0.7167 | 0.1168 | 0.3165 | 0.1455 | 0.5296 | 0.0809 |
| 3e685b9f6658c91f_seed_002_10_59 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_002 | 60 | duration_complete | 0.0389 | 0.9715 | 0.1490 | 0.2947 | 0.1455 | 0.5296 | 0.0866 |
| a0d2bef05974584b_seed_002_5_54 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_000 | 60 | duration_complete | 0.0288 | 0.7201 | 0.1168 | 0.3165 | 0.1455 | 0.5296 | 0.0809 |
| a0d2bef05974584b_seed_002_5_54 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_002 | 60 | duration_complete | 0.0391 | 0.9781 | 0.1490 | 0.2948 | 0.1455 | 0.5296 | 0.0866 |
| a3223fecee75c157_seed_000_5_54 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_000 | 60 | duration_complete | 0.0307 | 0.7677 | 0.1194 | 0.3291 | 0.1469 | 0.5105 | 0.0751 |
| a3223fecee75c157_seed_000_5_54 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_002 | 60 | duration_complete | 0.0387 | 0.9679 | 0.1515 | 0.2520 | 0.1482 | 0.5105 | 0.0770 |
| aggregate_phase_table | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_000 | 60 | duration_complete | 0.0309 | 0.7719 | 0.1183 | 0.2967 | 0.1472 | 0.3668 | 0.0786 |
| aggregate_phase_table | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_002 | 60 | duration_complete | 0.0363 | 0.9066 | 0.1466 | 0.2521 | 0.1477 | 0.3668 | 0.0771 |
| b106a81e6738ba7f_seed_002_5_54 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_000 | 60 | duration_complete | 0.0305 | 0.7629 | 0.0993 | 0.2786 | 0.1466 | 0.5134 | 0.0786 |
| b106a81e6738ba7f_seed_002_5_54 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_002 | 60 | duration_complete | 0.0382 | 0.9554 | 0.1512 | 0.2632 | 0.1471 | 0.5134 | 0.0824 |
| c23b3f13d9cb14be_seed_002_10_59 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_000 | 60 | duration_complete | 0.0299 | 0.7469 | 0.0993 | 0.2786 | 0.1466 | 0.5134 | 0.0755 |
| c23b3f13d9cb14be_seed_002_10_59 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_002 | 60 | duration_complete | 0.0376 | 0.9389 | 0.1512 | 0.2595 | 0.1467 | 0.5134 | 0.0786 |
| cdbc4efa2b19db62_seed_000_5_54 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_000 | 60 | duration_complete | 0.0288 | 0.7201 | 0.1168 | 0.3165 | 0.1455 | 0.5296 | 0.0809 |
| cdbc4efa2b19db62_seed_000_5_54 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_002 | 60 | duration_complete | 0.0391 | 0.9781 | 0.1490 | 0.2948 | 0.1455 | 0.5296 | 0.0866 |
| e501ccdd19c42b18_seed_002_10_59 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_000 | 60 | duration_complete | 0.0305 | 0.7630 | 0.1194 | 0.3291 | 0.1469 | 0.5025 | 0.0735 |
| e501ccdd19c42b18_seed_002_10_59 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` | seed_002 | 60 | duration_complete | 0.0385 | 0.9616 | 0.1515 | 0.2459 | 0.1478 | 0.5025 | 0.0745 |

### Policy Table Summary

| policy | source | prefix_len | window_len | entry_count | status |
|---|---|---:|---:|---:|---|
| 049f91faaf0f89ce_seed_000_5_54 | seed_000.jsonl | 5 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` |
| 13248f6e57891bfd_seed_002_5_54 | seed_002.jsonl | 5 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` |
| 3e685b9f6658c91f_seed_002_10_59 | seed_002.jsonl | 10 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` |
| a0d2bef05974584b_seed_002_5_54 | seed_002.jsonl | 5 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` |
| a3223fecee75c157_seed_000_5_54 | seed_000.jsonl | 5 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` |
| aggregate_phase_table | aggregate | 5 | 50 | 9 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` |
| b106a81e6738ba7f_seed_002_5_54 | seed_002.jsonl | 5 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` |
| c23b3f13d9cb14be_seed_002_10_59 | seed_002.jsonl | 10 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` |
| cdbc4efa2b19db62_seed_000_5_54 | seed_000.jsonl | 5 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` |
| e501ccdd19c42b18_seed_002_10_59 | seed_002.jsonl | 10 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE` |

## Interpretation

- Passing this smoke would justify a sequence/phase-aware imitation learner.
- Failing this smoke means target timing alone is not enough; do not launch PPO from these windows.
- This diagnostic preserves rollout timing; it does not test a memoryless obs-to-action clone.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
