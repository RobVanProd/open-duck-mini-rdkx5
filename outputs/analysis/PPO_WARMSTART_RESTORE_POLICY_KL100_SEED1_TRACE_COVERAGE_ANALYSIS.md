# Warm-Start Seed Failure Analysis

status: `HOLD_SEED_FAILURE_ACTION_MISMATCH`

Offline trace analysis only. No PPO updates, robot tests, SSH, deploy, or
runtime changes were performed.

## Inputs

- trace: `outputs/analysis/ppo_warmstart_step0_vs_restore_policy_kl100_seed1_trace/ppo_warmstart_restore_policy_kl100_640/seed_001/trace.jsonl`
- manifest: `outputs/analysis/source_vx_selector_trace_pitch_chain_rate_limited_4p3_manifest.json`
- BC NPZ: `outputs/analysis/pitch_chain_4p3_ppo_shape_rate_student_candidate/candidate_mlp.npz`

## Trace Summary

- samples: `500`
- termination tick: `None`
- first negative vx tick: `0`
- first height below 10 cm tick: `None`
- mean vx: `-0.0006` m/s
- min vx: `-0.1053` m/s
- base height min: `0.1556` m
- target velocity p95: `0.7370` rad/s
- joint tracking p95: `0.0693` rad
- action delta p95: `2.9497` /s

Contact percentage:

```text
00: 0.20%
01: 0.20%
10: 1.80%
11: 97.80%
```

## Nearest Manifest Coverage

- nearest distance mean/p95/max: `1.3746` / `1.5831` / `1.7376`
- nearest action L1 mean/p95/max: `0.1574` / `0.2044` / `0.2662`

| source | count | pct |
|---|---:|---:|
| `source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_004.jsonl` | 367 | 73.40 |
| `source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_003.jsonl` | 96 | 19.20 |
| `source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_006.jsonl` | 13 | 2.60 |
| `source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_001.jsonl` | 8 | 1.60 |
| `source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_005.jsonl` | 7 | 1.40 |
| `source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_000.jsonl` | 5 | 1.00 |
| `source_vx_selector_trace_pitch_chain_rate_limited_4p3_x008_10s_traces/seed_007.jsonl` | 4 | 0.80 |

## Last 10 Samples

| tick | vx | vy | height | pitch | contacts |
|---:|---:|---:|---:|---:|---|
| 490 | -0.0017 | -0.0204 | 0.1573 | 0.0240 | `11` |
| 491 | -0.0057 | -0.0088 | 0.1577 | 0.0310 | `11` |
| 492 | -0.0093 | 0.0007 | 0.1580 | 0.0387 | `11` |
| 493 | -0.0133 | 0.0097 | 0.1583 | 0.0453 | `11` |
| 494 | -0.0178 | 0.0147 | 0.1585 | 0.0496 | `11` |
| 495 | -0.0175 | 0.0226 | 0.1585 | 0.0499 | `11` |
| 496 | -0.0176 | 0.0273 | 0.1585 | 0.0466 | `11` |
| 497 | -0.0143 | 0.0250 | 0.1584 | 0.0414 | `11` |
| 498 | -0.0115 | 0.0192 | 0.1584 | 0.0355 | `11` |
| 499 | -0.0099 | 0.0115 | 0.1583 | 0.0298 | `11` |

## Decision

Seed failure has nearby states but high action mismatch; improve local BC fit/relabeling.
