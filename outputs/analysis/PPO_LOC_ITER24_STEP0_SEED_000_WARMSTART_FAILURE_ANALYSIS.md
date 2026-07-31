# Warm-Start Seed Failure Analysis

status: `HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY`

Offline trace analysis only. No PPO updates, robot tests, SSH, deploy, or
runtime changes were performed.

## Inputs

- trace: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_step0_trace_seed0_1_6_7/ppo_step0/seed_000/trace.jsonl`
- manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_024_history_context_resetsettle10_seed2_active/live_oracle_dagger_aggregate_manifest.json`
- BC NPZ: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_candidate/candidate_mlp.npz`

## Trace Summary

- samples: `638`
- termination tick: `637`
- first negative vx tick: `44`
- first height below 10 cm tick: `636`
- mean vx: `0.0015` m/s
- min vx: `-1.3496` m/s
- base height min: `0.0788` m
- target velocity p95: `1.4179` rad/s
- joint tracking p95: `0.1378` rad
- action delta p95: `5.6715` /s

Contact percentage:

```text
00: 0.16%
01: 7.68%
10: 16.77%
11: 75.39%
```

## Nearest Manifest Coverage

- nearest distance mean/p95/max: `0.1468` / `0.2306` / `0.5975`
- nearest action L1 mean/p95/max: `0.0114` / `0.0218` / `0.1104`

| source | count | pct |
|---|---:|---:|
| `rollouts_x008/student/seed_000/trace.jsonl` | 169 | 26.49 |
| `rollouts_x008/student/seed_002/trace.jsonl` | 107 | 16.77 |
| `rollouts_x008/student/seed_007/trace.jsonl` | 72 | 11.29 |
| `rollouts_x008/student/seed_006/trace.jsonl` | 65 | 10.19 |
| `rollouts_x008/student/seed_001/trace.jsonl` | 56 | 8.78 |
| `relabel_x008/rollouts_x008/student/seed_000/trace.jsonl` | 30 | 4.70 |
| `phase2_z0075_iter2_seed7_pass_control_weighted/phase2_z0075_iter2_recovery_rate150_seed7_trace_control/iter2_recovery_rate150/seed_007/trace.jsonl` | 18 | 2.82 |
| `phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_rate150_seed0_trace/iter2_recovery_rate150/seed_000/trace.jsonl` | 14 | 2.19 |

## Last 10 Samples

| tick | vx | vy | height | pitch | contacts |
|---:|---:|---:|---:|---:|---|
| 628 | -0.6450 | -0.0419 | 0.1737 | -0.7275 | `11` |
| 629 | -0.7229 | -0.0472 | 0.1697 | -0.7939 | `11` |
| 630 | -0.7988 | -0.0345 | 0.1647 | -0.8637 | `01` |
| 631 | -0.8771 | -0.0101 | 0.1585 | -0.9378 | `11` |
| 632 | -0.9572 | 0.0249 | 0.1510 | -1.0157 | `11` |
| 633 | -1.0370 | 0.0606 | 0.1416 | -1.0965 | `11` |
| 634 | -1.1256 | 0.1265 | 0.1298 | -1.1778 | `10` |
| 635 | -1.2005 | 0.2145 | 0.1156 | -1.2592 | `11` |
| 636 | -1.2781 | 0.3007 | 0.0987 | -1.3278 | `10` |
| 637 | -1.3496 | 0.3470 | 0.0788 | -1.3468 | `00` |

## Decision

Seed failure has nearby manifest support and modest action mismatch; investigate closed-loop stability/contact dynamics.
