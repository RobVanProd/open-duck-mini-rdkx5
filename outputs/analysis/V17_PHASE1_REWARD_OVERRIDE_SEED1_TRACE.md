# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/v17_phase1_reward_override_seed_sweep_cpu/v17_phase1/seed_001/trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `vanilla`
samples: `32`
duration_s: `0.6200`

## Termination

- done_seen: `True`
- first_done_tick: `31`
- first_done_time_s: `0.6200`

## Body And Motion

- body_pitch_abs_p95_rad: `0.2403`
- body_pitch_abs_max_rad: `0.2621`
- base_height_min_m: `0.1026`
- local_forward_velocity_mean_m_s: `-0.0996`
- local_forward_velocity_p95_m_s: `-0.0177`
- progress_x_m: `-0.2367`
- max_body_pitch_tick: `{'tick': 31, 'time_s': 0.62, 'body_pitch_rad': -0.26213840881735834}`

## Contacts

- foot_contact_counts: `{'left': 30, 'right': 2}`
- contact_events: `3`

## Largest Tracking Spike

`{'tick': 0, 'time_s': 0.0, 'joint': 'right_ankle', 'error_rad': 0.25872719287872314, 'sent_target_rad': -0.7554551362991333, 'actual_position_rad': -1.0141823291778564}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 0.4468 | 0.4468 | 0.0000 | 0.1797 | 0.1726 | 0.0000 |
| left_knee | 0.4878 | 0.4878 | 0.0000 | 0.1375 | 0.2967 | 0.0000 |
| left_ankle | 0.6460 | 0.6460 | 0.0000 | 0.0482 | 0.2245 | 0.0000 |
| right_hip_pitch | 0.5522 | 0.5522 | 0.0000 | 0.1013 | 0.0850 | 0.0000 |
| right_knee | 0.2061 | 0.2061 | 0.0000 | 0.0410 | 0.0849 | 0.0000 |
| right_ankle | 0.6897 | 0.6897 | 0.0000 | 0.1472 | 0.1483 | 0.0000 |

## Tail Reward Terms

- `cost/action_magnitude` mean `0.0001` p95 `0.0001`
- `cost/action_rate` mean `0.0000` p95 `0.0000`
- `cost/base_height` mean `0.0005` p95 `0.0007`
- `cost/command_progress_failure` mean `0.0000` p95 `-0.0000`
- `cost/command_progress_shortfall` mean `125.4240` p95 `208.6046`
- `cost/forward_contact_support` mean `0.0279` p95 `0.2200`
- `cost/forward_overshoot` mean `0.0000` p95 `0.0000`
- `cost/forward_pitch` mean `0.0120` p95 `0.0182`
- `cost/forward_pitch_rate` mean `0.0013` p95 `0.0055`
- `cost/forward_shortfall` mean `296.8661` p95 `956.8842`
- `cost/forward_wrong_direction` mean `154.2559` p95 `587.4681`
- `cost/orientation` mean `0.0339` p95 `0.0594`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/target_rate` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0008` p95 `0.0012`
- `diagnostic/actuator_bridge_delay_ticks` mean `0.0000` p95 `0.0000`
- `diagnostic/actuator_bridge_tau_mean_s` mean `0.0200` p95 `0.0200`
- `diagnostic/actuator_bridge_tracking_cost` mean `0.0000` p95 `0.0000`
- `diagnostic/actuator_bridge_velocity_limit_mean_rad_s` mean `5.2400` p95 `5.2400`
- `diagnostic/command_progress_failure` mean `0.0000` p95 `0.0000`
- `diagnostic/command_progress_ratio` mean `-0.8178` p95 `-0.6917`
- `diagnostic/command_progress_shortfall_cost` mean `1.7420` p95 `2.8973`
- `diagnostic/target_velocity_cost` mean `0.0000` p95 `0.0000`
- `reward/command_progress` mean `-27.8054` p95 `-23.5193`
- `reward/forward_progress` mean `0.0000` p95 `0.0000`
- `reward/tracking_lin_vel` mean `0.0000` p95 `0.0000`
