# Movement Bootstrap V10 Seed Sweep Summary

V10 was trained on an A100 using the `movement_bootstrap_v10` staged recipe.
The final Phase 3 candidate was:

```text
checkpoint: 2026_06_24_024457_153600
onnx_sha256: 54f5619c0a50f8064aa4b11e02b5a66125f0a27526ad83416e8d3e049e92254e
```

Training completed all three stages successfully, but the candidate did not
clear the offline `x=0.08` fitted-bridge seed gate.

## Gate Result

```text
status: HOLD
reason: V10 reduced falls mostly by freezing, not by producing consistent
        forward motion.
robot_touched: no
```

Full local CPU seed-sweep output:

```text
outputs/analysis/v10_local_cpu_seed_sweep_20260624T032754Z/V10_CANDIDATE_SEED_SWEEP.md
```

## Eight-Seed Result

| seed | status | samples | termination | track ratio | base height min |
|---:|---|---:|---|---:|---:|
| 0 | HOLD_CANDIDATE_LOW_FORWARD_PROGRESS | 750 | duration_complete | 0.0192 | 0.1511 |
| 1 | HOLD_CANDIDATE_FALL_OR_TERMINATION | 31 | fall_or_nan | 0.0567 | 0.0673 |
| 2 | HOLD_CANDIDATE_LOW_FORWARD_PROGRESS | 750 | duration_complete | 0.0241 | 0.1512 |
| 3 | HOLD_CANDIDATE_LOW_FORWARD_PROGRESS | 750 | duration_complete | 0.0015 | 0.1512 |
| 4 | HOLD_CANDIDATE_LOW_FORWARD_PROGRESS | 750 | duration_complete | 0.0377 | 0.1491 |
| 5 | HOLD_CANDIDATE_FALL_OR_TERMINATION | 54 | fall_or_nan | -3.8890 | 0.0332 |
| 6 | HOLD_CANDIDATE_LOW_FORWARD_PROGRESS | 750 | duration_complete | 0.0072 | 0.1508 |
| 7 | HOLD_CANDIDATE_FALL_OR_TERMINATION | 27 | fall_or_nan | 0.0544 | 0.0911 |

Distribution:

```text
runs: 8
falls: 3
duration_complete: 5
samples_mean: 482.75
track_ratio_mean: -0.4610
mean_local_vx_m_s: -0.0369
```

## Interpretation

V10 improved lifetime versus the V7/V9 baseline, but it did so by increasing
standstill completions:

```text
V7/V9 baseline: 5/8 falls, 3/8 standstill completions, mean ~312 samples
V10:            3/8 falls, 5/8 standstill completions, mean 482.75 samples
```

This is not a useful candidate. It did not produce consistent in-envelope
forward motion. Seed 5 also shows a strong reverse-motion failure, so the
wrong-direction regime was not eliminated.

## Decision

Stop iterating on the current V7/V9/V10 anchor lineage as the primary path.
The continuity/stabilization recipe can preserve posture, but it keeps
collapsing the gait into standstill or reverse/collapse regimes.

Next work should switch to a structurally different bootstrap or objective that
establishes one coherent forward behavior across seeds before applying strong
stability consolidation.

No robot validation is allowed from this candidate.
