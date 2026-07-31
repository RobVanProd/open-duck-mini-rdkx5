# Policy Target Velocity Analysis

telemetry_jsonl: `outputs/first_evidence/20260628T012023Z_corrected_candidate_x008_grounded_second_surface/corrected_candidate_x008_grounded_second_surface.jsonl`
samples_after_startup_filter: `223`
startup_ticks_excluded: `25`
servo_no_load_rad_s_reference: `4.720`
command_first: `(0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)`
command_last: `(0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)`
bus: read_error_count=`6`, write_error_count=`0`, last_error=`read_present_velocity: Checksum error`

## Pitch-Chain Summary

| joint | sent_vel_p95 | sent_vel_p99 | sent_vel_max | p95_vs_no_load | rate_limit_active | action_delta_p95 | tracking_p95 | lag_ticks | lag_ms | action_sat_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 0.7508 | 1.1715 | 1.3547 | 15.9% | 0.0% | 0.0603 | 0.0426 | 4 | 80.4 | 0.00 |
| left_knee | 1.2104 | 1.6005 | 1.6355 | 25.6% | 0.0% | 0.0973 | 0.0648 | 4 | 80.4 | 0.00 |
| left_ankle | 0.9162 | 1.1483 | 1.3553 | 19.4% | 0.0% | 0.0736 | 0.0512 | 3 | 60.3 | 0.00 |
| right_hip_pitch | 0.5966 | 1.0318 | 1.3182 | 12.6% | 0.0% | 0.0479 | 0.0282 | 3 | 60.3 | 0.00 |
| right_knee | 0.8854 | 1.2515 | 1.9568 | 18.8% | 0.0% | 0.0711 | 0.0452 | 4 | 80.4 | 0.00 |
| right_ankle | 0.6623 | 1.2168 | 1.6118 | 14.0% | 0.0% | 0.0532 | 0.0328 | 4 | 80.4 | 0.00 |

## Detailed Joint Metrics

### left_hip_pitch

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0046 | 0.0151 | 0.0235 | 0.0272 |
| target velocity sent rad/s | 0.2291 | 0.7508 | 1.1715 | 1.3547 |
| pre-rate-limit target velocity rad/s | 0.2291 | 0.7508 | 1.1715 | 1.3547 |
| action delta per tick | 0.0184 | 0.0603 | 0.0941 | 0.1089 |
| tracking error abs rad | 0.0153 | 0.0426 | 0.0532 | 0.0560 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `4 ticks`, `80.4 ms`, rmse `0.0137`

### left_knee

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0051 | 0.0243 | 0.0321 | 0.0329 |
| target velocity sent rad/s | 0.2555 | 1.2104 | 1.6005 | 1.6355 |
| pre-rate-limit target velocity rad/s | 0.2555 | 1.2104 | 1.6005 | 1.6355 |
| action delta per tick | 0.0205 | 0.0973 | 0.1286 | 0.1314 |
| tracking error abs rad | 0.0328 | 0.0648 | 0.0961 | 0.1110 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `4 ticks`, `80.4 ms`, rmse `0.0311`

### left_ankle

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0060 | 0.0184 | 0.0231 | 0.0272 |
| target velocity sent rad/s | 0.2964 | 0.9162 | 1.1483 | 1.3553 |
| pre-rate-limit target velocity rad/s | 0.2964 | 0.9162 | 1.1483 | 1.3553 |
| action delta per tick | 0.0238 | 0.0736 | 0.0923 | 0.1087 |
| tracking error abs rad | 0.0132 | 0.0512 | 0.0609 | 0.0640 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0156`

### right_hip_pitch

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0040 | 0.0120 | 0.0207 | 0.0265 |
| target velocity sent rad/s | 0.1988 | 0.5966 | 1.0318 | 1.3182 |
| pre-rate-limit target velocity rad/s | 0.1988 | 0.5966 | 1.0318 | 1.3182 |
| action delta per tick | 0.0160 | 0.0479 | 0.0829 | 0.1059 |
| tracking error abs rad | 0.0102 | 0.0282 | 0.0511 | 0.0640 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0102`

### right_knee

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0045 | 0.0178 | 0.0251 | 0.0393 |
| target velocity sent rad/s | 0.2226 | 0.8854 | 1.2515 | 1.9568 |
| pre-rate-limit target velocity rad/s | 0.2226 | 0.8854 | 1.2515 | 1.9568 |
| action delta per tick | 0.0179 | 0.0711 | 0.1006 | 0.1572 |
| tracking error abs rad | 0.0174 | 0.0452 | 0.0604 | 0.0622 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `4 ticks`, `80.4 ms`, rmse `0.0140`

### right_ankle

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0039 | 0.0133 | 0.0244 | 0.0324 |
| target velocity sent rad/s | 0.1938 | 0.6623 | 1.2168 | 1.6118 |
| pre-rate-limit target velocity rad/s | 0.1938 | 0.6623 | 1.2168 | 1.6118 |
| action delta per tick | 0.0156 | 0.0532 | 0.0978 | 0.1295 |
| tracking error abs rad | 0.0108 | 0.0328 | 0.0447 | 0.0658 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `4 ticks`, `80.4 ms`, rmse `0.0099`

## Interpretation

- Compare these target velocities against actuator sine sweep velocities before attributing tracking error to ground contact.
