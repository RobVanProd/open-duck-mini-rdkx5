# Policy Target Velocity Analysis

telemetry_jsonl: `outputs/first_evidence/20260628T010517Z_corrected_candidate_x008_stand/corrected_candidate_x008_stand.jsonl`
samples_after_startup_filter: `721`
startup_ticks_excluded: `25`
servo_no_load_rad_s_reference: `4.720`
command_first: `(0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)`
command_last: `(0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)`
bus: read_error_count=`6`, write_error_count=`0`, last_error=`read_present_position: Checksum error`

## Pitch-Chain Summary

| joint | sent_vel_p95 | sent_vel_p99 | sent_vel_max | p95_vs_no_load | rate_limit_active | action_delta_p95 | tracking_p95 | lag_ticks | lag_ms | action_sat_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 0.3890 | 0.4334 | 0.4860 | 8.2% | 0.0% | 0.0313 | 0.0136 | 3 | 60.3 | 0.00 |
| left_knee | 0.2778 | 0.3044 | 0.3427 | 5.9% | 0.0% | 0.0223 | 0.0154 | 3 | 60.3 | 0.00 |
| left_ankle | 0.3950 | 0.4709 | 0.5372 | 8.4% | 0.0% | 0.0317 | 0.0154 | 3 | 60.3 | 0.00 |
| right_hip_pitch | 0.3391 | 0.4100 | 0.5433 | 7.2% | 0.0% | 0.0272 | 0.0148 | 3 | 60.3 | 0.00 |
| right_knee | 0.1888 | 0.2494 | 0.2848 | 4.0% | 0.0% | 0.0152 | 0.0126 | 4 | 80.4 | 0.00 |
| right_ankle | 0.2118 | 0.2747 | 0.3027 | 4.5% | 0.0% | 0.0170 | 0.0087 | 3 | 60.3 | 0.00 |

## Detailed Joint Metrics

### left_hip_pitch

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0032 | 0.0078 | 0.0087 | 0.0098 |
| target velocity sent rad/s | 0.1580 | 0.3890 | 0.4334 | 0.4860 |
| pre-rate-limit target velocity rad/s | 0.1580 | 0.3890 | 0.4334 | 0.4860 |
| action delta per tick | 0.0127 | 0.0313 | 0.0348 | 0.0391 |
| tracking error abs rad | 0.0061 | 0.0136 | 0.0149 | 0.0165 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0020`

### left_knee

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0029 | 0.0056 | 0.0061 | 0.0069 |
| target velocity sent rad/s | 0.1423 | 0.2778 | 0.3044 | 0.3427 |
| pre-rate-limit target velocity rad/s | 0.1423 | 0.2778 | 0.3044 | 0.3427 |
| action delta per tick | 0.0114 | 0.0223 | 0.0245 | 0.0275 |
| tracking error abs rad | 0.0057 | 0.0154 | 0.0166 | 0.0179 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0043`

### left_ankle

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0030 | 0.0079 | 0.0095 | 0.0108 |
| target velocity sent rad/s | 0.1476 | 0.3950 | 0.4709 | 0.5372 |
| pre-rate-limit target velocity rad/s | 0.1476 | 0.3950 | 0.4709 | 0.5372 |
| action delta per tick | 0.0119 | 0.0317 | 0.0378 | 0.0432 |
| tracking error abs rad | 0.0040 | 0.0154 | 0.0173 | 0.0201 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0021`

### right_hip_pitch

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0027 | 0.0068 | 0.0082 | 0.0109 |
| target velocity sent rad/s | 0.1368 | 0.3391 | 0.4100 | 0.5433 |
| pre-rate-limit target velocity rad/s | 0.1368 | 0.3391 | 0.4100 | 0.5433 |
| action delta per tick | 0.0110 | 0.0272 | 0.0329 | 0.0437 |
| tracking error abs rad | 0.0039 | 0.0148 | 0.0167 | 0.0189 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0023`

### right_knee

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0015 | 0.0038 | 0.0050 | 0.0057 |
| target velocity sent rad/s | 0.0748 | 0.1888 | 0.2494 | 0.2848 |
| pre-rate-limit target velocity rad/s | 0.0748 | 0.1888 | 0.2494 | 0.2848 |
| action delta per tick | 0.0060 | 0.0152 | 0.0200 | 0.0229 |
| tracking error abs rad | 0.0032 | 0.0126 | 0.0146 | 0.0161 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `4 ticks`, `80.4 ms`, rmse `0.0030`

### right_ankle

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0021 | 0.0043 | 0.0055 | 0.0061 |
| target velocity sent rad/s | 0.1051 | 0.2118 | 0.2747 | 0.3027 |
| pre-rate-limit target velocity rad/s | 0.1051 | 0.2118 | 0.2747 | 0.3027 |
| action delta per tick | 0.0084 | 0.0170 | 0.0221 | 0.0243 |
| tracking error abs rad | 0.0043 | 0.0087 | 0.0110 | 0.0127 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0023`

## Interpretation

- Compare these target velocities against actuator sine sweep velocities before attributing tracking error to ground contact.
