# Suspended Replay Gate Analysis

telemetry_jsonl: `outputs/first_evidence/20260712T174550Z_rate165_hard_vector_x0_repeat/suspended_x0.jsonl`
terminal_log: `outputs/first_evidence/20260712T174550Z_rate165_hard_vector_x0_repeat/suspended_x0_terminal.log`
samples: `743`
gate_recommendation: `HOLD_CONTROL_IMPACT`
gate_reason: `repeated control budget warnings: 2`

## Stop/Go Threshold Status

Nonzero CRC/read retries are warnings unless they correlate with control damage: dt spikes, action saturation/jumps, post-startup tracking spikes, write failures, or visible operator-reported twitching.

read_error_rate_pct: `0.000`
bus_event_count: `0`
bus_read_burst_count: `0`
bus_write_burst_count: `0`
dt_gt_0_030_s_count: `2`
dt_gt_0_050_s_count: `2`
startup_tracking_spikes_gt_0.05_rad: `0`
post_startup_tracking_spikes_gt_0.05_rad: `0`

holds:
- repeated control budget warnings: 2
- dt exceeded 0.050s

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
| control_budget_exceeded | 2 |
| exception_or_traceback | 0 |
| motor_off_cleanup | 1 |

terminal_timestamp_status: `not present; correlation is limited`

## Timing

dt_mean_s: 0.02020
dt_p95_s: 0.02009
dt_p99_s: 0.02010
dt_max_s: 0.06212
dt_spikes_gt_0.04_s: `2`
- tick `250` t=`603.48941` dt_s=`0.06212`
- tick `540` t=`609.35645` dt_s=`0.06087`

## Accel Obs[3:6]

| axis | mean | std | min | max |
|---|---:|---:|---:|---:|
| accel_x | 1.6044 | 0.1097 | 0.0000 | 2.1700 |
| accel_y | 1.0164 | 0.1088 | 0.0000 | 1.5300 |
| accel_z | 9.6342 | 0.3774 | 0.0000 | 10.6500 |

## Action Stats

| joint | action_mean | action_min | action_max | saturation_pct |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0808 | 0.0456 | 0.0959 | 0.00 |
| left_hip_roll | 0.0494 | 0.0049 | 0.0997 | 0.00 |
| left_hip_pitch | 0.0060 | -0.0289 | 0.0409 | 0.00 |
| left_knee | 0.0101 | -0.0544 | 0.0562 | 0.00 |
| left_ankle | 0.0033 | -0.0504 | 0.0678 | 0.00 |
| neck_pitch | 0.0701 | 0.0107 | 0.1342 | 0.00 |
| head_pitch | -0.0133 | -0.0295 | 0.0187 | 0.00 |
| head_yaw | 0.0034 | -0.0233 | 0.0272 | 0.00 |
| head_roll | 0.0154 | -0.0024 | 0.0306 | 0.00 |
| right_hip_yaw | -0.0721 | -0.1122 | -0.0030 | 0.00 |
| right_hip_roll | 0.0064 | -0.0304 | 0.0312 | 0.00 |
| right_hip_pitch | -0.0167 | -0.0823 | 0.0213 | 0.00 |
| right_knee | -0.0373 | -0.0482 | -0.0144 | 0.00 |
| right_ankle | 0.0273 | -0.0095 | 0.0665 | 0.00 |

## Tracking Error

| joint | p50_abs_rad | p95_abs_rad | p99_abs_rad | max_abs_rad |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0030 | 0.0043 | 0.0047 | 0.0260 |
| left_hip_roll | 0.0069 | 0.0173 | 0.0186 | 0.0210 |
| left_hip_pitch | 0.0036 | 0.0086 | 0.0099 | 0.0112 |
| left_knee | 0.0049 | 0.0143 | 0.0153 | 0.0177 |
| left_ankle | 0.0043 | 0.0121 | 0.0130 | 0.0137 |
| neck_pitch | 0.0081 | 0.0219 | 0.0229 | 0.0246 |
| head_pitch | 0.0057 | 0.0065 | 0.0068 | 0.0137 |
| head_yaw | 0.0244 | 0.0280 | 0.0290 | 0.0298 |
| head_roll | 0.0089 | 0.0112 | 0.0115 | 0.0127 |
| right_hip_yaw | 0.0024 | 0.0031 | 0.0036 | 0.0240 |
| right_hip_roll | 0.0074 | 0.0132 | 0.0135 | 0.0138 |
| right_hip_pitch | 0.0031 | 0.0069 | 0.0088 | 0.0146 |
| right_knee | 0.0020 | 0.0060 | 0.0067 | 0.0072 |
| right_ankle | 0.0033 | 0.0109 | 0.0125 | 0.0187 |

largest_tracking_spike: tick `132`, t=`601.07709`, joint `head_yaw`, abs_error_rad=`0.0298`
nearest_dt_spike_to_largest_tracking: tick `250`, delta_ticks=`118`, dt_s=`0.06212`
tracking_spikes_gt_0.05_rad: `0`

## Target Step And Rate Limit

| joint | pre_step_max_rad | post_step_max_rad | pre_to_post_delta_max_rad |
|---|---:|---:|---:|
| left_hip_yaw | 0.0074 | 0.0074 | 0.0000 |
| left_hip_roll | 0.0119 | 0.0119 | 0.0000 |
| left_hip_pitch | 0.0062 | 0.0062 | 0.0000 |
| left_knee | 0.0060 | 0.0060 | 0.0000 |
| left_ankle | 0.0053 | 0.0053 | 0.0000 |
| neck_pitch | 0.0101 | 0.0101 | 0.0000 |
| head_pitch | 0.0063 | 0.0063 | 0.0000 |
| head_yaw | 0.0084 | 0.0084 | 0.0000 |
| head_roll | 0.0061 | 0.0061 | 0.0000 |
| right_hip_yaw | 0.0233 | 0.0233 | 0.0000 |
| right_hip_roll | 0.0124 | 0.0124 | 0.0000 |
| right_hip_pitch | 0.0168 | 0.0168 | 0.0000 |
| right_knee | 0.0046 | 0.0046 | 0.0000 |
| right_ankle | 0.0075 | 0.0075 | 0.0000 |

## Pitch Posture Numeric Summary

Sign-to-physical-forward cannot be inferred from telemetry alone; use joint identity visual notes for direction.

| joint | scaled_delta_mean_rad | sent_target_mean_rad | sent_min | sent_max |
|---|---:|---:|---:|---:|
| left_hip_pitch | 0.0015 | -0.6285 | -0.6372 | -0.6198 |
| left_knee | 0.0025 | 1.3705 | 1.3544 | 1.3821 |
| left_ankle | 0.0008 | -0.7832 | -0.7966 | -0.7670 |
| right_hip_pitch | -0.0042 | 0.6308 | 0.6144 | 0.6403 |
| right_knee | -0.0093 | 1.3697 | 1.3669 | 1.3754 |
| right_ankle | 0.0068 | -0.7892 | -0.7984 | -0.7794 |

## Bus Counters

bus_status: `available`
read_error_count_max: `0`
write_error_count_max: `0`
last_error: `None`
