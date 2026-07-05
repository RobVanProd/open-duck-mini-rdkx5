# Warm-Start Seed Failure Analysis

status: `HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY`

Offline trace analysis only. No PPO updates, robot tests, SSH, deploy, or
runtime changes were performed.

## Inputs

- trace: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_step0_trace_seed0_1_6_7/ppo_step0/seed_007/trace.jsonl`
- manifest: `outputs/analysis/live_oracle_dagger_phase_student/iter_024_history_context_resetsettle10_seed2_active/live_oracle_dagger_aggregate_manifest.json`
- BC NPZ: `outputs/analysis/ppo_loc_iter24_live_oracle_seed2_active_rate150_candidate/candidate_mlp.npz`

## Trace Summary

- samples: `577`
- termination tick: `576`
- first negative vx tick: `44`
- first height below 10 cm tick: `571`
- mean vx: `0.0542` m/s
- min vx: `-0.0721` m/s
- base height min: `0.0033` m
- target velocity p95: `1.4236` rad/s
- joint tracking p95: `0.1382` rad
- action delta p95: `5.6943` /s

Contact percentage:

```text
00: 0.69%
01: 6.24%
10: 16.81%
11: 76.26%
```

## Nearest Manifest Coverage

- nearest distance mean/p95/max: `0.1535` / `0.2228` / `0.6520`
- nearest action L1 mean/p95/max: `0.0113` / `0.0247` / `0.1104`

| source | count | pct |
|---|---:|---:|
| `rollouts_x008/student/seed_007/trace.jsonl` | 174 | 30.16 |
| `rollouts_x008/student/seed_001/trace.jsonl` | 96 | 16.64 |
| `rollouts_x008/student/seed_006/trace.jsonl` | 81 | 14.04 |
| `rollouts_x008/student/seed_002/trace.jsonl` | 57 | 9.88 |
| `rollouts_x008/student/seed_000/trace.jsonl` | 52 | 9.01 |
| `phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_004/trace.jsonl` | 18 | 3.12 |
| `relabel_x008/rollouts_x008/student/seed_007/trace.jsonl` | 11 | 1.91 |
| `phase2_z0075_iter2_seed7_pass_control_weighted/phase2_z0075_iter2_recovery_rate150_seed7_trace_control/iter2_recovery_rate150/seed_007/trace.jsonl` | 10 | 1.73 |

## Last 10 Samples

| tick | vx | vy | height | pitch | contacts |
|---:|---:|---:|---:|---:|---|
| 567 | 0.6894 | 0.0346 | 0.1327 | 0.7922 | `10` |
| 568 | 0.7697 | 0.0178 | 0.1261 | 0.8449 | `11` |
| 569 | 0.8568 | -0.0095 | 0.1178 | 0.9043 | `10` |
| 570 | 0.9411 | -0.0335 | 0.1076 | 0.9718 | `11` |
| 571 | 1.0425 | -0.0414 | 0.0955 | 1.0514 | `00` |
| 572 | 1.1291 | -0.0719 | 0.0813 | 1.1415 | `10` |
| 573 | 1.2285 | -0.1036 | 0.0652 | 1.2400 | `01` |
| 574 | 1.3253 | -0.0992 | 0.0468 | 1.3461 | `00` |
| 575 | 1.4222 | -0.1618 | 0.0262 | 1.4400 | `00` |
| 576 | 1.5008 | -0.1270 | 0.0033 | 1.4274 | `00` |

## Decision

Seed failure has nearby manifest support and modest action mismatch; investigate closed-loop stability/contact dynamics.
