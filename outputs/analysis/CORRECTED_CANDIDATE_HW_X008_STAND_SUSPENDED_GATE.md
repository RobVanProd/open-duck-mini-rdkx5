# Suspended Replay Gate Analysis

telemetry_jsonl: `outputs/first_evidence/20260628T010517Z_corrected_candidate_x008_stand/corrected_candidate_x008_stand.jsonl`
terminal_log: `outputs/first_evidence/20260628T010517Z_corrected_candidate_x008_stand/terminal.log`
samples: `747`
gate_recommendation: `WARN_PROCEED_WITH_CAUTION`
gate_reason: `read retry/error rate 0.80% is yellow; continue only if uncorrelated`

## Stop/Go Threshold Status

Nonzero CRC/read retries are warnings unless they correlate with control damage: dt spikes, action saturation/jumps, post-startup tracking spikes, write failures, or visible operator-reported twitching.

read_error_rate_pct: `0.803`
bus_event_count: `6`
bus_read_burst_count: `0`
bus_write_burst_count: `0`
dt_gt_0_030_s_count: `0`
dt_gt_0_050_s_count: `0`
startup_tracking_spikes_gt_0.05_rad: `25`
post_startup_tracking_spikes_gt_0.05_rad: `0`

holds:
- NONE

warnings:
- read retry/error rate 0.80% is yellow; continue only if uncorrelated
- terminal CRC/read checksum warnings observed: 6
- tracking p95 above 0.02 rad on at least one joint

## Policy And Command

policy_hash: `63506567f7a973be0ff6b2b222bba41736409da713466db442067c0f2a91415e`
input_name: `obs`
output_name: `continuous_actions`
command_first: `[0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`
command_last: `[0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`
command_unique_count: `1`
command_max_abs: `0.0800`

## Terminal Warnings

| pattern | count |
|---|---:|
| crc_mismatch | 6 |
| read_crc | 6 |
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
dt_max_s: 0.02170
dt_spikes_gt_0.04_s: `0`

## Accel Obs[3:6]

| axis | mean | std | min | max |
|---|---:|---:|---:|---:|
| accel_x | 1.6398 | 0.1824 | 0.0000 | 2.7800 |
| accel_y | 0.0896 | 0.1536 | -1.5800 | 0.8500 |
| accel_z | 9.6993 | 0.4068 | 0.0000 | 11.0300 |

## Action Stats

| joint | action_mean | action_min | action_max | saturation_pct |
|---|---:|---:|---:|---:|
| left_hip_yaw | -0.0060 | -0.0667 | 0.0238 | 0.00 |
| left_hip_roll | -0.0196 | -0.0972 | 0.0911 | 0.00 |
| left_hip_pitch | -0.3630 | -0.4707 | -0.2300 | 0.00 |
| left_knee | -0.0047 | -0.1726 | 0.1253 | 0.00 |
| left_ankle | 0.2150 | 0.1315 | 0.3812 | 0.00 |
| neck_pitch | 0.4390 | 0.3938 | 0.5519 | 0.00 |
| head_pitch | -0.1084 | -0.1546 | -0.0112 | 0.00 |
| head_yaw | -0.2766 | -0.4247 | -0.2207 | 0.00 |
| head_roll | -0.1675 | -0.2370 | -0.0884 | 0.00 |
| right_hip_yaw | -0.0087 | -0.0543 | 0.0493 | 0.00 |
| right_hip_roll | -0.0204 | -0.1487 | 0.0637 | 0.00 |
| right_hip_pitch | 0.3728 | 0.2720 | 0.4770 | 0.00 |
| right_knee | 0.1183 | 0.0234 | 0.1695 | 0.00 |
| right_ankle | 0.3572 | 0.2886 | 0.4639 | 0.00 |

## Tracking Error

| joint | p50_abs_rad | p95_abs_rad | p99_abs_rad | max_abs_rad |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0010 | 0.0052 | 0.0065 | 0.0197 |
| left_hip_roll | 0.0069 | 0.0205 | 0.0227 | 0.0235 |
| left_hip_pitch | 0.0061 | 0.0138 | 0.0190 | 0.1028 |
| left_knee | 0.0059 | 0.0155 | 0.0176 | 0.0365 |
| left_ankle | 0.0041 | 0.0155 | 0.0187 | 0.0898 |
| neck_pitch | 0.0074 | 0.0119 | 0.0267 | 0.1174 |
| head_pitch | 0.0056 | 0.0112 | 0.0136 | 0.0203 |
| head_yaw | 0.0081 | 0.0129 | 0.0275 | 0.0692 |
| head_roll | 0.0044 | 0.0153 | 0.0165 | 0.0416 |
| right_hip_yaw | 0.0039 | 0.0086 | 0.0102 | 0.0152 |
| right_hip_roll | 0.0061 | 0.0207 | 0.0220 | 0.0229 |
| right_hip_pitch | 0.0039 | 0.0149 | 0.0179 | 0.1028 |
| right_knee | 0.0033 | 0.0130 | 0.0154 | 0.0406 |
| right_ankle | 0.0044 | 0.0091 | 0.0126 | 0.1035 |

largest_tracking_spike: tick `2`, t=`256.76919`, joint `neck_pitch`, abs_error_rad=`0.1174`
nearest_dt_spike_to_largest_tracking: `NONE`
tracking_spikes_gt_0.05_rad: `25`
- tick `2` t=`256.76919` joint `neck_pitch` abs_error_rad=`0.1174`
- tick `3` t=`256.78929` joint `neck_pitch` abs_error_rad=`0.1114`
- tick `4` t=`256.80938` joint `neck_pitch` abs_error_rad=`0.1059`
- tick `1` t=`256.74910` joint `right_ankle` abs_error_rad=`0.1035`
- tick `1` t=`256.74910` joint `left_hip_pitch` abs_error_rad=`0.1028`
- tick `1` t=`256.74910` joint `right_hip_pitch` abs_error_rad=`0.1028`
- tick `1` t=`256.74910` joint `neck_pitch` abs_error_rad=`0.0998`
- tick `2` t=`256.76919` joint `right_hip_pitch` abs_error_rad=`0.0954`
- tick `5` t=`256.82947` joint `neck_pitch` abs_error_rad=`0.0950`
- tick `2` t=`256.76919` joint `left_hip_pitch` abs_error_rad=`0.0935`

## Target Step And Rate Limit

| joint | pre_step_max_rad | post_step_max_rad | pre_to_post_delta_max_rad |
|---|---:|---:|---:|
| left_hip_yaw | 0.0100 | 0.0100 | 0.0000 |
| left_hip_roll | 0.0109 | 0.0109 | 0.0000 |
| left_hip_pitch | 0.0152 | 0.0152 | 0.0009 |
| left_knee | 0.0160 | 0.0160 | 0.0000 |
| left_ankle | 0.0267 | 0.0267 | 0.0000 |
| neck_pitch | 0.0155 | 0.0186 | 0.0057 |
| head_pitch | 0.0143 | 0.0143 | 0.0000 |
| head_yaw | 0.0168 | 0.0168 | 0.0000 |
| head_roll | 0.0152 | 0.0152 | 0.0000 |
| right_hip_yaw | 0.0082 | 0.0082 | 0.0000 |
| right_hip_roll | 0.0100 | 0.0100 | 0.0000 |
| right_hip_pitch | 0.0162 | 0.0162 | 0.0144 |
| right_knee | 0.0112 | 0.0112 | 0.0000 |
| right_ankle | 0.0105 | 0.0105 | 0.0000 |

## Pitch Posture Numeric Summary

Sign-to-physical-forward cannot be inferred from telemetry alone; use joint identity visual notes for direction.

| joint | scaled_delta_mean_rad | sent_target_mean_rad | sent_min | sent_max |
|---|---:|---:|---:|---:|
| left_hip_pitch | -0.0907 | -0.7207 | -0.7477 | -0.6875 |
| left_knee | -0.0012 | 1.3668 | 1.3248 | 1.3993 |
| left_ankle | 0.0537 | -0.7303 | -0.7511 | -0.6887 |
| right_hip_pitch | 0.0932 | 0.7282 | 0.7030 | 0.7474 |
| right_knee | 0.0296 | 1.4086 | 1.3849 | 1.4214 |
| right_ankle | 0.0893 | -0.7067 | -0.7239 | -0.6800 |

## Bus Counters

bus_status: `available`
read_error_count_max: `6`
write_error_count_max: `0`
last_error: `read_present_position: Checksum error`
