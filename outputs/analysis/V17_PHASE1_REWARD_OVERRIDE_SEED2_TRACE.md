# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/v17_phase1_reward_override_seed_sweep_cpu/v17_phase1/seed_002/trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `vanilla`
samples: `60`
duration_s: `1.1800`

## Termination

- done_seen: `True`
- first_done_tick: `59`
- first_done_time_s: `1.1800`

## Body And Motion

- body_pitch_abs_p95_rad: `0.1274`
- body_pitch_abs_max_rad: `0.1281`
- base_height_min_m: `0.1525`
- local_forward_velocity_mean_m_s: `0.0182`
- local_forward_velocity_p95_m_s: `0.0791`
- progress_x_m: `-0.0131`
- max_body_pitch_tick: `{'tick': 25, 'time_s': 0.5, 'body_pitch_rad': 0.12813277251898755}`

## Contacts

- foot_contact_counts: `{'left': 58, 'right': 59}`
- contact_events: `3`

## Largest Tracking Spike

`{'tick': 0, 'time_s': 0.0, 'joint': 'left_knee', 'error_rad': 0.4480656385421753, 'sent_target_rad': 1.4467394351959229, 'actual_position_rad': 1.8948050737380981}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 0.3241 | 0.3241 | 0.0000 | 0.1320 | 0.2038 | 0.0000 |
| left_knee | 0.4668 | 0.4668 | 0.0000 | 0.0538 | 0.2902 | 0.0000 |
| left_ankle | 0.4908 | 0.4908 | 0.0000 | 0.0384 | 0.2437 | 0.0000 |
| right_hip_pitch | 0.4157 | 0.4157 | 0.0000 | 0.0675 | 0.0722 | 0.0000 |
| right_knee | 0.3110 | 0.3110 | 0.0000 | 0.0775 | 0.1688 | 0.0000 |
| right_ankle | 0.2240 | 0.2240 | 0.0000 | 0.0988 | 0.1891 | 0.0000 |

## Tail Reward Terms

- `cost/action_magnitude` mean `0.0001` p95 `0.0001`
- `cost/action_rate` mean `0.0000` p95 `0.0000`
- `cost/base_height` mean `0.0000` p95 `0.0000`
- `cost/command_progress_failure` mean `13.0000` p95 `13.0000`
- `cost/command_progress_shortfall` mean `5.7134` p95 `7.2976`
- `cost/forward_contact_support` mean `0.0000` p95 `0.0000`
- `cost/forward_overshoot` mean `0.0000` p95 `0.0000`
- `cost/forward_pitch` mean `0.0003` p95 `0.0003`
- `cost/forward_pitch_rate` mean `0.0000` p95 `0.0000`
- `cost/forward_shortfall` mean `14.7685` p95 `17.0626`
- `cost/forward_wrong_direction` mean `0.0058` p95 `0.0232`
- `cost/orientation` mean `0.0007` p95 `0.0008`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/target_rate` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0015` p95 `0.0018`
- `diagnostic/actuator_bridge_delay_ticks` mean `0.0000` p95 `0.0000`
- `diagnostic/actuator_bridge_tau_mean_s` mean `0.0200` p95 `0.0200`
- `diagnostic/actuator_bridge_tracking_cost` mean `0.0000` p95 `0.0000`
- `diagnostic/actuator_bridge_velocity_limit_mean_rad_s` mean `5.2400` p95 `5.2400`
- `diagnostic/command_progress_failure` mean `0.0500` p95 `0.0500`
- `diagnostic/command_progress_ratio` mean `0.2697` p95 `0.3161`
- `diagnostic/command_progress_shortfall_cost` mean `0.0794` p95 `0.1014`
- `diagnostic/target_velocity_cost` mean `0.0000` p95 `0.0000`
- `reward/command_progress` mean `9.1695` p95 `10.7468`
- `reward/forward_progress` mean `0.5687` p95 `1.8114`
- `reward/tracking_lin_vel` mean `0.1072` p95 `0.1886`
