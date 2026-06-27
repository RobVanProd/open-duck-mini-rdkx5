# Warm-Start Seed Failure Analysis

status: `HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY`

Offline trace analysis only. No PPO updates, robot tests, SSH, deploy, or
runtime changes were performed.

## Inputs

- trace: `outputs/analysis/ppo_warmstart_step0_vs_restore_policy_kl100_seed1_trace/ppo_warmstart_step0/seed_001/trace.jsonl`
- manifest: `outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json`
- BC NPZ: `outputs/analysis/pitch_chain_4p3_ppo_shape_rate_student_candidate/candidate_mlp.npz`

## Trace Summary

- samples: `500`
- termination tick: `None`
- first negative vx tick: `0`
- first height below 10 cm tick: `None`
- mean vx: `0.0361` m/s
- min vx: `-0.0678` m/s
- base height min: `0.1556` m
- target velocity p95: `2.2016` rad/s
- joint tracking p95: `0.1742` rad
- action delta p95: `8.8063` /s

Contact percentage:

```text
00: 0.20%
01: 18.40%
10: 18.40%
11: 63.00%
```

## Nearest Manifest Coverage

- nearest distance mean/p95/max: `0.2325` / `0.3598` / `0.5055`
- nearest action L1 mean/p95/max: `0.0277` / `0.0500` / `0.1201`

| source | count | pct |
|---|---:|---:|
| `source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_001.jsonl` | 115 | 23.00 |
| `source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_007.jsonl` | 75 | 15.00 |
| `source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_005.jsonl` | 65 | 13.00 |
| `source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_002.jsonl` | 64 | 12.80 |
| `source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_003.jsonl` | 57 | 11.40 |
| `source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_000.jsonl` | 52 | 10.40 |
| `source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_004.jsonl` | 42 | 8.40 |
| `source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_006.jsonl` | 30 | 6.00 |

## Last 10 Samples

| tick | vx | vy | height | pitch | contacts |
|---:|---:|---:|---:|---:|---|
| 490 | 0.0081 | -0.1169 | 0.1583 | 0.0580 | `11` |
| 491 | -0.0136 | -0.1281 | 0.1574 | 0.0647 | `11` |
| 492 | 0.0307 | -0.0800 | 0.1580 | 0.0727 | `01` |
| 493 | 0.0602 | -0.0350 | 0.1607 | 0.0787 | `11` |
| 494 | 0.0586 | -0.0036 | 0.1638 | 0.0845 | `11` |
| 495 | 0.0611 | 0.0040 | 0.1662 | 0.0919 | `11` |
| 496 | 0.0633 | -0.0187 | 0.1677 | 0.0965 | `11` |
| 497 | 0.0485 | -0.0312 | 0.1682 | 0.0978 | `11` |
| 498 | 0.0287 | -0.0437 | 0.1679 | 0.0972 | `11` |
| 499 | 0.0110 | -0.0466 | 0.1671 | 0.0946 | `11` |

## Decision

Seed failure has nearby manifest support and modest action mismatch; investigate closed-loop stability/contact dynamics.
