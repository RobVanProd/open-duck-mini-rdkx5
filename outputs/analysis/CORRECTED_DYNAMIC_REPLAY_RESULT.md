# Corrected Dynamic Replay Result

status: `HOLD_DYNAMIC_TRACKING_STILL_BLOCKS_WALKING`

This result records the corrected-knee suspended/free-air `x=0.08` policy
replay collected after the left-knee offset correction.

No grounded replay, walking-on-floor test, gain tuning, offset edit, remap,
action-scale change, phase change, deployment, or training was performed.
Torque-off was attempted at the end of the robot-side run.

## Input

- telemetry: `outputs/first_evidence/20260627T221019Z_corrected_dynamic_replay/suspended_policy_replay_x008_corrected_knee.jsonl`
- terminal log: `outputs/first_evidence/20260627T221019Z_corrected_dynamic_replay/suspended_policy_replay_x008_corrected_knee.terminal.log`
- command: `x=0.08`
- duration: `15 s`
- action scale: `0.25`
- max motor velocity: `5.24 rad/s`
- duck_config sha256: `131a7b8fce1107b14f4727562f44f9e17324caf7fc22512ad7115911f050991b`
- robot condition: supported/on stand

## Telemetry Summary

| joint | sent velocity p95 | tracking p95 | lag | rate-limit active | action saturation |
|---|---:|---:|---:|---:|---:|
| left_hip_pitch | `5.2169 rad/s` | `0.1711 rad` | `4 ticks / 80.3 ms` | `6.52%` | `0.00%` |
| left_knee | `3.6721 rad/s` | `0.1485 rad` | `3 ticks / 60.3 ms` | `0.42%` | `0.00%` |
| left_ankle | `3.8513 rad/s` | `0.1250 rad` | `4 ticks / 80.3 ms` | `3.05%` | `0.00%` |
| right_hip_pitch | `3.1419 rad/s` | `0.1275 rad` | `4 ticks / 80.3 ms` | `0.00%` | `2.50%` |
| right_knee | `4.4832 rad/s` | `0.1660 rad` | `4 ticks / 80.3 ms` | `2.91%` | `0.00%` |
| right_ankle | `3.5640 rad/s` | `0.1263 rad` | `4 ticks / 80.3 ms` | `1.25%` | `0.00%` |

The broader hardware-analysis summary, without startup filtering, reports max
pitch-chain tracking p95 `0.2038 rad`.

Bus summary:

```text
read_error_count: 20 by final telemetry record
write_error_count: 0
last_error: read_present_position: Checksum error
```

## Corrected Dynamic Fit

Generated:

```text
outputs/analysis/ACTUATOR_RESPONSE_FIT_CORRECTED_KNEE.md
outputs/analysis/actuator_response_fit_corrected_knee.json
outputs/analysis/CORRECTED_KNEE_ACTUATOR_FIT_COMPARE.md
outputs/analysis/corrected_knee_actuator_fit_compare.json
```

Combined fit summary:

| joint | delay ticks | tau_s | velocity limit | model p95 | raw p95 |
|---|---:|---:|---:|---:|---:|
| left_hip_pitch | `3` | `0.020` | `2.50` | `0.0267` | `0.1850` |
| left_knee | `3` | `0.020` | `3.25` | `0.0248` | `0.1968` |
| left_ankle | `3` | `0.020` | `2.75` | `0.0166` | `0.1474` |
| right_hip_pitch | `3` | `0.020` | `2.25` | `0.0259` | `0.1518` |
| right_knee | `3` | `0.020` | `2.75` | `0.0335` | `0.2058` |
| right_ankle | `3` | `0.020` | `2.00` | `0.0211` | `0.1448` |

The corrected dynamic fit remains close to the original dynamic fit: delay is
still `3 ticks`, and the effective velocity limits remain in the same
approximately `2-3.25 rad/s` range. The knee correction did not make
`BEST_WALK_ONNX_2` dynamically trackable at `x=0.08`.

## Decision

```text
HOLD_DYNAMIC_TRACKING_STILL_BLOCKS_WALKING
```

The robot is better calibrated at the knee and passes low-speed actuator
tracking, but the corrected suspended `x=0.08` replay still shows the same
dynamic target waveform mismatch. Grounded replay remains blocked.

Next useful work is offline: use the corrected dynamic fit as the current
actuator bridge evidence, and continue candidate-policy work against the
measured actuator limits. Do not run grounded replay from this result.
