# Warm-Start Seed Failure Analysis

status: `HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY`

Offline trace analysis only. No PPO updates, robot tests, SSH, deploy, or
runtime changes were performed.

## Inputs

- trace: `outputs/analysis/dagger6_targeted_recovery_trace_x008_fitted_10s/dagger6/seed_001/trace.jsonl`
- manifest: `outputs/analysis/filtered_source_vx_selector_dagger7_targeted_recovery_manifest.json`
- BC NPZ: `outputs/analysis/source_vx_selector_trace_dagger7_targeted_recovery_mlp128_rate_reg_candidate/candidate_mlp.npz`

## Trace Summary

- samples: `32`
- termination tick: `31`
- first negative vx tick: `0`
- first height below 10 cm tick: `30`
- mean vx: `0.0108` m/s
- min vx: `-0.0696` m/s
- base height min: `0.0775` m
- target velocity p95: `2.1766` rad/s
- joint tracking p95: `0.1751` rad
- action delta p95: `8.7065` /s

Contact percentage:

```text
00: 9.38%
10: 84.38%
11: 6.25%
```

## Nearest Manifest Coverage

- nearest distance mean/p95/max: `0.0129` / `0.0000` / `0.4130`
- nearest action L1 mean/p95/max: `0.0557` / `0.0736` / `0.1094`

| source | count | pct |
|---|---:|---:|
| `seed_001/trace.jsonl` | 32 | 100.00 |

## Last 10 Samples

| tick | vx | vy | height | pitch | contacts |
|---:|---:|---:|---:|---:|---|
| 22 | 0.0565 | 0.5657 | 0.1768 | -0.0957 | `10` |
| 23 | 0.0749 | 0.6309 | 0.1739 | -0.0917 | `10` |
| 24 | 0.0827 | 0.7003 | 0.1696 | -0.0893 | `10` |
| 25 | 0.0845 | 0.7840 | 0.1634 | -0.0857 | `10` |
| 26 | 0.0902 | 0.8730 | 0.1547 | -0.0789 | `10` |
| 27 | 0.0975 | 0.9697 | 0.1436 | -0.0678 | `10` |
| 28 | 0.0678 | 1.0773 | 0.1306 | -0.0620 | `10` |
| 29 | 0.0515 | 1.2019 | 0.1152 | -0.0624 | `00` |
| 30 | 0.0309 | 1.3054 | 0.0974 | -0.0704 | `10` |
| 31 | 0.0054 | 1.3568 | 0.0775 | -0.0764 | `00` |

## Decision

Seed failure has nearby manifest support and modest action mismatch; investigate closed-loop stability/contact dynamics.
