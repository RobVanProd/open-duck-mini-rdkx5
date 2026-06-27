# Warm-Start Seed Failure Analysis

status: `HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY`

Offline trace analysis only. No PPO updates, robot tests, SSH, deploy, or
runtime changes were performed.

## Inputs

- trace: `outputs/analysis/candidate_seed_sweep/ppo_swish_step0/seed_005/trace.jsonl`
- manifest: `outputs/analysis/source_vx_selector_trace_dagger3_manifest.json`
- BC NPZ: `outputs/analysis/ppo_loc_swish_bc_student_candidate/candidate_mlp.npz`

## Trace Summary

- samples: `74`
- termination tick: `73`
- first negative vx tick: `10`
- first height below 10 cm tick: `72`
- mean vx: `-0.1976` m/s
- min vx: `-1.4579` m/s
- base height min: `0.0717` m
- target velocity p95: `1.7630` rad/s
- joint tracking p95: `0.1760` rad
- action delta p95: `7.0519` /s

Contact percentage:

```text
00: 6.76%
01: 5.41%
10: 12.16%
11: 75.68%
```

## Nearest Manifest Coverage

- nearest distance mean/p95/max: `0.6114` / `1.0276` / `1.0906`
- nearest action L1 mean/p95/max: `0.0408` / `0.0783` / `0.1111`

| source | count | pct |
|---|---:|---:|
| `source_vx_selector_trace_dagger2_rate_reg_standard_relabel_blend_x008_10s_traces/trace.jsonl` | 45 | 60.81 |
| `source_vx_selector_trace_dagger1_mlp128_relabel_blend_x008_10s_traces/seed_005.jsonl` | 20 | 27.03 |
| `source_vx_selector_fitted_bridge_x008_10s_traces/seed_005.jsonl` | 8 | 10.81 |
| `source_vx_selector_trace_mlp128_relabel_blend_x008_10s_traces/seed_005.jsonl` | 1 | 1.35 |

## Last 10 Samples

| tick | vx | vy | height | pitch | contacts |
|---:|---:|---:|---:|---:|---|
| 64 | -0.6693 | -0.0400 | 0.1662 | -0.7463 | `01` |
| 65 | -0.7333 | -0.0437 | 0.1622 | -0.8064 | `10` |
| 66 | -0.7873 | -0.0471 | 0.1579 | -0.8743 | `01` |
| 67 | -0.8642 | -0.0685 | 0.1524 | -0.9487 | `11` |
| 68 | -0.9360 | -0.0871 | 0.1459 | -1.0355 | `11` |
| 69 | -1.0124 | -0.1138 | 0.1376 | -1.1337 | `00` |
| 70 | -1.1197 | -0.1299 | 0.1263 | -1.2382 | `10` |
| 71 | -1.2389 | -0.1408 | 0.1117 | -1.3492 | `00` |
| 72 | -1.3598 | -0.1328 | 0.0934 | -1.4577 | `10` |
| 73 | -1.4579 | -0.1138 | 0.0717 | -1.4801 | `00` |

## Decision

Seed failure has nearby manifest support and modest action mismatch; investigate closed-loop stability/contact dynamics.
