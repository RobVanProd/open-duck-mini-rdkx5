# PPO BC Swish Warm-Start Seed Comparison

status: `HOLD_SEED5_WEAK_COVERAGE_AND_CLOSED_LOOP_COLLAPSE`

This is an offline trace comparison. It did not run PPO updates, SSH, deploy,
run robot tests, or change robot runtime behavior.

## Inputs

Successful traces:

```text
outputs/analysis/PPO_BC_SWISH_WARMSTART_SUCCESS_TRACE_GATE.md
seeds: 0,2
```

Failing trace:

```text
outputs/analysis/PPO_BC_SWISH_WARMSTART_SEED5_TRACE_GATE.md
seed: 5
```

Per-seed analyses:

```text
outputs/analysis/PPO_BC_SWISH_WARMSTART_SEED0_TRACE_ANALYSIS.md
outputs/analysis/PPO_BC_SWISH_WARMSTART_SEED2_TRACE_ANALYSIS.md
outputs/analysis/PPO_BC_SWISH_WARMSTART_SEED5_FAILURE_ANALYSIS.md
```

## Comparison

| metric | seed 0 | seed 2 | seed 5 |
|---|---:|---:|---:|
| samples | 500 | 500 | 74 |
| mean vx m/s | 0.0458 | 0.0458 | -0.1976 |
| min vx m/s | -0.0495 | -0.0501 | -1.4579 |
| first negative vx tick | 0 | 32 | 10 |
| first height < 0.10m tick | NA | NA | 72 |
| min height m | 0.1520 | 0.1509 | 0.0717 |
| final pitch rad | 0.0707 | 0.0908 | -1.4801 |
| target velocity p95 rad/s | 2.1786 | 2.1970 | 1.7630 |
| tracking p95 rad | 0.1813 | 0.1842 | 0.1760 |
| nearest manifest distance p95 | 0.4358 | 0.4155 | 1.0276 |
| nearest action L1 p95 | 0.0411 | 0.0400 | 0.0783 |
| double support pct | 60.8 | 61.2 | 75.7 |
| no-contact pct | 0.0 | 0.0 | 6.8 |

## Interpretation

Seed 5 is not a target-rate failure:

```text
seed 5 target velocity p95: 1.7630 rad/s
successful seeds target velocity p95: about 2.18-2.20 rad/s
```

Seed 5 is not a fitted tracking spike failure:

```text
seed 5 tracking p95: 0.1760 rad
successful seeds tracking p95: about 0.181-0.184 rad
```

Seed 5 does show weaker local source coverage:

```text
nearest distance p95: 1.0276 vs 0.4155-0.4358
nearest action L1 p95: 0.0783 vs 0.0400-0.0411
```

The physical failure signature is:

```text
early reverse velocity
excess double-support dwell
late no-contact events
backward pitch collapse
base-height collapse
```

## Decision

Do not start PPO from the current swish step-0 checkpoint.

The next candidate improvement should target seed-5-adjacent recovery/stability,
not the export path:

```text
1. add seed-5-adjacent recovery samples or relabeling
2. penalize/relabel reverse velocity and backward pitch collapse
3. reduce double-support dwell for seed-5-like states
4. retrain the swish PPO-loc BC student
5. require 8/8 duration-complete before PPO updates
```

The current result supports a warm-start-data/stability fix before PPO, not a
robot test and not another checkpoint/export debugging pass.
