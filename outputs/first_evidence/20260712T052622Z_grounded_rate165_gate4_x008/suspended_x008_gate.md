# Suspended Replay Gate Analysis

telemetry_jsonl: `outputs/first_evidence/20260712T052622Z_grounded_rate165_gate4_x008/suspended_x008.jsonl`
terminal_log: `outputs/first_evidence/20260712T052622Z_grounded_rate165_gate4_x008/suspended_x008_terminal.log`
samples: `747`
gate_recommendation: `HOLD_CONTROL_IMPACT`
gate_reason: `read retry/error rate 3.35% exceeds red threshold`

## Stop/Go Threshold Status

Nonzero CRC/read retries are warnings unless they correlate with control damage: dt spikes, action saturation/jumps, post-startup tracking spikes, write failures, or visible operator-reported twitching.

read_error_rate_pct: `3.347`
bus_event_count: `25`
bus_read_burst_count: `0`
bus_write_burst_count: `0`
dt_gt_0_030_s_count: `0`
dt_gt_0_050_s_count: `0`
startup_tracking_spikes_gt_0.05_rad: `42`
post_startup_tracking_spikes_gt_0.05_rad: `224`

holds:
- read retry/error rate 3.35% exceeds red threshold
- tracking p95 above 0.05 rad
- bus event correlates with post-startup tracking spike

warnings:
- terminal CRC/read checksum warnings observed: 25
- tracking p95 above 0.02 rad on at least one joint
- post-startup tracking spikes present but below red max threshold
- startup-only tracking spike above 0.15 rad; review but do not block by itself

## Policy And Command

policy_hash: `e06643e5790217075d9c7a0d1e1ac262652058592b374ac0446bdd0426d0ea33`
input_name: `obs`
output_name: `continuous_actions`
command_first: `[0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`
command_last: `[0.08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]`
command_unique_count: `1`
command_max_abs: `0.0800`

## Terminal Warnings

| pattern | count |
|---|---:|
| crc_mismatch | 25 |
| read_crc | 25 |
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
dt_p99_s: 0.02017
dt_max_s: 0.02040
dt_spikes_gt_0.04_s: `0`

## Accel Obs[3:6]

| axis | mean | std | min | max |
|---|---:|---:|---:|---:|
| accel_x | 1.7599 | 0.6248 | -0.3700 | 3.6200 |
| accel_y | 0.4173 | 0.4401 | -1.4600 | 2.1700 |
| accel_z | 10.0887 | 0.5928 | 0.0000 | 11.5100 |

## Action Stats

| joint | action_mean | action_min | action_max | saturation_pct |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0904 | -0.1779 | 0.2554 | 0.00 |
| left_hip_roll | 0.0332 | -0.1385 | 0.2880 | 0.00 |
| left_hip_pitch | -0.4297 | -0.7813 | 0.0016 | 0.00 |
| left_knee | -0.0270 | -0.4479 | 0.3193 | 0.00 |
| left_ankle | 0.3224 | 0.0880 | 0.6520 | 0.00 |
| neck_pitch | 0.5980 | 0.3930 | 0.7462 | 0.00 |
| head_pitch | -0.1747 | -0.3669 | 0.1624 | 0.00 |
| head_yaw | -0.2069 | -0.5260 | 0.0504 | 0.00 |
| head_roll | -0.1443 | -0.3644 | 0.0046 | 0.00 |
| right_hip_yaw | 0.0367 | -0.0821 | 0.1798 | 0.00 |
| right_hip_roll | -0.2319 | -0.4478 | -0.0101 | 0.00 |
| right_hip_pitch | 0.5410 | 0.0641 | 0.7333 | 0.00 |
| right_knee | 0.1158 | -0.1101 | 0.3925 | 0.00 |
| right_ankle | 0.5002 | 0.3121 | 0.7751 | 0.00 |

## Tracking Error

| joint | p50_abs_rad | p95_abs_rad | p99_abs_rad | max_abs_rad |
|---|---:|---:|---:|---:|
| left_hip_yaw | 0.0108 | 0.0372 | 0.0490 | 0.0624 |
| left_hip_roll | 0.0100 | 0.0368 | 0.0489 | 0.0632 |
| left_hip_pitch | 0.0170 | 0.0515 | 0.0641 | 0.1393 |
| left_knee | 0.0158 | 0.0580 | 0.0755 | 0.1070 |
| left_ankle | 0.0147 | 0.0459 | 0.0550 | 0.1199 |
| neck_pitch | 0.0119 | 0.0372 | 0.0764 | 0.1606 |
| head_pitch | 0.0070 | 0.0252 | 0.0388 | 0.0451 |
| head_yaw | 0.0184 | 0.0507 | 0.0650 | 0.0989 |
| head_roll | 0.0105 | 0.0279 | 0.0347 | 0.0701 |
| right_hip_yaw | 0.0074 | 0.0241 | 0.0317 | 0.0442 |
| right_hip_roll | 0.0115 | 0.0397 | 0.0512 | 0.0731 |
| right_hip_pitch | 0.0111 | 0.0430 | 0.0587 | 0.1068 |
| right_knee | 0.0094 | 0.0341 | 0.0541 | 0.0751 |
| right_ankle | 0.0133 | 0.0431 | 0.0539 | 0.1197 |

largest_tracking_spike: tick `3`, t=`1449.43032`, joint `neck_pitch`, abs_error_rad=`0.1606`
nearest_dt_spike_to_largest_tracking: `NONE`
tracking_spikes_gt_0.05_rad: `266`
- tick `3` t=`1449.43032` joint `neck_pitch` abs_error_rad=`0.1606`
- tick `2` t=`1449.41023` joint `neck_pitch` abs_error_rad=`0.1542`
- tick `2` t=`1449.41023` joint `left_hip_pitch` abs_error_rad=`0.1393`
- tick `4` t=`1449.45041` joint `neck_pitch` abs_error_rad=`0.1289`
- tick `3` t=`1449.43032` joint `left_hip_pitch` abs_error_rad=`0.1271`
- tick `2` t=`1449.41023` joint `left_ankle` abs_error_rad=`0.1199`
- tick `2` t=`1449.41023` joint `right_ankle` abs_error_rad=`0.1197`
- tick `5` t=`1449.47050` joint `neck_pitch` abs_error_rad=`0.1127`
- tick `1` t=`1449.39014` joint `right_ankle` abs_error_rad=`0.1098`
- tick `2` t=`1449.41023` joint `left_knee` abs_error_rad=`0.1070`

## Target Step And Rate Limit

| joint | pre_step_max_rad | post_step_max_rad | pre_to_post_delta_max_rad |
|---|---:|---:|---:|
| left_hip_yaw | 0.0681 | 0.0681 | 0.0000 |
| left_hip_roll | 0.0509 | 0.0509 | 0.0000 |
| left_hip_pitch | 0.0672 | 0.0672 | 0.0000 |
| left_knee | 0.0999 | 0.0999 | 0.0000 |
| left_ankle | 0.0610 | 0.0610 | 0.0000 |
| neck_pitch | 0.0308 | 0.0514 | 0.0245 |
| head_pitch | 0.0403 | 0.0403 | 0.0000 |
| head_yaw | 0.0352 | 0.0352 | 0.0000 |
| head_roll | 0.0275 | 0.0275 | 0.0000 |
| right_hip_yaw | 0.0317 | 0.0317 | 0.0000 |
| right_hip_roll | 0.0629 | 0.0629 | 0.0000 |
| right_hip_pitch | 0.0897 | 0.0888 | 0.0009 |
| right_knee | 0.0511 | 0.0511 | 0.0000 |
| right_ankle | 0.0407 | 0.0407 | 0.0082 |

## Pitch Posture Numeric Summary

Sign-to-physical-forward cannot be inferred from telemetry alone; use joint identity visual notes for direction.

| joint | scaled_delta_mean_rad | sent_target_mean_rad | sent_min | sent_max |
|---|---:|---:|---:|---:|
| left_hip_pitch | -0.1074 | -0.7374 | -0.8253 | -0.6296 |
| left_knee | -0.0068 | 1.3612 | 1.2560 | 1.4478 |
| left_ankle | 0.0806 | -0.7034 | -0.7620 | -0.6210 |
| right_hip_pitch | 0.1352 | 0.7702 | 0.6510 | 0.8183 |
| right_knee | 0.0289 | 1.4079 | 1.3515 | 1.4771 |
| right_ankle | 0.1250 | -0.6710 | -0.7180 | -0.6022 |

## Bus Counters

bus_status: `available`
read_error_count_max: `25`
write_error_count_max: `0`
last_error: `read_present_position: Checksum error`
