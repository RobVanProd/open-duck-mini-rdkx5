# Closed-Loop Teacher Template

overall_status: `PASS_HAS_LOW_RATE_MOVING_TEACHER_WINDOWS`

## Summary

| command_cell | traces | mean_vx | single_% | in_envelope_% | moving_% | moving_in_envelope_% | moving_single_in_envelope_% | single_dvx | safe_moving_single_dvx | pitch_vel_p95 | pitch_vel_max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| straight_x004 | 8 | 0.0019 | 3.6500 | 96.5500 | 6.6500 | 4.6500 | 1.2500 | -0.0155 | -0.0483 | 2.3441 | 5.2400 |
| straight_x008 | 8 | 0.0640 | 49.4000 | 78.4000 | 89.5500 | 70.5500 | 32.8000 | 0.0030 | 0.0039 | 5.1961 | 5.2400 |
| upstream_nearest_turn | 8 | 0.0540 | 44.8000 | 78.4500 | 82.1500 | 63.7000 | 28.9000 | 0.0042 | 0.0034 | 4.9472 | 5.2400 |

## Interpretation

The traces contain moving low-rate windows that may be usable as a constrained teacher subset. Validate these windows before training.

Robot validation remains blocked.
