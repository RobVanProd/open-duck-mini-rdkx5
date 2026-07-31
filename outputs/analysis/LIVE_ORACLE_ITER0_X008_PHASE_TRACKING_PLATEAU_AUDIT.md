# Live-Oracle Iter0 X008 Phase Tracking Plateau Audit

status: `PASS_PHASE_TRACKING_PLATEAU_AUDIT`

samples: `6000`

## Summary

- all-sample max pitch tracking p95: `0.2454` rad
- all-sample max pitch sent velocity p95: `3.6586` rad/s

| phase_bin | samples | max_tracking_p95 | max_sent_vel_p95 | dominant_tracking_joint | dominant_tracking_p95 |
|---:|---:|---:|---:|---|---:|
| 0 | 1568 | 0.2504 | 3.7406 | `right_knee` | 0.2504 |
| 1 | 1568 | 0.2567 | 3.9081 | `right_knee` | 0.2567 |
| 2 | 1568 | 0.2413 | 3.4019 | `right_knee` | 0.2413 |
| 3 | 1296 | 0.2370 | 3.3350 | `right_knee` | 0.2370 |

## Interpretation

- The strict tracking plateau is phase-dependent if one bin materially exceeds the others.
- Use this to decide whether a phase-indexed high-command head is worth training before escalating to recurrence.
