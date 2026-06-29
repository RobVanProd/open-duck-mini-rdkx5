# Phase 2 z=0.005 Seed-5 Failure Diagnostic

status: `HOLD_Z005_SEED5_SUPPORT_COLLAPSE_DIAGNOSED`

This is an offline read-only diagnostic. It did not train, SSH, deploy, or touch the robot.

## Comparison

| command | samples | termination | mean vx | track ratio | base height min | body pitch p95 | double support | single support | max sent vel p95 | max tracking p95 | vel excess |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.080 | 56 | `fall_or_nan` | -0.2654 | -3.3180 | 0.0677 | -0.0683 | 91.0714 | 7.1429 | 1.9250 | 0.1968 | 0.0000 |
| 0.000 | 61 | `fall_or_nan` | -0.2589 | NA | 0.0512 | -0.0759 | 85.2459 | 8.1967 | 1.2575 | 0.1953 | 0.0000 |

## Swing / Contact

| command | left segments | right segments | left lift | right lift | left rel-x p95 | right rel-x p95 |
|---:|---:|---:|---:|---:|---:|---:|
| 0.080 | 0 | 1 | 0.0286 | 0.0429 | NA | 0.0084 |
| 0.000 | 2 | 3 | 0.0308 | 0.0419 | 0.0080 | 0.0080 |

## Findings

- `x008`: falls before 1.3s, base-height collapse, no corrected-envelope velocity excess, low target-rate demand, double-support dominated, backward drift/collapse
- `x000`: falls before 1.3s, base-height collapse, no corrected-envelope velocity excess, low target-rate demand, double-support dominated, backward drift/collapse
- `shared`: seed 5 collapses vertically on z=0.005 in both command modes, failure is backward-biased even at zero command, failure is not caused by corrected-envelope velocity excess, support pattern is double-support dominated before collapse

## Recommendation

The next z=0.005 support recipe should target seed-5 terrain support and base-height margin while preserving the z=0.002 gait. Do not treat this as an actuator-envelope or action-saturation problem.

Do not advance to z=0.005 push, stronger terrain, or robot validation from this candidate.
