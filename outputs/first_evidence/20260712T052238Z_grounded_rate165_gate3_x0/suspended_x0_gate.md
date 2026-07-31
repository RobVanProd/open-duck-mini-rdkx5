# Suspended Replay Gate Analysis

telemetry_jsonl: `outputs/first_evidence/20260712T052238Z_grounded_rate165_gate3_x0/suspended_x0.jsonl`
terminal_log: `outputs/first_evidence/20260712T052238Z_grounded_rate165_gate3_x0/suspended_x0_terminal.log`
samples: `747`
gate_recommendation: `WARN_PROCEED_WITH_CAUTION`
gate_reason: `read retry/error rate 0.94% is yellow; continue only if uncorrelated`

## Stop/Go Threshold Status

Nonzero CRC/read retries are warnings unless they correlate with control damage: dt spikes, action saturation/jumps, post-startup tracking spikes, write failures, or visible operator-reported twitching.

read_error_rate_pct: `0.937`
bus_event_count: `7`
bus_read_burst_count: `0`
bus_write_burst_count: `0`
dt_gt_0_030_s_count: `0`
dt_gt_0_050_s_count: `0`
startup_tracking_spikes_gt_0.05_rad: `0`
post_startup_tracking_spikes_gt_0.05_rad: `0`

holds:
- NONE

warnings:
- read retry/error rate 0.94% is yellow; continue only if uncorrelated
- terminal CRC/read checksum warnings observed: 7

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
| crc_mismatch | 7 |
| read_crc | 7 |
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
dt_max_s: 0.02263
dt_spikes_gt_0.04_s: `0`

## Accel Obs[3:6]

| axis | mean | std | min | max |
|---|---:|---:|---:|---:|
| accel_x | 1.6173 | 0.1315 | 0.0000 | 2.0800 |
| accel_y | 0.3755 | 0.1236 | -0.0100 | 0.9500 |
| accel_z | 9.8143 | 0.3798 | 0.0000 | 10.9600 |

## Action Stats

| joint | action_mean | action_min | action_max | saturation_pct |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0762 | 0.0506 | 0.0959 | 0.00 |
| left_hip_roll | 0.0524 | 0.0038 | 0.0994 | 0.00 |
| left_hip_pitch | -0.0090 | -0.0422 | 0.0388 | 0.00 |
| left_knee | 0.0132 | -0.0491 | 0.0633 | 0.00 |
| left_ankle | 0.0072 | -0.0547 | 0.0745 | 0.00 |
| neck_pitch | 0.0831 | 0.0165 | 0.1369 | 0.00 |
| head_pitch | -0.0145 | -0.0270 | 0.0208 | 0.00 |
| head_yaw | 0.0020 | -0.0257 | 0.0253 | 0.00 |
| head_roll | 0.0164 | 0.0003 | 0.0266 | 0.00 |
| right_hip_yaw | -0.0725 | -0.1113 | -0.0045 | 0.00 |
| right_hip_roll | 0.0112 | -0.0329 | 0.0388 | 0.00 |
| right_hip_pitch | -0.0137 | -0.0799 | 0.0226 | 0.00 |
| right_knee | -0.0307 | -0.0478 | -0.0083 | 0.00 |
| right_ankle | 0.0236 | -0.0141 | 0.0605 | 0.00 |

## Tracking Error

| joint | p50_abs_rad | p95_abs_rad | p99_abs_rad | max_abs_rad |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0031 | 0.0055 | 0.0077 | 0.0210 |
| left_hip_roll | 0.0054 | 0.0156 | 0.0173 | 0.0177 |
| left_hip_pitch | 0.0027 | 0.0072 | 0.0086 | 0.0103 |
| left_knee | 0.0047 | 0.0130 | 0.0149 | 0.0160 |
| left_ankle | 0.0039 | 0.0106 | 0.0115 | 0.0130 |
| neck_pitch | 0.0084 | 0.0164 | 0.0221 | 0.0297 |
| head_pitch | 0.0007 | 0.0013 | 0.0019 | 0.0082 |
| head_yaw | 0.0033 | 0.0051 | 0.0059 | 0.0064 |
| head_roll | 0.0118 | 0.0142 | 0.0145 | 0.0147 |
| right_hip_yaw | 0.0009 | 0.0037 | 0.0052 | 0.0246 |
| right_hip_roll | 0.0047 | 0.0102 | 0.0110 | 0.0157 |
| right_hip_pitch | 0.0012 | 0.0082 | 0.0105 | 0.0170 |
| right_knee | 0.0008 | 0.0053 | 0.0059 | 0.0090 |
| right_ankle | 0.0032 | 0.0104 | 0.0118 | 0.0162 |

largest_tracking_spike: tick `5`, t=`1250.81505`, joint `neck_pitch`, abs_error_rad=`0.0297`
nearest_dt_spike_to_largest_tracking: `NONE`
tracking_spikes_gt_0.05_rad: `0`

## Target Step And Rate Limit

| joint | pre_step_max_rad | post_step_max_rad | pre_to_post_delta_max_rad |
|---|---:|---:|---:|
| left_hip_yaw | 0.0061 | 0.0061 | 0.0000 |
| left_hip_roll | 0.0118 | 0.0118 | 0.0000 |
| left_hip_pitch | 0.0078 | 0.0078 | 0.0000 |
| left_knee | 0.0069 | 0.0069 | 0.0000 |
| left_ankle | 0.0072 | 0.0072 | 0.0000 |
| neck_pitch | 0.0097 | 0.0097 | 0.0000 |
| head_pitch | 0.0069 | 0.0069 | 0.0000 |
| head_yaw | 0.0079 | 0.0079 | 0.0000 |
| head_roll | 0.0038 | 0.0038 | 0.0000 |
| right_hip_yaw | 0.0235 | 0.0235 | 0.0000 |
| right_hip_roll | 0.0136 | 0.0136 | 0.0000 |
| right_hip_pitch | 0.0151 | 0.0151 | 0.0000 |
| right_knee | 0.0050 | 0.0050 | 0.0000 |
| right_ankle | 0.0087 | 0.0087 | 0.0000 |

## Pitch Posture Numeric Summary

Sign-to-physical-forward cannot be inferred from telemetry alone; use joint identity visual notes for direction.

| joint | scaled_delta_mean_rad | sent_target_mean_rad | sent_min | sent_max |
|---|---:|---:|---:|---:|
| left_hip_pitch | -0.0023 | -0.6323 | -0.6405 | -0.6203 |
| left_knee | 0.0033 | 1.3713 | 1.3557 | 1.3838 |
| left_ankle | 0.0018 | -0.7822 | -0.7977 | -0.7654 |
| right_hip_pitch | -0.0034 | 0.6316 | 0.6150 | 0.6406 |
| right_knee | -0.0077 | 1.3713 | 1.3670 | 1.3769 |
| right_ankle | 0.0059 | -0.7901 | -0.7995 | -0.7809 |

## Bus Counters

bus_status: `available`
read_error_count_max: `7`
write_error_count_max: `0`
last_error: `read_present_position: Checksum error`
