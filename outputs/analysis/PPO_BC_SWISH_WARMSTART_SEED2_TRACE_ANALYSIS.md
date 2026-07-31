# Warm-Start Seed Failure Analysis

status: `HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY`

Offline trace analysis only. No PPO updates, robot tests, SSH, deploy, or
runtime changes were performed.

## Inputs

- trace: `outputs/analysis/candidate_seed_sweep/ppo_swish_step0/seed_002/trace.jsonl`
- manifest: `outputs/analysis/source_vx_selector_trace_dagger3_manifest.json`
- BC NPZ: `outputs/analysis/ppo_loc_swish_bc_student_candidate/candidate_mlp.npz`

## Trace Summary

- samples: `500`
- termination tick: `None`
- first negative vx tick: `32`
- first height below 10 cm tick: `None`
- mean vx: `0.0458` m/s
- min vx: `-0.0501` m/s
- base height min: `0.1509` m
- target velocity p95: `2.1970` rad/s
- joint tracking p95: `0.1842` rad
- action delta p95: `8.7881` /s

Contact percentage:

```text
01: 20.00%
10: 18.80%
11: 61.20%
```

## Nearest Manifest Coverage

- nearest distance mean/p95/max: `0.2583` / `0.4155` / `0.6787`
- nearest action L1 mean/p95/max: `0.0194` / `0.0400` / `0.1020`

| source | count | pct |
|---|---:|---:|
| `source_vx_selector_trace_dagger2_rate_reg_standard_relabel_blend_x008_10s_traces/trace.jsonl` | 490 | 98.00 |
| `source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_002.jsonl` | 6 | 1.20 |
| `source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_002.jsonl` | 2 | 0.40 |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_002.jsonl` | 2 | 0.40 |

## Last 10 Samples

| tick | vx | vy | height | pitch | contacts |
|---:|---:|---:|---:|---:|---|
| 490 | 0.0301 | -0.1101 | 0.1580 | 0.0673 | `11` |
| 491 | 0.0395 | -0.0537 | 0.1588 | 0.0773 | `01` |
| 492 | 0.0573 | -0.0079 | 0.1613 | 0.0860 | `11` |
| 493 | 0.0558 | 0.0188 | 0.1641 | 0.0923 | `11` |
| 494 | 0.0658 | 0.0037 | 0.1664 | 0.0969 | `11` |
| 495 | 0.0708 | -0.0210 | 0.1679 | 0.0985 | `11` |
| 496 | 0.0542 | -0.0406 | 0.1685 | 0.0990 | `11` |
| 497 | 0.0369 | -0.0694 | 0.1683 | 0.0984 | `11` |
| 498 | 0.0153 | -0.1042 | 0.1675 | 0.0957 | `11` |
| 499 | -0.0050 | -0.1047 | 0.1662 | 0.0908 | `11` |

## Decision

Seed failure has nearby manifest support and modest action mismatch; investigate closed-loop stability/contact dynamics.
