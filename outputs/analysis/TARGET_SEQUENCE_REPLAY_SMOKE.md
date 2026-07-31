# Target Sequence Replay Smoke

status: `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION`

This is an offline sequence-preservation diagnostic over curated target windows.
It replays target action tables in closed-loop sim; it is not PPO, BC training, or a deployable policy.

## Dataset

- manifest: `outputs/analysis/target_dataset_manifest_dynamic_roll_lateral_fix_robust_modes.json`
- dataset_id: `47153f26ab48ef14`
- manifest_status: `PASS_TARGET_DATASET_MANIFEST_READY`
- policy_set: `all`
- sequence_policies: `10`
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

status: `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION`
jax_backend: `cpu`
jax_devices: `['TFRT_CPU_0']`

| policy | status | seed | samples | termination | vx | ratio | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 049f91faaf0f89ce_seed_000_5_54 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_000 | 150 | duration_complete | 0.0107 | 0.2681 | 0.0716 | 0.2754 | 0.1466 | 0.5134 | 0.0784 |
| 049f91faaf0f89ce_seed_000_5_54 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_002 | 150 | duration_complete | 0.0133 | 0.3321 | 0.0736 | 0.2694 | 0.1470 | 0.5134 | 0.0785 |
| 13248f6e57891bfd_seed_002_5_54 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_000 | 150 | duration_complete | 0.0123 | 0.3071 | 0.0882 | 0.3246 | 0.1469 | 0.5105 | 0.0735 |
| 13248f6e57891bfd_seed_002_5_54 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_002 | 150 | duration_complete | 0.0142 | 0.3556 | 0.0456 | 0.2749 | 0.1472 | 0.5105 | 0.0745 |
| 3e685b9f6658c91f_seed_002_10_59 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_000 | 150 | duration_complete | 0.0121 | 0.3017 | 0.0881 | 0.3160 | 0.1455 | 0.5296 | 0.0831 |
| 3e685b9f6658c91f_seed_002_10_59 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_002 | 150 | duration_complete | 0.0140 | 0.3488 | 0.0650 | 0.2863 | 0.1455 | 0.5296 | 0.0847 |
| a0d2bef05974584b_seed_002_5_54 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_000 | 150 | duration_complete | 0.0119 | 0.2973 | 0.0881 | 0.3160 | 0.1455 | 0.5296 | 0.0827 |
| a0d2bef05974584b_seed_002_5_54 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_002 | 150 | duration_complete | 0.0140 | 0.3505 | 0.0650 | 0.2867 | 0.1455 | 0.5296 | 0.0845 |
| a3223fecee75c157_seed_000_5_54 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_000 | 150 | duration_complete | 0.0123 | 0.3071 | 0.0882 | 0.3246 | 0.1469 | 0.5105 | 0.0735 |
| a3223fecee75c157_seed_000_5_54 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_002 | 150 | duration_complete | 0.0142 | 0.3556 | 0.0456 | 0.2749 | 0.1472 | 0.5105 | 0.0745 |
| aggregate_phase_table | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_000 | 150 | duration_complete | 0.0117 | 0.2930 | 0.0645 | 0.2935 | 0.1472 | 0.3658 | 0.0722 |
| aggregate_phase_table | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_002 | 150 | duration_complete | 0.0138 | 0.3443 | 0.0499 | 0.2536 | 0.1476 | 0.3658 | 0.0717 |
| b106a81e6738ba7f_seed_002_5_54 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_000 | 150 | duration_complete | 0.0107 | 0.2681 | 0.0716 | 0.2754 | 0.1466 | 0.5134 | 0.0784 |
| b106a81e6738ba7f_seed_002_5_54 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_002 | 150 | duration_complete | 0.0133 | 0.3321 | 0.0736 | 0.2694 | 0.1470 | 0.5134 | 0.0785 |
| c23b3f13d9cb14be_seed_002_10_59 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_000 | 150 | duration_complete | 0.0111 | 0.2778 | 0.0716 | 0.2754 | 0.1466 | 0.5177 | 0.0764 |
| c23b3f13d9cb14be_seed_002_10_59 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_002 | 150 | duration_complete | 0.0147 | 0.3668 | 0.0736 | 0.2591 | 0.1466 | 0.5177 | 0.0773 |
| cdbc4efa2b19db62_seed_000_5_54 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_000 | 150 | duration_complete | 0.0119 | 0.2973 | 0.0881 | 0.3160 | 0.1455 | 0.5296 | 0.0827 |
| cdbc4efa2b19db62_seed_000_5_54 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_002 | 150 | duration_complete | 0.0140 | 0.3505 | 0.0650 | 0.2867 | 0.1455 | 0.5296 | 0.0845 |
| e501ccdd19c42b18_seed_002_10_59 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_000 | 150 | duration_complete | 0.0116 | 0.2893 | 0.0882 | 0.3246 | 0.1469 | 0.5105 | 0.0732 |
| e501ccdd19c42b18_seed_002_10_59 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` | seed_002 | 150 | duration_complete | 0.0127 | 0.3185 | 0.0456 | 0.2579 | 0.1472 | 0.5105 | 0.0736 |

### Policy Table Summary

| policy | source | prefix_len | window_len | entry_count | status |
|---|---|---:|---:|---:|---|
| 049f91faaf0f89ce_seed_000_5_54 | seed_000.jsonl | 5 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` |
| 13248f6e57891bfd_seed_002_5_54 | seed_002.jsonl | 5 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` |
| 3e685b9f6658c91f_seed_002_10_59 | seed_002.jsonl | 10 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` |
| a0d2bef05974584b_seed_002_5_54 | seed_002.jsonl | 5 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` |
| a3223fecee75c157_seed_000_5_54 | seed_000.jsonl | 5 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` |
| aggregate_phase_table | aggregate | 5 | 50 | 9 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` |
| b106a81e6738ba7f_seed_002_5_54 | seed_002.jsonl | 5 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` |
| c23b3f13d9cb14be_seed_002_10_59 | seed_002.jsonl | 10 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` |
| cdbc4efa2b19db62_seed_000_5_54 | seed_000.jsonl | 5 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` |
| e501ccdd19c42b18_seed_002_10_59 | seed_002.jsonl | 10 | 50 | 1 | `HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION` |

## Interpretation

- Passing this smoke would justify a sequence/phase-aware imitation learner.
- Failing this smoke means target timing alone is not enough; do not launch PPO from these windows.
- This diagnostic preserves rollout timing; it does not test a memoryless obs-to-action clone.
- No robot tests, SSH, deploy, PPO training, or runtime behavior changes were performed.
