# Candidate Trace Set Summary

status: `HOLD_TRACE_SET_LOW_COMMAND_FAILURES`

## Aggregate

- action_saturation_pct_mean: `0.0000`
- base_height_min_mean_m: `0.1393`
- falls_or_terminations: `4`
- mean_local_vx_m_s: `-0.0249`
- samples_mean: `61`
- soft_prior_abs_error_mean: `0.2609`
- soft_prior_rms_error_mean: `0.2892`
- track_ratio_mean: `-0.6216`

## Failure Surfaces

| surface | count |
|---|---:|
| `LOW_PROGRESS_TERMINATION` | 3 |
| `REVERSE_HEIGHT_COLLAPSE` | 1 |

## Per-Seed Rows

| seed | surface | samples | mean_vx | track_ratio | prior_abs_err | base_height_min | first_reverse_tick | first_low_height_tick | dominant_cost |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | `LOW_PROGRESS_TERMINATION` | 70 | -0.0011 | -0.0269 | 0.2614 | 0.1536 | 0 | NA | `cost/forward_shortfall=33.1709` |
| 1 | `REVERSE_HEIGHT_COLLAPSE` | 34 | -0.0870 | -2.1760 | 0.2612 | 0.0919 | 0 | 32 | `cost/forward_wrong_direction=675.0524` |
| 2 | `LOW_PROGRESS_TERMINATION` | 70 | 0.0059 | 0.1478 | 0.2577 | 0.1526 | 6 | NA | `cost/forward_shortfall=17.2315` |
| 3 | `LOW_PROGRESS_TERMINATION` | 70 | -0.0172 | -0.4312 | 0.2631 | 0.1589 | 0 | NA | `cost/forward_shortfall=94.6439` |

## Interpretation

The trace set should be read as an offline sim diagnosis only. It does not
approve robot testing. Low target velocity and zero action saturation mean
these failures are behavior discovery/stability failures, not actuator
envelope failures.

The exported policy also does not closely match the soft-prior pitch-chain
action pattern: mean absolute prior error is about `0.261` in normalized action
space across all four seeds. That suggests V21's weak prior shaped the training
run but did not lock the final policy into the intended low-command gait basin.
