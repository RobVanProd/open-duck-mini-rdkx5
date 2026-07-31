# Candidate Trace Set Summary

status: `HOLD_TRACE_SET_LOW_COMMAND_FAILURES`

## Aggregate

- action_saturation_pct_mean: `0.0000`
- base_height_min_mean_m: `0.1413`
- falls_or_terminations: `4`
- mean_local_vx_m_s: `-0.0265`
- samples_mean: `60.7500`
- soft_prior_abs_error_mean: `0.2711`
- soft_prior_rms_error_mean: `0.2969`
- track_ratio_mean: `-0.6618`

## Failure Surfaces

| surface | count |
|---|---:|
| `LOW_PROGRESS_TERMINATION` | 3 |
| `REVERSE_HEIGHT_COLLAPSE` | 1 |

## Per-Seed Rows

| seed | surface | samples | mean_vx | track_ratio | prior_abs_err | base_height_min | first_reverse_tick | first_low_height_tick | dominant_cost |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| NA | `LOW_PROGRESS_TERMINATION` | 70 | -0.0018 | -0.0450 | 0.2712 | 0.1537 | 0 | NA | `cost/forward_shortfall=18.4214` |
| NA | `REVERSE_HEIGHT_COLLAPSE` | 33 | -0.0895 | -2.2364 | 0.2734 | 0.1000 | 4 | 31 | `cost/forward_wrong_direction=696.2212` |
| NA | `LOW_PROGRESS_TERMINATION` | 70 | 0.0036 | 0.0889 | 0.2685 | 0.1526 | 6 | NA | `cost/forward_shortfall=11.1184` |
| NA | `LOW_PROGRESS_TERMINATION` | 70 | -0.0182 | -0.4547 | 0.2711 | 0.1588 | 0 | NA | `cost/forward_wrong_direction=81.6103` |

## Interpretation

The trace set should be read as an offline sim diagnosis only. It does not
approve robot testing. Low target velocity and zero action saturation mean
these failures are behavior discovery/stability failures, not actuator
envelope failures.
