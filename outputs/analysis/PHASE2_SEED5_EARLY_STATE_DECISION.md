# Phase 2 Seed5 Early-State Correction Decision

status: `HOLD_SEED5_EARLY_STATE_BC_NOT_SUFFICIENT`

This is an offline sim-side analysis. No robot tests, SSH, deploy, grounded
replay, runtime behavior changes, or robot tuning were performed.

## Test

The neighbor trace comparison showed seed 5 diverges before the fall tail at
both x=0.08 and x=0.0. This branch tested a focused early-state correction:

```text
x=0.08 seed5 trace: live-oracle relabel, keep ticks 0-24
x=0.0 seed5 trace: zero-action relabel, keep ticks 0-17
pitch-chain label-rate cap: 2.25 rad/s equivalent
early seed5 entry weight: 10x
base aggregate: seed5-capped aggregate
student: same phase/command-modulated BC architecture
```

## x=0.08 Rough z=0.002 Gate

| seed | status | vx | track ratio | velocity excess | tracking p95 | rel-x p95 |
|---:|---|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TRACKING` | 0.0320 | 0.4001 | 0.0000 | 0.2069 | 0.0019 |
| 1 | `HOLD_CANDIDATE_TRACKING` | 0.0333 | 0.4159 | 0.0000 | 0.2031 | 0.0117 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 0.0395 | 0.4934 | 0.0000 | 0.1998 | 0.0087 |
| 3 | `PASS_CANDIDATE_SIM_GATE` | 0.0291 | 0.3634 | 0.0000 | 0.1946 | 0.0042 |
| 4 | `PASS_CANDIDATE_SIM_GATE` | 0.0361 | 0.4512 | 0.0000 | 0.1977 | 0.0074 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | -0.3300 | -4.1252 | 1.8076 | 0.2281 | 0.0061 |
| 6 | `HOLD_CANDIDATE_TRACKING` | 0.0393 | 0.4912 | 0.0000 | 0.2048 | 0.0195 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 0.0352 | 0.4406 | 0.0000 | 0.1997 | 0.0142 |

Summary:

```text
passes: 4/8
duration_complete: 7/8
falls: 1/8
remaining fall: seed 5
new/regressed holds: seeds 0,1,6 tracking
```

## x=0 Rough z=0.002 Gate

The candidate also failed command-zero robustness:

```text
passes: 7/8
duration_complete: 7/8
falls: 1/8
falling seed: 5
mean vx including fall: -0.0474 m/s
```

## Decision

Early-state BC weighting did not break the seed5 basin and introduced tracking
regressions at x=0.08. Do not continue by simply increasing early seed5 weight
or widening the early tick window.

The evidence now closes two local fixes:

```text
tail-only cap/downweight: improved distribution, seed5 still falls
early-state weighted BC: seed5 still falls and other seeds regress
```

## Next Step

The next useful branch should change the correction mechanism, not only the
sample weights:

- use a recurrent/stateful student or frame-stack path for the seed5 support
  mismatch
- or add a seed5-specific recovery teacher that changes the first contact
  transition, rather than cloning the same phase/command BC map harder
- gate x=0.0 and x=0.08 together because seed5 is command-independent

Robot validation remains blocked.
