# Warm-Start Seed Failure Analysis

status: `HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY`

Offline trace analysis only. No PPO updates, robot tests, SSH, deploy, or
runtime changes were performed.

## Inputs

- trace: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_step0_trace_seed0_1_6_7/ppo_step0/seed_006/trace.jsonl`
- manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_024_history_context_resetsettle10_seed2_active/live_oracle_dagger_aggregate_manifest.json`
- BC NPZ: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_candidate/candidate_mlp.npz`

## Trace Summary

- samples: `212`
- termination tick: `211`
- first negative vx tick: `44`
- first height below 10 cm tick: `210`
- mean vx: `-0.0633` m/s
- min vx: `-1.4036` m/s
- base height min: `0.0724` m
- target velocity p95: `1.3967` rad/s
- joint tracking p95: `0.1312` rad
- action delta p95: `5.5867` /s

Contact percentage:

```text
01: 5.19%
10: 8.49%
11: 86.32%
```

## Nearest Manifest Coverage

- nearest distance mean/p95/max: `0.1953` / `0.3357` / `0.5947`
- nearest action L1 mean/p95/max: `0.0137` / `0.0271` / `0.1104`

| source | count | pct |
|---|---:|---:|
| `rollouts_x008/student/seed_001/trace.jsonl` | 35 | 16.51 |
| `rollouts_x008/student/seed_006/trace.jsonl` | 33 | 15.57 |
| `phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_006/push_010_712c01db7c0c749d.jsonl` | 28 | 13.21 |
| `rollouts_x008/student/seed_000/trace.jsonl` | 26 | 12.26 |
| `rollouts_x008/student/seed_007/trace.jsonl` | 20 | 9.43 |
| `phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_001/trace.jsonl` | 18 | 8.49 |
| `rollouts_x008/student/seed_002/trace.jsonl` | 14 | 6.60 |
| `phase2_z0075_iter21_seed5_postpush_regressed_seed_push_snippets_relabelled/analysis/phase2_z0075_iter21_seed5_postpush_regressed_seed_push_snippets/seed_003/push_007_12b13233187b9b65.jsonl` | 9 | 4.25 |

## Last 10 Samples

| tick | vx | vy | height | pitch | contacts |
|---:|---:|---:|---:|---:|---|
| 202 | -0.6400 | -0.0397 | 0.1756 | -0.7515 | `11` |
| 203 | -0.7157 | -0.0300 | 0.1713 | -0.8197 | `11` |
| 204 | -0.8052 | -0.0265 | 0.1659 | -0.8929 | `11` |
| 205 | -0.8996 | -0.0153 | 0.1590 | -0.9705 | `11` |
| 206 | -0.9912 | 0.0042 | 0.1505 | -1.0531 | `11` |
| 207 | -1.0734 | 0.0385 | 0.1401 | -1.1413 | `11` |
| 208 | -1.1754 | 0.0890 | 0.1274 | -1.2329 | `11` |
| 209 | -1.2611 | 0.1540 | 0.1119 | -1.3241 | `10` |
| 210 | -1.3432 | 0.2165 | 0.0936 | -1.3957 | `11` |
| 211 | -1.4036 | 0.2745 | 0.0724 | -1.3871 | `10` |

## Decision

Seed failure has nearby manifest support and modest action mismatch; investigate closed-loop stability/contact dynamics.
