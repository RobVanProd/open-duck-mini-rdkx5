# Warm-Start Seed Failure Analysis

status: `HOLD_SEED_FAILURE_ACTION_MISMATCH`

Offline trace analysis only. No PPO updates, robot tests, SSH, deploy, or
runtime changes were performed.

## Inputs

- trace: `outputs/analysis/dagger6_targeted_recovery_trace_x008_fitted_10s/dagger6/seed_007/trace.jsonl`
- manifest: `outputs/analysis/filtered_source_vx_selector_dagger7_targeted_recovery_manifest.json`
- BC NPZ: `outputs/analysis/source_vx_selector_trace_dagger7_targeted_recovery_mlp128_rate_reg_candidate/candidate_mlp.npz`

## Trace Summary

- samples: `33`
- termination tick: `32`
- first negative vx tick: `0`
- first height below 10 cm tick: `31`
- mean vx: `0.0264` m/s
- min vx: `-0.0794` m/s
- base height min: `0.0730` m
- target velocity p95: `2.0073` rad/s
- joint tracking p95: `0.1681` rad
- action delta p95: `8.0291` /s

Contact percentage:

```text
00: 6.06%
01: 84.85%
11: 9.09%
```

## Nearest Manifest Coverage

- nearest distance mean/p95/max: `0.0147` / `0.0000` / `0.4848`
- nearest action L1 mean/p95/max: `0.0635` / `0.1290` / `0.1415`

| source | count | pct |
|---|---:|---:|
| `seed_007/trace.jsonl` | 33 | 100.00 |

## Last 10 Samples

| tick | vx | vy | height | pitch | contacts |
|---:|---:|---:|---:|---:|---|
| 23 | 0.0613 | -0.6161 | 0.1709 | 0.0152 | `01` |
| 24 | 0.0509 | -0.6639 | 0.1677 | 0.0136 | `01` |
| 25 | 0.0251 | -0.7205 | 0.1636 | 0.0080 | `01` |
| 26 | 0.0013 | -0.7911 | 0.1584 | -0.0011 | `01` |
| 27 | -0.0127 | -0.8763 | 0.1513 | -0.0110 | `01` |
| 28 | -0.0299 | -0.9615 | 0.1420 | -0.0184 | `01` |
| 29 | -0.0380 | -1.0481 | 0.1298 | -0.0165 | `01` |
| 30 | -0.0352 | -1.1341 | 0.1142 | -0.0024 | `00` |
| 31 | -0.0188 | -1.2256 | 0.0949 | 0.0231 | `01` |
| 32 | 0.0160 | -1.3233 | 0.0730 | 0.0455 | `00` |

## Decision

Seed failure has nearby states but high action mismatch; improve local BC fit/relabeling.
