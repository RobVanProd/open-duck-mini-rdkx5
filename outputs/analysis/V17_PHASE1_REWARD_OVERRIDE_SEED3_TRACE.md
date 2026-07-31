# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/v17_phase1_reward_override_seed_sweep_cpu/v17_phase1/seed_003/trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `vanilla`
samples: `60`
duration_s: `1.1800`

## Termination

- done_seen: `True`
- first_done_tick: `59`
- first_done_time_s: `1.1800`

## Body And Motion

- body_pitch_abs_p95_rad: `0.1465`
- body_pitch_abs_max_rad: `0.1473`
- base_height_min_m: `0.1561`
- local_forward_velocity_mean_m_s: `-0.0055`
- local_forward_velocity_p95_m_s: `0.0662`
- progress_x_m: `-0.0101`
- max_body_pitch_tick: `{'tick': 23, 'time_s': 0.46, 'body_pitch_rad': 0.14725532771968028}`

## Contacts

- foot_contact_counts: `{'left': 54, 'right': 51}`
- contact_events: `3`

## Largest Tracking Spike

`{'tick': 0, 'time_s': 0.0, 'joint': 'left_ankle', 'error_rad': 0.2806137204170227, 'sent_target_rad': -0.6924387812614441, 'actual_position_rad': -0.9730525016784668}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 0.3520 | 0.3520 | 0.0000 | 0.0494 | 0.2128 | 0.0000 |
| left_knee | 0.3818 | 0.3818 | 0.0000 | 0.0969 | 0.2335 | 0.0000 |
| left_ankle | 0.5012 | 0.5012 | 0.0000 | 0.0649 | 0.2613 | 0.0000 |
| right_hip_pitch | 0.5666 | 0.5666 | 0.0000 | 0.0400 | 0.0959 | 0.0000 |
| right_knee | 0.3168 | 0.3168 | 0.0000 | 0.0774 | 0.0453 | 0.0000 |
| right_ankle | 0.4191 | 0.4191 | 0.0000 | 0.0818 | 0.1576 | 0.0000 |

## Tail Reward Terms

- `cost/action_magnitude` mean `0.0001` p95 `0.0001`
- `cost/action_rate` mean `0.0000` p95 `0.0000`
- `cost/base_height` mean `0.0000` p95 `0.0000`
- `cost/command_progress_failure` mean `13.0000` p95 `13.0000`
- `cost/command_progress_shortfall` mean `29.4551` p95 `31.7096`
- `cost/forward_contact_support` mean `0.0000` p95 `0.0000`
- `cost/forward_overshoot` mean `0.0000` p95 `0.0000`
- `cost/forward_pitch` mean `0.0002` p95 `0.0003`
- `cost/forward_pitch_rate` mean `0.0000` p95 `0.0000`
- `cost/forward_shortfall` mean `14.5870` p95 `18.7752`
- `cost/forward_wrong_direction` mean `0.0374` p95 `0.1199`
- `cost/orientation` mean `0.0007` p95 `0.0007`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/target_rate` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0013` p95 `0.0016`
- `diagnostic/actuator_bridge_delay_ticks` mean `0.0000` p95 `0.0000`
- `diagnostic/actuator_bridge_tau_mean_s` mean `0.0200` p95 `0.0200`
- `diagnostic/actuator_bridge_tracking_cost` mean `0.0000` p95 `0.0000`
- `diagnostic/actuator_bridge_velocity_limit_mean_rad_s` mean `5.2400` p95 `5.2400`
- `diagnostic/command_progress_failure` mean `0.0500` p95 `0.0500`
- `diagnostic/command_progress_ratio` mean `-0.0894` p95 `-0.0704`
- `diagnostic/command_progress_shortfall_cost` mean `0.4091` p95 `0.4404`
- `diagnostic/target_velocity_cost` mean `0.0000` p95 `0.0000`
- `reward/command_progress` mean `-3.0406` p95 `-2.3941`
- `reward/forward_progress` mean `0.8027` p95 `1.8219`
- `reward/tracking_lin_vel` mean `0.1184` p95 `0.1895`
