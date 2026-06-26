# Warm-Start Seed Failure Analysis

status: `HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY`

Offline trace analysis only. No PPO updates, robot tests, SSH, deploy, or
runtime changes were performed.

## Inputs

- trace: `outputs/analysis/candidate_seed_sweep/ppo_swish_seed5_recovery_step0/seed_005/trace.jsonl`
- manifest: `outputs/analysis/ppo_swish_seed5_recovery_manifest.json`
- BC NPZ: `outputs/analysis/ppo_loc_swish_seed5_recovery_candidate/candidate_mlp.npz`

## Trace Summary

- samples: `75`
- termination tick: `74`
- first negative vx tick: `10`
- first height below 10 cm tick: `74`
- mean vx: `-0.1893` m/s
- min vx: `-1.5043` m/s
- base height min: `0.0777` m
- target velocity p95: `1.8172` rad/s
- joint tracking p95: `0.1679` rad
- action delta p95: `7.2690` /s

Contact percentage:

```text
00: 9.33%
01: 5.33%
10: 5.33%
11: 80.00%
```

## Nearest Manifest Coverage

- nearest distance mean/p95/max: `0.3168` / `0.6022` / `0.6492`
- nearest action L1 mean/p95/max: `0.0229` / `0.0409` / `0.0631`

| source | count | pct |
|---|---:|---:|
| `ppo_swish_seed5_relabel_blend_traces/trace.jsonl` | 71 | 94.67 |
| `source_vx_selector_trace_dagger2_rate_reg_standard_relabel_blend_x008_10s_traces/trace.jsonl` | 4 | 5.33 |

## Last 10 Samples

| tick | vx | vy | height | pitch | contacts |
|---:|---:|---:|---:|---:|---|
| 65 | -0.5946 | -0.0056 | 0.1691 | -0.7115 | `11` |
| 66 | -0.6351 | -0.0375 | 0.1679 | -0.7723 | `01` |
| 67 | -0.7035 | -0.0664 | 0.1657 | -0.8454 | `10` |
| 68 | -0.7875 | -0.0856 | 0.1616 | -0.9251 | `00` |
| 69 | -0.8917 | -0.1035 | 0.1551 | -1.0121 | `00` |
| 70 | -1.0008 | -0.1252 | 0.1460 | -1.1064 | `00` |
| 71 | -1.1359 | -0.1444 | 0.1340 | -1.2080 | `01` |
| 72 | -1.2693 | -0.1640 | 0.1188 | -1.3160 | `11` |
| 73 | -1.3937 | -0.1874 | 0.1001 | -1.4241 | `00` |
| 74 | -1.5043 | -0.1814 | 0.0777 | -1.4773 | `00` |

## Decision

Seed failure has nearby manifest support and modest action mismatch; investigate closed-loop stability/contact dynamics.
