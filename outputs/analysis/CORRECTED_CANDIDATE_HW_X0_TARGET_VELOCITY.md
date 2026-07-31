# Policy Target Velocity Analysis

telemetry_jsonl: `outputs/first_evidence/20260628T010359Z_corrected_candidate_x0_stand/corrected_candidate_x0_stand.jsonl`
samples_after_startup_filter: `721`
startup_ticks_excluded: `25`
servo_no_load_rad_s_reference: `4.720`
command_first: `(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)`
command_last: `(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)`
bus: read_error_count=`18`, write_error_count=`0`, last_error=`read_present_position: Checksum error`

## Pitch-Chain Summary

| joint | sent_vel_p95 | sent_vel_p99 | sent_vel_max | p95_vs_no_load | rate_limit_active | action_delta_p95 | tracking_p95 | lag_ticks | lag_ms | action_sat_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 0.1968 | 0.2303 | 0.3096 | 4.2% | 0.0% | 0.0158 | 0.0098 | 3 | 60.3 | 0.00 |
| left_knee | 0.2039 | 0.2355 | 0.6173 | 4.3% | 0.0% | 0.0164 | 0.0124 | 3 | 60.3 | 0.00 |
| left_ankle | 0.2221 | 0.2697 | 0.6578 | 4.7% | 0.0% | 0.0178 | 0.0103 | 3 | 60.3 | 0.00 |
| right_hip_pitch | 0.1671 | 0.2019 | 0.2629 | 3.5% | 0.0% | 0.0134 | 0.0097 | 3 | 60.3 | 0.00 |
| right_knee | 0.1728 | 0.2293 | 0.3074 | 3.7% | 0.0% | 0.0139 | 0.0112 | 4 | 80.3 | 0.00 |
| right_ankle | 0.1766 | 0.2160 | 0.3192 | 3.7% | 0.0% | 0.0142 | 0.0089 | 4 | 80.3 | 0.00 |

## Detailed Joint Metrics

### left_hip_pitch

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0022 | 0.0040 | 0.0046 | 0.0062 |
| target velocity sent rad/s | 0.1095 | 0.1968 | 0.2303 | 0.3096 |
| pre-rate-limit target velocity rad/s | 0.1095 | 0.1968 | 0.2303 | 0.3096 |
| action delta per tick | 0.0088 | 0.0158 | 0.0185 | 0.0249 |
| tracking error abs rad | 0.0046 | 0.0098 | 0.0103 | 0.0108 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0023`

### left_knee

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0019 | 0.0041 | 0.0047 | 0.0124 |
| target velocity sent rad/s | 0.0967 | 0.2039 | 0.2355 | 0.6173 |
| pre-rate-limit target velocity rad/s | 0.0967 | 0.2039 | 0.2355 | 0.6173 |
| action delta per tick | 0.0078 | 0.0164 | 0.0189 | 0.0496 |
| tracking error abs rad | 0.0057 | 0.0124 | 0.0140 | 0.0150 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0041`

### left_ankle

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0021 | 0.0045 | 0.0054 | 0.0132 |
| target velocity sent rad/s | 0.1042 | 0.2221 | 0.2697 | 0.6578 |
| pre-rate-limit target velocity rad/s | 0.1042 | 0.2221 | 0.2697 | 0.6578 |
| action delta per tick | 0.0084 | 0.0178 | 0.0217 | 0.0529 |
| tracking error abs rad | 0.0039 | 0.0103 | 0.0119 | 0.0141 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0022`

### right_hip_pitch

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0015 | 0.0034 | 0.0041 | 0.0053 |
| target velocity sent rad/s | 0.0751 | 0.1671 | 0.2019 | 0.2629 |
| pre-rate-limit target velocity rad/s | 0.0751 | 0.1671 | 0.2019 | 0.2629 |
| action delta per tick | 0.0060 | 0.0134 | 0.0162 | 0.0211 |
| tracking error abs rad | 0.0028 | 0.0097 | 0.0112 | 0.0130 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0022`

### right_knee

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0018 | 0.0035 | 0.0046 | 0.0062 |
| target velocity sent rad/s | 0.0908 | 0.1728 | 0.2293 | 0.3074 |
| pre-rate-limit target velocity rad/s | 0.0908 | 0.1728 | 0.2293 | 0.3074 |
| action delta per tick | 0.0073 | 0.0139 | 0.0184 | 0.0247 |
| tracking error abs rad | 0.0036 | 0.0112 | 0.0132 | 0.0141 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `4 ticks`, `80.3 ms`, rmse `0.0030`

### right_ankle

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0015 | 0.0035 | 0.0043 | 0.0064 |
| target velocity sent rad/s | 0.0755 | 0.1766 | 0.2160 | 0.3192 |
| pre-rate-limit target velocity rad/s | 0.0755 | 0.1766 | 0.2160 | 0.3192 |
| action delta per tick | 0.0061 | 0.0142 | 0.0174 | 0.0256 |
| tracking error abs rad | 0.0035 | 0.0089 | 0.0104 | 0.0118 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `4 ticks`, `80.3 ms`, rmse `0.0021`

## Interpretation

- Compare these target velocities against actuator sine sweep velocities before attributing tracking error to ground contact.
