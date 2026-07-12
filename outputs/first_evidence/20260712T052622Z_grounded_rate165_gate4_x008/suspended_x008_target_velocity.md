# Policy Target Velocity Analysis

telemetry_jsonl: `outputs/first_evidence/20260712T052622Z_grounded_rate165_gate4_x008/suspended_x008.jsonl`
samples_after_startup_filter: `721`
startup_ticks_excluded: `25`
servo_no_load_rad_s_reference: `4.720`
command_first: `(0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)`
command_last: `(0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)`
bus: read_error_count=`25`, write_error_count=`0`, last_error=`read_present_position: Checksum error`

## Pitch-Chain Summary

| joint | sent_vel_p95 | sent_vel_p99 | sent_vel_max | p95_vs_no_load | rate_limit_active | action_delta_p95 | tracking_p95 | lag_ticks | lag_ms | action_sat_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 1.2965 | 1.6677 | 2.0780 | 27.5% | 0.0% | 0.1042 | 0.0507 | 3 | 60.3 | 0.00 |
| left_knee | 1.6888 | 2.1435 | 3.0123 | 35.8% | 0.0% | 0.1357 | 0.0575 | 3 | 60.3 | 0.00 |
| left_ankle | 1.3758 | 1.8173 | 2.0665 | 29.1% | 0.0% | 0.1105 | 0.0456 | 3 | 60.3 | 0.00 |
| right_hip_pitch | 1.2519 | 1.6147 | 2.0042 | 26.5% | 0.0% | 0.1006 | 0.0419 | 3 | 60.3 | 0.00 |
| right_knee | 0.9343 | 1.4285 | 1.8466 | 19.8% | 0.0% | 0.0751 | 0.0338 | 3 | 60.3 | 0.00 |
| right_ankle | 1.1834 | 1.4893 | 2.0247 | 25.1% | 0.0% | 0.0951 | 0.0429 | 3 | 60.3 | 0.00 |

## Detailed Joint Metrics

### left_hip_pitch

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0097 | 0.0260 | 0.0335 | 0.0417 |
| target velocity sent rad/s | 0.4843 | 1.2965 | 1.6677 | 2.0780 |
| pre-rate-limit target velocity rad/s | 0.4843 | 1.2965 | 1.6677 | 2.0780 |
| action delta per tick | 0.0389 | 0.1042 | 0.1340 | 0.1670 |
| tracking error abs rad | 0.0170 | 0.0507 | 0.0597 | 0.0686 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0057`

### left_knee

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0095 | 0.0339 | 0.0431 | 0.0605 |
| target velocity sent rad/s | 0.4752 | 1.6888 | 2.1435 | 3.0123 |
| pre-rate-limit target velocity rad/s | 0.4752 | 1.6888 | 2.1435 | 3.0123 |
| action delta per tick | 0.0382 | 0.1357 | 0.1722 | 0.2420 |
| tracking error abs rad | 0.0161 | 0.0575 | 0.0737 | 0.0895 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0079`

### left_ankle

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0083 | 0.0276 | 0.0365 | 0.0415 |
| target velocity sent rad/s | 0.4114 | 1.3758 | 1.8173 | 2.0665 |
| pre-rate-limit target velocity rad/s | 0.4114 | 1.3758 | 1.8173 | 2.0665 |
| action delta per tick | 0.0331 | 0.1105 | 0.1462 | 0.1661 |
| tracking error abs rad | 0.0149 | 0.0456 | 0.0547 | 0.0647 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0053`

### right_hip_pitch

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0063 | 0.0252 | 0.0324 | 0.0403 |
| target velocity sent rad/s | 0.3124 | 1.2519 | 1.6147 | 2.0042 |
| pre-rate-limit target velocity rad/s | 0.3124 | 1.2519 | 1.6147 | 2.0042 |
| action delta per tick | 0.0251 | 0.1006 | 0.1297 | 0.1611 |
| tracking error abs rad | 0.0111 | 0.0419 | 0.0580 | 0.0644 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0064`

### right_knee

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0060 | 0.0188 | 0.0287 | 0.0373 |
| target velocity sent rad/s | 0.2972 | 0.9343 | 1.4285 | 1.8466 |
| pre-rate-limit target velocity rad/s | 0.2972 | 0.9343 | 1.4285 | 1.8466 |
| action delta per tick | 0.0239 | 0.0751 | 0.1148 | 0.1493 |
| tracking error abs rad | 0.0093 | 0.0338 | 0.0522 | 0.0751 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0049`

### right_ankle

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0078 | 0.0238 | 0.0299 | 0.0407 |
| target velocity sent rad/s | 0.3862 | 1.1834 | 1.4893 | 2.0247 |
| pre-rate-limit target velocity rad/s | 0.3862 | 1.1834 | 1.4893 | 2.0247 |
| action delta per tick | 0.0310 | 0.0951 | 0.1197 | 0.1627 |
| tracking error abs rad | 0.0134 | 0.0429 | 0.0506 | 0.0596 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0050`

## Interpretation

- Compare these target velocities against actuator sine sweep velocities before attributing tracking error to ground contact.
