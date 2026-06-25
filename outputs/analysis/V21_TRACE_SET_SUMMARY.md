# Candidate Trace Set Summary

status: `HOLD_TRACE_SET_LOW_COMMAND_FAILURES`

## Aggregate

- action_saturation_pct_mean: `0.0000`
- base_height_min_mean_m: `0.1393`
- falls_or_terminations: `4`
- mean_local_vx_m_s: `-0.0249`
- samples_mean: `61`
- track_ratio_mean: `-0.6216`

## Failure Surfaces

| surface | count |
|---|---:|
| `LOW_PROGRESS_TERMINATION` | 3 |
| `REVERSE_HEIGHT_COLLAPSE` | 1 |

## Per-Seed Rows

| seed | surface | samples | mean_vx | track_ratio | base_height_min | first_reverse_tick | first_low_height_tick | dominant_cost |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 0 | `LOW_PROGRESS_TERMINATION` | 70 | -0.0011 | -0.0269 | 0.1536 | 0 | NA | `cost/forward_shortfall=33.1709` |
| 1 | `REVERSE_HEIGHT_COLLAPSE` | 34 | -0.0870 | -2.1760 | 0.0919 | 0 | 32 | `cost/forward_wrong_direction=675.0524` |
| 2 | `LOW_PROGRESS_TERMINATION` | 70 | 0.0059 | 0.1478 | 0.1526 | 6 | NA | `cost/forward_shortfall=17.2315` |
| 3 | `LOW_PROGRESS_TERMINATION` | 70 | -0.0172 | -0.4312 | 0.1589 | 0 | NA | `cost/forward_shortfall=94.6439` |

## Interpretation

The trace set should be read as an offline sim diagnosis only. It does not
approve robot testing. Low target velocity and zero action saturation mean
these failures are behavior discovery/stability failures, not actuator
envelope failures.
