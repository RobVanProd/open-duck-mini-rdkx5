# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/pitch_chain_4p3_ppo_shape_rate_student_gate_failure_traces/pitch_chain_4p3_ppo_shape_rate_student/seed_001/trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `fitted`
samples: `500`
duration_s: `9.9800`

## Termination

- done_seen: `False`
- first_done_tick: `None`
- first_done_time_s: `NA`

## Body And Motion

- body_pitch_abs_p95_rad: `0.0991`
- body_pitch_abs_max_rad: `0.1081`
- base_height_min_m: `0.1556`
- local_forward_velocity_mean_m_s: `0.0359`
- local_forward_velocity_p95_m_s: `0.0938`
- progress_x_m: `0.0266`
- max_body_pitch_tick: `{'tick': 465, 'time_s': 9.3, 'body_pitch_rad': 0.10808180166976063}`

## Contacts

- foot_contact_counts: `{'left': 398, 'right': 405}`
- contact_events: `132`

## Largest Tracking Spike

`{'tick': 0, 'time_s': 0.0, 'joint': 'left_hip_pitch', 'error_rad': 0.38306358456611633, 'sent_target_rad': -0.7347999811172485, 'actual_position_rad': -0.3517363965511322}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 1.9903 | 1.5508 | 0.0924 | 0.1442 | 0.7651 | 0.0000 |
| left_knee | 2.7930 | 2.3138 | 0.1496 | 0.2213 | 0.5389 | 0.0000 |
| left_ankle | 2.7956 | 2.4521 | 0.1507 | 0.2057 | 0.8365 | 0.0000 |
| right_hip_pitch | 1.8072 | 1.5708 | 0.1045 | 0.1391 | 0.7874 | 0.0000 |
| right_knee | 3.7059 | 3.0000 | 0.2196 | 0.2554 | 0.6834 | 0.0000 |
| right_ankle | 2.4310 | 2.2500 | 0.1368 | 0.1988 | 0.8990 | 0.0000 |

## Tail Reward Terms

- `cost/action_rate` mean `0.0501` p95 `0.0980`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0087` p95 `0.0168`
- `diagnostic/actuator_bridge_delay_ticks` mean `0.0000` p95 `0.0000`
- `diagnostic/actuator_bridge_tau_mean_s` mean `0.0200` p95 `0.0200`
- `diagnostic/actuator_bridge_tracking_cost` mean `0.0000` p95 `0.0000`
- `diagnostic/actuator_bridge_velocity_limit_mean_rad_s` mean `5.2400` p95 `5.2400`
- `diagnostic/behavior_prior_cost` mean `0.0000` p95 `0.0000`
- `diagnostic/command_progress_failure` mean `0.0000` p95 `0.0000`
- `diagnostic/command_progress_ratio` mean `0.4519` p95 `0.4547`
- `diagnostic/command_progress_shortfall_cost` mean `0.0219` p95 `0.0228`
- `diagnostic/forward_double_support_steps` mean `0.0000` p95 `0.0000`
- `diagnostic/soft_prior_cost` mean `0.0000` p95 `0.0000`
- `diagnostic/soft_prior_phase` mean `0.0000` p95 `0.0000`
- `diagnostic/target_velocity_cost` mean `0.0000` p95 `0.0000`
- `reward/alive` mean `20.0000` p95 `20.0000`
- `reward/imitation` mean `1.8599` p95 `3.4837`
- `reward/tracking_ang_vel` mean `0.4830` p95 `2.3485`
- `reward/tracking_lin_vel` mean `1.8618` p95 `2.3499`
