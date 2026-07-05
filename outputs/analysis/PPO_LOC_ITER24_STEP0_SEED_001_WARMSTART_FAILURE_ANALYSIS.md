# Warm-Start Seed Failure Analysis

status: `HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY`

Offline trace analysis only. No PPO updates, robot tests, SSH, deploy, or
runtime changes were performed.

## Inputs

- trace: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_step0_trace_seed0_1_6_7/ppo_step0/seed_001/trace.jsonl`
- manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_024_history_context_resetsettle10_seed2_active/live_oracle_dagger_aggregate_manifest.json`
- BC NPZ: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_candidate/candidate_mlp.npz`

## Trace Summary

- samples: `750`
- termination tick: `None`
- first negative vx tick: `44`
- first height below 10 cm tick: `None`
- mean vx: `0.0274` m/s
- min vx: `-0.0804` m/s
- base height min: `0.1583` m
- target velocity p95: `1.4189` rad/s
- joint tracking p95: `0.1396` rad
- action delta p95: `5.6755` /s

Contact percentage:

```text
01: 6.00%
10: 19.47%
11: 74.53%
```

## Nearest Manifest Coverage

- nearest distance mean/p95/max: `0.1515` / `0.2267` / `0.5015`
- nearest action L1 mean/p95/max: `0.0109` / `0.0209` / `0.1104`

| source | count | pct |
|---|---:|---:|
| `rollouts_x008/student/seed_007/trace.jsonl` | 168 | 22.40 |
| `rollouts_x008/student/seed_001/trace.jsonl` | 99 | 13.20 |
| `rollouts_x008/student/seed_002/trace.jsonl` | 99 | 13.20 |
| `rollouts_x008/student/seed_006/trace.jsonl` | 89 | 11.87 |
| `rollouts_x008/student/seed_000/trace.jsonl` | 62 | 8.27 |
| `phase2_z0075_iter2_seed7_pass_control_weighted/phase2_z0075_iter2_recovery_rate150_seed7_trace_control/iter2_recovery_rate150/seed_007/trace.jsonl` | 43 | 5.73 |
| `phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_004/trace.jsonl` | 28 | 3.73 |
| `phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_rate150_seed0_trace/iter2_recovery_rate150/seed_000/trace.jsonl` | 25 | 3.33 |

## Last 10 Samples

| tick | vx | vy | height | pitch | contacts |
|---:|---:|---:|---:|---:|---|
| 740 | -0.0742 | -0.0980 | 0.1671 | -0.0000 | `10` |
| 741 | -0.0605 | -0.1496 | 0.1660 | -0.0041 | `10` |
| 742 | -0.0524 | -0.1831 | 0.1650 | -0.0078 | `11` |
| 743 | -0.0466 | -0.1457 | 0.1647 | -0.0036 | `11` |
| 744 | -0.0055 | -0.0898 | 0.1654 | 0.0050 | `11` |
| 745 | 0.0304 | -0.0347 | 0.1672 | 0.0117 | `11` |
| 746 | 0.0524 | -0.0173 | 0.1692 | 0.0169 | `11` |
| 747 | 0.0663 | -0.0114 | 0.1710 | 0.0209 | `11` |
| 748 | 0.0764 | -0.0079 | 0.1723 | 0.0244 | `11` |
| 749 | 0.0800 | -0.0068 | 0.1730 | 0.0279 | `11` |

## Decision

Seed failure has nearby manifest support and modest action mismatch; investigate closed-loop stability/contact dynamics.
