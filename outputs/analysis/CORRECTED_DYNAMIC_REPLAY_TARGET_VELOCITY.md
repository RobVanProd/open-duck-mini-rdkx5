# Policy Target Velocity Analysis

telemetry_jsonl: `outputs/first_evidence/20260627T221019Z_corrected_dynamic_replay/suspended_policy_replay_x008_corrected_knee.jsonl`
samples_after_startup_filter: `721`
startup_ticks_excluded: `25`
servo_no_load_rad_s_reference: `4.720`
command_first: `(0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)`
command_last: `(0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)`
bus: read_error_count=`20`, write_error_count=`0`, last_error=`read_present_position: Checksum error`

## Pitch-Chain Summary

| joint | sent_vel_p95 | sent_vel_p99 | sent_vel_max | p95_vs_no_load | rate_limit_active | action_delta_p95 | tracking_p95 | lag_ticks | lag_ms | action_sat_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 5.2169 | 5.2178 | 5.2256 | 110.5% | 6.5% | 0.3893 | 0.1711 | 4 | 80.3 | 0.00 |
| left_knee | 3.6721 | 4.6261 | 5.2170 | 77.8% | 0.4% | 0.2950 | 0.1485 | 3 | 60.3 | 0.00 |
| left_ankle | 3.8513 | 5.2174 | 5.2182 | 81.6% | 3.1% | 0.2563 | 0.1250 | 4 | 80.3 | 0.00 |
| right_hip_pitch | 3.1419 | 3.8863 | 4.7807 | 66.6% | 0.0% | 0.2525 | 0.1275 | 4 | 80.3 | 2.50 |
| right_knee | 4.4832 | 5.2173 | 5.2182 | 95.0% | 2.9% | 0.3572 | 0.1660 | 4 | 80.3 | 0.00 |
| right_ankle | 3.5640 | 5.2167 | 5.2178 | 75.5% | 1.2% | 0.2734 | 0.1263 | 4 | 80.3 | 0.00 |

## Detailed Joint Metrics

### left_hip_pitch

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0221 | 0.1048 | 0.1048 | 0.1048 |
| target velocity sent rad/s | 1.0988 | 5.2169 | 5.2178 | 5.2256 |
| pre-rate-limit target velocity rad/s | 1.1047 | 4.7542 | 10.4091 | 13.5221 |
| action delta per tick | 0.0888 | 0.3893 | 0.8364 | 1.0866 |
| tracking error abs rad | 0.0461 | 0.1711 | 0.2240 | 0.2690 |

- rate_limit_active_pct: `6.52`
- rate_limit_delta_max_rad: `0.1669`
- best_lag: `4 ticks`, `80.3 ms`, rmse `0.0272`

### left_knee

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0279 | 0.0738 | 0.0929 | 0.1048 |
| target velocity sent rad/s | 1.3885 | 3.6721 | 4.6261 | 5.2170 |
| pre-rate-limit target velocity rad/s | 1.3885 | 3.6721 | 4.6260 | 6.4162 |
| action delta per tick | 0.1115 | 0.2950 | 0.3717 | 0.5156 |
| tracking error abs rad | 0.0641 | 0.1485 | 0.1907 | 0.2321 |

- rate_limit_active_pct: `0.42`
- rate_limit_delta_max_rad: `0.0241`
- best_lag: `3 ticks`, `60.3 ms`, rmse `0.0206`

### left_ankle

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0144 | 0.0774 | 0.1048 | 0.1048 |
| target velocity sent rad/s | 0.7180 | 3.8513 | 5.2174 | 5.2182 |
| pre-rate-limit target velocity rad/s | 0.7056 | 3.1905 | 8.1535 | 8.9286 |
| action delta per tick | 0.0567 | 0.2563 | 0.6552 | 0.7174 |
| tracking error abs rad | 0.0242 | 0.1250 | 0.1875 | 0.2088 |

- rate_limit_active_pct: `3.05`
- rate_limit_delta_max_rad: `0.0745`
- best_lag: `4 ticks`, `80.3 ms`, rmse `0.0196`

### right_hip_pitch

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0174 | 0.0631 | 0.0781 | 0.0960 |
| target velocity sent rad/s | 0.8649 | 3.1419 | 3.8863 | 4.7807 |
| pre-rate-limit target velocity rad/s | 0.8649 | 3.1419 | 3.8863 | 4.7807 |
| action delta per tick | 0.0695 | 0.2525 | 0.3123 | 0.3841 |
| tracking error abs rad | 0.0324 | 0.1275 | 0.1446 | 0.1706 |

- rate_limit_active_pct: `0.00`
- rate_limit_delta_max_rad: `0.0000`
- best_lag: `4 ticks`, `80.3 ms`, rmse `0.0205`

### right_knee

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0301 | 0.0901 | 0.1048 | 0.1048 |
| target velocity sent rad/s | 1.4973 | 4.4832 | 5.2173 | 5.2182 |
| pre-rate-limit target velocity rad/s | 1.5094 | 4.4460 | 6.7483 | 9.1281 |
| action delta per tick | 0.1213 | 0.3572 | 0.5422 | 0.7334 |
| tracking error abs rad | 0.0678 | 0.1660 | 0.1817 | 0.2049 |

- rate_limit_active_pct: `2.91`
- rate_limit_delta_max_rad: `0.0786`
- best_lag: `4 ticks`, `80.3 ms`, rmse `0.0273`

### right_ankle

| metric | p50 | p95 | p99 | max |
|---|---:|---:|---:|---:|
| target step sent rad/tick | 0.0161 | 0.0716 | 0.1048 | 0.1048 |
| target velocity sent rad/s | 0.8036 | 3.5640 | 5.2167 | 5.2178 |
| pre-rate-limit target velocity rad/s | 0.8036 | 3.4024 | 5.5957 | 6.3421 |
| action delta per tick | 0.0646 | 0.2734 | 0.4496 | 0.5095 |
| tracking error abs rad | 0.0330 | 0.1263 | 0.1672 | 0.1902 |

- rate_limit_active_pct: `1.25`
- rate_limit_delta_max_rad: `0.0226`
- best_lag: `4 ticks`, `80.3 ms`, rmse `0.0239`

## Interpretation

- At least one joint has p95 sent target velocity above 75% of the ST3215 no-load speed reference.
- Runtime rate limiting is active on at least one analyzed joint.
- ONNX action saturation appears on at least one analyzed joint.
- Compare these target velocities against actuator sine sweep velocities before attributing tracking error to ground contact.
