# Suspended Replay Gate Analysis

telemetry_jsonl: `outputs/first_evidence/20260712T174400Z_rate165_hard_vector_x0/suspended_x0.jsonl`
terminal_log: `outputs/first_evidence/20260712T174400Z_rate165_hard_vector_x0/suspended_x0_terminal.log`
samples: `747`
gate_recommendation: `WARN_PROCEED_WITH_CAUTION`
gate_reason: `tracking p95 above 0.02 rad on at least one joint`

## Stop/Go Threshold Status

Nonzero CRC/read retries are warnings unless they correlate with control damage: dt spikes, action saturation/jumps, post-startup tracking spikes, write failures, or visible operator-reported twitching.

read_error_rate_pct: `0.000`
bus_event_count: `0`
bus_read_burst_count: `0`
bus_write_burst_count: `0`
dt_gt_0_030_s_count: `0`
dt_gt_0_050_s_count: `0`
startup_tracking_spikes_gt_0.05_rad: `0`
post_startup_tracking_spikes_gt_0.05_rad: `0`

holds:
- NONE

warnings:
- tracking p95 above 0.02 rad on at least one joint

## Policy And Command

policy_hash: `e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33`
input_name: `obs`
output_name: `continuous_actions`
command_first: `[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`
command_last: `[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`
command_unique_count: `1`
command_max_abs: `0.0000`

## Terminal Warnings

| pattern | count |
|---|---:|
| crc_mismatch | 0 |
| read_crc | 0 |
| write_crc | 0 |
| read_error | 0 |
| write_error | 0 |
| timeout | 0 |
| control_budget_exceeded | 0 |
| exception_or_traceback | 0 |
| motor_off_cleanup | 1 |

terminal_timestamp_status: `not present; correlation is limited`

## Timing

dt_mean_s: 0.02009
dt_p95_s: 0.02009
dt_p99_s: 0.02010
dt_max_s: 0.02212
dt_spikes_gt_0.04_s: `0`

## Accel Obs[3:6]

| axis | mean | std | min | max |
|---|---:|---:|---:|---:|
| accel_x | 1.6045 | 0.1206 | 0.0000 | 2.0600 |
| accel_y | 1.0228 | 0.1065 | 0.0000 | 1.4800 |
| accel_z | 9.6692 | 0.3763 | 0.0000 | 10.8700 |

## Action Stats

| joint | action_mean | action_min | action_max | saturation_pct |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0815 | 0.0480 | 0.0964 | 0.00 |
| left_hip_roll | 0.0494 | 0.0065 | 0.1036 | 0.00 |
| left_hip_pitch | 0.0041 | -0.0333 | 0.0417 | 0.00 |
| left_knee | 0.0116 | -0.0535 | 0.0576 | 0.00 |
| left_ankle | 0.0012 | -0.0519 | 0.0648 | 0.00 |
| neck_pitch | 0.0697 | 0.0109 | 0.1316 | 0.00 |
| head_pitch | -0.0132 | -0.0292 | 0.0186 | 0.00 |
| head_yaw | 0.0030 | -0.0238 | 0.0259 | 0.00 |
| head_roll | 0.0149 | 0.0005 | 0.0265 | 0.00 |
| right_hip_yaw | -0.0735 | -0.1120 | -0.0043 | 0.00 |
| right_hip_roll | 0.0048 | -0.0322 | 0.0298 | 0.00 |
| right_hip_pitch | -0.0155 | -0.0831 | 0.0234 | 0.00 |
| right_knee | -0.0358 | -0.0487 | -0.0152 | 0.00 |
| right_ankle | 0.0247 | -0.0127 | 0.0651 | 0.00 |

## Tracking Error

| joint | p50_abs_rad | p95_abs_rad | p99_abs_rad | max_abs_rad |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0018 | 0.0061 | 0.0077 | 0.0241 |
| left_hip_roll | 0.0063 | 0.0172 | 0.0183 | 0.0197 |
| left_hip_pitch | 0.0033 | 0.0088 | 0.0100 | 0.0105 |
| left_knee | 0.0048 | 0.0143 | 0.0154 | 0.0176 |
| left_ankle | 0.0041 | 0.0113 | 0.0122 | 0.0149 |
| neck_pitch | 0.0086 | 0.0219 | 0.0232 | 0.0266 |
| head_pitch | 0.0057 | 0.0065 | 0.0068 | 0.0136 |
| head_yaw | 0.0242 | 0.0280 | 0.0290 | 0.0295 |
| head_roll | 0.0088 | 0.0111 | 0.0113 | 0.0116 |
| right_hip_yaw | 0.0010 | 0.0035 | 0.0042 | 0.0253 |
| right_hip_roll | 0.0071 | 0.0129 | 0.0132 | 0.0134 |
| right_hip_pitch | 0.0024 | 0.0072 | 0.0088 | 0.0178 |
| right_knee | 0.0020 | 0.0060 | 0.0068 | 0.0092 |
| right_ankle | 0.0035 | 0.0108 | 0.0123 | 0.0171 |

largest_tracking_spike: tick `590`, t=`505.37256`, joint `head_yaw`, abs_error_rad=`0.0295`
nearest_dt_spike_to_largest_tracking: `NONE`
tracking_spikes_gt_0.05_rad: `0`

## Target Step And Rate Limit

| joint | pre_step_max_rad | post_step_max_rad | pre_to_post_delta_max_rad |
|---|---:|---:|---:|
| left_hip_yaw | 0.0081 | 0.0081 | 0.0000 |
| left_hip_roll | 0.0117 | 0.0117 | 0.0000 |
| left_hip_pitch | 0.0062 | 0.0062 | 0.0000 |
| left_knee | 0.0071 | 0.0071 | 0.0000 |
| left_ankle | 0.0056 | 0.0056 | 0.0000 |
| neck_pitch | 0.0109 | 0.0109 | 0.0000 |
| head_pitch | 0.0065 | 0.0065 | 0.0000 |
| head_yaw | 0.0088 | 0.0088 | 0.0000 |
| head_roll | 0.0037 | 0.0037 | 0.0000 |
| right_hip_yaw | 0.0232 | 0.0232 | 0.0000 |
| right_hip_roll | 0.0123 | 0.0123 | 0.0000 |
| right_hip_pitch | 0.0165 | 0.0165 | 0.0000 |
| right_knee | 0.0043 | 0.0043 | 0.0000 |
| right_ankle | 0.0080 | 0.0080 | 0.0000 |

## Pitch Posture Numeric Summary

Sign-to-physical-forward cannot be inferred from telemetry alone; use joint identity visual notes for direction.

| joint | scaled_delta_mean_rad | sent_target_mean_rad | sent_min | sent_max |
|---|---:|---:|---:|---:|
| left_hip_pitch | 0.0010 | -0.6290 | -0.6383 | -0.6196 |
| left_knee | 0.0029 | 1.3709 | 1.3546 | 1.3824 |
| left_ankle | 0.0003 | -0.7837 | -0.7970 | -0.7678 |
| right_hip_pitch | -0.0039 | 0.6311 | 0.6142 | 0.6409 |
| right_knee | -0.0090 | 1.3700 | 1.3668 | 1.3752 |
| right_ankle | 0.0062 | -0.7898 | -0.7992 | -0.7797 |

## Bus Counters

bus_status: `available`
read_error_count_max: `0`
write_error_count_max: `0`
last_error: `None`
