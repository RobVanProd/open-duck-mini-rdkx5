# Policy Target Velocity Analysis

telemetry_jsonl: `outputs/first_evidence/20260628T011648Z_corrected_candidate_x008_grounded_first/corrected_candidate_x008_grounded_first.jsonl`
samples_after_startup_filter: `223`
startup_ticks_excluded: `25`
servo_no_load_rad_s_reference: `4.720`
command_first: `(0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)`
command_last: `(0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)`
bus: read_error_count=`12`, write_error_count=`0`, last_error=`read_present_position: Checksum error`

## Pitch-Chain Summary

| joint | sent_vel_p95 | sent_vel_p99 | sent_vel_max | p95_vs_no_load | rate_limit_active | action_delta_p95 | tracking_p95 | lag_ticks | lag_ms | action_sat_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 1.5108 | 2.0939 | 2.1442 | 32.0% | 0.0% | 0.1214 | 0.0743 | 4 | 80.3 | 0.00 |
| left_knee | 1.8308 | 2.1860 | 2.2193 | 38.8% | 0.0% | 0.1471 | 0.0970 | 3 | 60.3 | 0.00 |
| left_ankle | 1.3701 | 1.7584 | 1.8553 | 29.0% | 0.0% | 0.1101 | 0.0668 | 3 | 60.3 | 0.00 |
| right_hip_pitch | 1.3175 | 1.6785 | 1.9475 | 27.9% | 0.0% | 0.1059 | 0.0607 | 3 | 60.3 | 0.00 |
| right_knee | 1.7261 | 2.3013 | 2.3894 | 36.6% | 0.0% | 0.1387 | 0.0865 | 4 | 80.3 | 0.00 |
| right_ankle | 1.1679 | 1.8282 | 2.2593 | 24.7% | 0.0% | 0.0938 | 0.0572 | 4 | 80.3 | 0.00 |

## Detailed Joint Metrics

### left_hip_pitch

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0066 | 0.0303 | 0.0421 | 0.0431 |
| target velocity sent rad/s | 0.3285 | 1.5108 | 2.0939 | 2.1442 |
| pre-rate-limit target velocity rad/s | 0.3285 | 1.5108 | 2.0939 | 2.1442 |
| action delta per tick | 0.0264 | 0.1214 | 0.1682 | 0.1723 |
| tracking error abs rad | 0.0170 | 0.0743 | 0.0986 | 0.1116 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `4 ticks`, `80.3 ms`, rmse `0.0164`

### left_knee

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0102 | 0.0368 | 0.0439 | 0.0446 |
| target velocity sent rad/s | 0.5068 | 1.8308 | 2.1860 | 2.2193 |
| pre-rate-limit target velocity rad/s | 0.5068 | 1.8308 | 2.1860 | 2.2193 |
| action delta per tick | 0.0407 | 0.1471 | 0.1757 | 0.1784 |
| tracking error abs rad | 0.0279 | 0.0970 | 0.1250 | 0.1344 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0291`

### left_ankle

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0088 | 0.0275 | 0.0353 | 0.0373 |
| target velocity sent rad/s | 0.4397 | 1.3701 | 1.7584 | 1.8553 |
| pre-rate-limit target velocity rad/s | 0.4397 | 1.3701 | 1.7584 | 1.8553 |
| action delta per tick | 0.0353 | 0.1101 | 0.1413 | 0.1491 |
| tracking error abs rad | 0.0170 | 0.0668 | 0.0832 | 0.0902 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0151`

### right_hip_pitch

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0075 | 0.0265 | 0.0337 | 0.0391 |
| target velocity sent rad/s | 0.3713 | 1.3175 | 1.6785 | 1.9475 |
| pre-rate-limit target velocity rad/s | 0.3713 | 1.3175 | 1.6785 | 1.9475 |
| action delta per tick | 0.0298 | 0.1059 | 0.1349 | 0.1565 |
| tracking error abs rad | 0.0158 | 0.0607 | 0.0853 | 0.0902 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0154`

### right_knee

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0100 | 0.0347 | 0.0462 | 0.0480 |
| target velocity sent rad/s | 0.4979 | 1.7261 | 2.3013 | 2.3894 |
| pre-rate-limit target velocity rad/s | 0.4979 | 1.7261 | 2.3013 | 2.3894 |
| action delta per tick | 0.0400 | 0.1387 | 0.1849 | 0.1920 |
| tracking error abs rad | 0.0242 | 0.0865 | 0.1078 | 0.1239 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `4 ticks`, `80.3 ms`, rmse `0.0183`

### right_ankle

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0073 | 0.0235 | 0.0367 | 0.0454 |
| target velocity sent rad/s | 0.3642 | 1.1679 | 1.8282 | 2.2593 |
| pre-rate-limit target velocity rad/s | 0.3642 | 1.1679 | 1.8282 | 2.2593 |
| action delta per tick | 0.0293 | 0.0938 | 0.1469 | 0.1815 |
| tracking error abs rad | 0.0157 | 0.0572 | 0.0939 | 0.1105 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `4 ticks`, `80.3 ms`, rmse `0.0127`

## Interpretation

- Compare these target velocities against actuator sine sweep velocities before attributing tracking error to ground contact.
