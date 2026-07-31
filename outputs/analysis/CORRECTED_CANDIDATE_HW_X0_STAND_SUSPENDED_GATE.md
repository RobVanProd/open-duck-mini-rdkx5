# Suspended Replay Gate Analysis

telemetry_jsonl: `outputs/first_evidence/20260628T010359Z_corrected_candidate_x0_stand/corrected_candidate_x0_stand.jsonl`
terminal_log: `outputs/first_evidence/20260628T010359Z_corrected_candidate_x0_stand/terminal.log`
samples: `747`
gate_recommendation: `HOLD_CONTROL_IMPACT`
gate_reason: `read retry/error rate 2.41% exceeds red threshold`

## Stop/Go Threshold Status

Nonzero CRC/read retries are warnings unless they correlate with control damage: dt spikes, action saturation/jumps, post-startup tracking spikes, write failures, or visible operator-reported twitching.

read_error_rate_pct: `2.410`
bus_event_count: `18`
bus_read_burst_count: `0`
bus_write_burst_count: `0`
dt_gt_0_030_s_count: `0`
dt_gt_0_050_s_count: `0`
startup_tracking_spikes_gt_0.05_rad: `20`
post_startup_tracking_spikes_gt_0.05_rad: `0`

holds:
- read retry/error rate 2.41% exceeds red threshold

warnings:
- terminal CRC/read checksum warnings observed: 18
- one isolated control budget warning

## Policy And Command

policy_hash: `63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e`
input_name: `obs`
output_name: `continuous_actions`
command_first: `[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`
command_last: `[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`
command_unique_count: `1`
command_max_abs: `0.0000`

## Terminal Warnings

| pattern | count |
|---|---:|
| crc_mismatch | 18 |
| read_crc | 18 |
| write_crc | 0 |
| read_error | 0 |
| write_error | 0 |
| timeout | 0 |
| control_budget_exceeded | 1 |
| exception_or_traceback | 0 |
| motor_off_cleanup | 1 |

terminal_timestamp_status: `not present; correlation is limited`

## Timing

dt_mean_s: 0.02010
dt_p95_s: 0.02010
dt_p99_s: 0.02021
dt_max_s: 0.02523
dt_spikes_gt_0.04_s: `0`

## Accel Obs[3:6]

| axis | mean | std | min | max |
|---|---:|---:|---:|---:|
| accel_x | 1.6114 | 0.2078 | 0.0000 | 3.3600 |
| accel_y | 0.1012 | 0.1897 | -0.9700 | 1.2400 |
| accel_z | 9.7815 | 0.4744 | 0.0000 | 13.8700 |

## Action Stats

| joint | action_mean | action_min | action_max | saturation_pct |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0072 | -0.0543 | 0.0179 | 0.00 |
| left_hip_roll | -0.0424 | -0.0999 | 0.0168 | 0.00 |
| left_hip_pitch | -0.3196 | -0.4105 | -0.2569 | 0.00 |
| left_knee | 0.0088 | -0.1738 | 0.1034 | 0.00 |
| left_ankle | 0.1944 | 0.1279 | 0.3722 | 0.00 |
| neck_pitch | 0.4035 | 0.3708 | 0.4783 | 0.00 |
| head_pitch | -0.0714 | -0.0924 | -0.0089 | 0.00 |
| head_yaw | -0.2622 | -0.3523 | -0.2244 | 0.00 |
| head_roll | -0.1624 | -0.2083 | -0.0700 | 0.00 |
| right_hip_yaw | 0.0008 | -0.0246 | 0.0523 | 0.00 |
| right_hip_roll | -0.0465 | -0.1273 | 0.0143 | 0.00 |
| right_hip_pitch | 0.3873 | 0.3324 | 0.4381 | 0.00 |
| right_knee | 0.0840 | 0.0067 | 0.1487 | 0.00 |
| right_ankle | 0.3649 | 0.3121 | 0.4192 | 0.00 |

## Tracking Error

| joint | p50_abs_rad | p95_abs_rad | p99_abs_rad | max_abs_rad |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0008 | 0.0034 | 0.0044 | 0.0146 |
| left_hip_roll | 0.0056 | 0.0165 | 0.0178 | 0.0203 |
| left_hip_pitch | 0.0046 | 0.0099 | 0.0149 | 0.0943 |
| left_knee | 0.0056 | 0.0127 | 0.0165 | 0.0325 |
| left_ankle | 0.0040 | 0.0107 | 0.0135 | 0.0902 |
| neck_pitch | 0.0055 | 0.0168 | 0.0327 | 0.1124 |
| head_pitch | 0.0073 | 0.0106 | 0.0115 | 0.0158 |
| head_yaw | 0.0044 | 0.0120 | 0.0283 | 0.0587 |
| head_roll | 0.0036 | 0.0104 | 0.0137 | 0.0457 |
| right_hip_yaw | 0.0033 | 0.0080 | 0.0094 | 0.0098 |
| right_hip_roll | 0.0066 | 0.0173 | 0.0186 | 0.0192 |
| right_hip_pitch | 0.0028 | 0.0099 | 0.0131 | 0.1068 |
| right_knee | 0.0036 | 0.0113 | 0.0139 | 0.0422 |
| right_ankle | 0.0035 | 0.0091 | 0.0107 | 0.0955 |

largest_tracking_spike: tick `2`, t=`178.81014`, joint `neck_pitch`, abs_error_rad=`0.1124`
nearest_dt_spike_to_largest_tracking: `NONE`
tracking_spikes_gt_0.05_rad: `20`
- tick `2` t=`178.81014` joint `neck_pitch` abs_error_rad=`0.1124`
- tick `1` t=`178.79004` joint `right_hip_pitch` abs_error_rad=`0.1068`
- tick `3` t=`178.83023` joint `neck_pitch` abs_error_rad=`0.1051`
- tick `1` t=`178.79004` joint `neck_pitch` abs_error_rad=`0.0998`
- tick `2` t=`178.81014` joint `right_hip_pitch` abs_error_rad=`0.0971`
- tick `1` t=`178.79004` joint `right_ankle` abs_error_rad=`0.0955`
- tick `1` t=`178.79004` joint `left_hip_pitch` abs_error_rad=`0.0943`
- tick `4` t=`178.85032` joint `neck_pitch` abs_error_rad=`0.0940`
- tick `1` t=`178.79004` joint `left_ankle` abs_error_rad=`0.0902`
- tick `2` t=`178.81014` joint `left_hip_pitch` abs_error_rad=`0.0896`

## Target Step And Rate Limit

| joint | pre_step_max_rad | post_step_max_rad | pre_to_post_delta_max_rad |
|---|---:|---:|---:|
| left_hip_yaw | 0.0094 | 0.0094 | 0.0000 |
| left_hip_roll | 0.0099 | 0.0099 | 0.0000 |
| left_hip_pitch | 0.0083 | 0.0083 | 0.0000 |
| left_knee | 0.0131 | 0.0131 | 0.0000 |
| left_ankle | 0.0164 | 0.0164 | 0.0000 |
| neck_pitch | 0.0100 | 0.0126 | 0.0026 |
| head_pitch | 0.0109 | 0.0109 | 0.0000 |
| head_yaw | 0.0152 | 0.0152 | 0.0000 |
| head_roll | 0.0163 | 0.0163 | 0.0000 |
| right_hip_yaw | 0.0054 | 0.0054 | 0.0000 |
| right_hip_roll | 0.0118 | 0.0118 | 0.0000 |
| right_hip_pitch | 0.0122 | 0.0122 | 0.0047 |
| right_knee | 0.0109 | 0.0109 | 0.0000 |
| right_ankle | 0.0064 | 0.0064 | 0.0000 |

## Pitch Posture Numeric Summary

Sign-to-physical-forward cannot be inferred from telemetry alone; use joint identity visual notes for direction.

| joint | scaled_delta_mean_rad | sent_target_mean_rad | sent_min | sent_max |
|---|---:|---:|---:|---:|
| left_hip_pitch | -0.0799 | -0.7099 | -0.7326 | -0.6942 |
| left_knee | 0.0022 | 1.3702 | 1.3245 | 1.3938 |
| left_ankle | 0.0486 | -0.7354 | -0.7520 | -0.6910 |
| right_hip_pitch | 0.0968 | 0.7318 | 0.7181 | 0.7430 |
| right_knee | 0.0210 | 1.4000 | 1.3807 | 1.4162 |
| right_ankle | 0.0912 | -0.7048 | -0.7180 | -0.6912 |

## Bus Counters

bus_status: `available`
read_error_count_max: `18`
write_error_count_max: `0`
last_error: `read_present_position: Checksum error`
