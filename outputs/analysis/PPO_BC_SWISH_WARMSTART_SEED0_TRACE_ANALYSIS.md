# Warm-Start Seed Failure Analysis

status: `HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY`

Offline trace analysis only. No PPO updates, robot tests, SSH, deploy, or
runtime changes were performed.

## Inputs

- trace: `outputs/analysis/candidate_seed_sweep/ppo_swish_step0/seed_000/trace.jsonl`
- manifest: `outputs/analysis/source_vx_selector_trace_dagger3_manifest.json`
- BC NPZ: `outputs/analysis/ppo_loc_swish_bc_student_candidate/candidate_mlp.npz`

## Trace Summary

- samples: `500`
- termination tick: `None`
- first negative vx tick: `0`
- first height below 10 cm tick: `None`
- mean vx: `0.0458` m/s
- min vx: `-0.0495` m/s
- base height min: `0.1520` m
- target velocity p95: `2.1786` rad/s
- joint tracking p95: `0.1813` rad
- action delta p95: `8.7145` /s

Contact percentage:

```text
01: 22.20%
10: 17.00%
11: 60.80%
```

## Nearest Manifest Coverage

- nearest distance mean/p95/max: `0.2724` / `0.4358` / `0.6516`
- nearest action L1 mean/p95/max: `0.0203` / `0.0411` / `0.1451`

| source | count | pct |
|---|---:|---:|
| `source_vx_selector_trace_dagger2_rate_reg_standard_relabel_blend_x008_10s_traces/trace.jsonl` | 493 | 98.60 |
| `source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_000.jsonl` | 5 | 1.00 |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_000.jsonl` | 2 | 0.40 |

## Last 10 Samples

| tick | vx | vy | height | pitch | contacts |
|---:|---:|---:|---:|---:|---|
| 490 | 0.0592 | 0.0005 | 0.1648 | 0.1034 | `11` |
| 491 | 0.0645 | -0.0287 | 0.1669 | 0.1033 | `11` |
| 492 | 0.0482 | -0.0510 | 0.1680 | 0.1037 | `11` |
| 493 | 0.0348 | -0.0671 | 0.1682 | 0.1044 | `11` |
| 494 | 0.0140 | -0.0892 | 0.1676 | 0.1042 | `11` |
| 495 | -0.0085 | -0.1066 | 0.1664 | 0.1015 | `11` |
| 496 | -0.0018 | -0.1029 | 0.1653 | 0.0959 | `11` |
| 497 | 0.0021 | -0.0673 | 0.1642 | 0.0887 | `01` |
| 498 | 0.0056 | -0.0263 | 0.1633 | 0.0802 | `01` |
| 499 | 0.0071 | 0.0121 | 0.1625 | 0.0707 | `01` |

## Decision

Seed failure has nearby manifest support and modest action mismatch; investigate closed-loop stability/contact dynamics.
