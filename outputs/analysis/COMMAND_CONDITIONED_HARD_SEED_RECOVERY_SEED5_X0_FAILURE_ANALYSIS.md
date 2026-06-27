# Warm-Start Seed Failure Analysis

status: `HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY`

Offline trace analysis only. No PPO updates, robot tests, SSH, deploy, or
runtime changes were performed.

## Inputs

- trace: `outputs/analysis/command_conditioned_hard_seed_recovery/seed5_x0_trace/command_conditioned_hard_seed_recovery_candidate/seed_005/trace.jsonl`
- manifest: `outputs/analysis/command_conditioned_hard_seed_recovery_manifest.json`
- BC NPZ: `outputs/analysis/command_conditioned_hard_seed_recovery_candidate/candidate_mlp.npz`

## Trace Summary

- samples: `73`
- termination tick: `72`
- first negative vx tick: `9`
- first height below 10 cm tick: `70`
- mean vx: `-0.2176` m/s
- min vx: `-1.5401` m/s
- base height min: `0.0464` m
- target velocity p95: `0.7501` rad/s
- joint tracking p95: `0.0803` rad
- action delta p95: `3.0004` /s

Contact percentage:

```text
00: 6.85%
01: 6.85%
10: 6.85%
11: 79.45%
```

## Nearest Manifest Coverage

- nearest distance mean/p95/max: `0.4706` / `1.8015` / `2.4739`
- nearest action L1 mean/p95/max: `0.0363` / `0.0820` / `0.1619`

| source | count | pct |
|---|---:|---:|
| `seed_005/trace.jsonl` | 42 | 57.53 |
| `seed_003/trace.jsonl` | 19 | 26.03 |
| `seed_004/trace.jsonl` | 6 | 8.22 |
| `seed_007/trace.jsonl` | 5 | 6.85 |
| `seed_006/trace.jsonl` | 1 | 1.37 |

## Last 10 Samples

| tick | vx | vy | height | pitch | contacts |
|---:|---:|---:|---:|---:|---|
| 63 | -0.6929 | -0.0181 | 0.1640 | -0.7675 | `10` |
| 64 | -0.7766 | -0.0180 | 0.1591 | -0.8345 | `01` |
| 65 | -0.8621 | -0.0150 | 0.1528 | -0.9087 | `10` |
| 66 | -0.9578 | -0.0105 | 0.1449 | -0.9912 | `10` |
| 67 | -1.0457 | -0.0028 | 0.1355 | -1.0869 | `01` |
| 68 | -1.1547 | 0.0008 | 0.1237 | -1.1938 | `11` |
| 69 | -1.2682 | -0.0001 | 0.1093 | -1.3125 | `01` |
| 70 | -1.3743 | -0.0152 | 0.0917 | -1.4407 | `00` |
| 71 | -1.4650 | -0.0160 | 0.0708 | -1.5482 | `00` |
| 72 | -1.5401 | -0.0326 | 0.0464 | -1.4061 | `00` |

## Decision

Seed failure has nearby manifest support and modest action mismatch; investigate closed-loop stability/contact dynamics.
