# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/pitch_chain_4p3_ppo_shape_rate_student_gate_failure_traces/pitch_chain_4p3_ppo_shape_rate_student/seed_004/trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `fitted`
samples: `500`
duration_s: `9.9800`

## Termination

- done_seen: `False`
- first_done_tick: `None`
- first_done_time_s: `NA`

## Body And Motion

- body_pitch_abs_p95_rad: `0.0967`
- body_pitch_abs_max_rad: `0.1078`
- base_height_min_m: `0.1506`
- local_forward_velocity_mean_m_s: `0.0393`
- local_forward_velocity_p95_m_s: `0.1006`
- progress_x_m: `-0.0641`
- max_body_pitch_tick: `{'tick': 434, 'time_s': 8.68, 'body_pitch_rad': 0.10780266460247319}`

## Contacts

- foot_contact_counts: `{'left': 406, 'right': 418}`
- contact_events: `130`

## Largest Tracking Spike

`{'tick': 0, 'time_s': 0.0, 'joint': 'right_knee', 'error_rad': 0.32151174545288086, 'sent_target_rad': 1.4123268127441406, 'actual_position_rad': 1.7338385581970215}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 1.9529 | 1.4932 | 0.0927 | 0.1455 | 0.7679 | 0.0000 |
| left_knee | 2.6768 | 2.2341 | 0.1482 | 0.2177 | 0.5201 | 0.0000 |
| left_ankle | 2.5493 | 2.2216 | 0.1411 | 0.2011 | 0.8365 | 0.0000 |
| right_hip_pitch | 1.7474 | 1.5474 | 0.1043 | 0.1393 | 0.7821 | 0.0000 |
| right_knee | 3.7024 | 3.0000 | 0.2199 | 0.2561 | 0.6735 | 0.0000 |
| right_ankle | 2.5166 | 2.2500 | 0.1330 | 0.1914 | 0.8984 | 0.0000 |

## Tail Reward Terms

- `cost/action_rate` mean `0.0500` p95 `0.1137`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0077` p95 `0.0147`
- `diagnostic/actuator_bridge_delay_ticks` mean `0.0000` p95 `0.0000`
- `diagnostic/actuator_bridge_tau_mean_s` mean `0.0200` p95 `0.0200`
- `diagnostic/actuator_bridge_tracking_cost` mean `0.0000` p95 `0.0000`
- `diagnostic/actuator_bridge_velocity_limit_mean_rad_s` mean `5.2400` p95 `5.2400`
- `diagnostic/behavior_prior_cost` mean `0.0000` p95 `0.0000`
- `diagnostic/command_progress_failure` mean `0.0000` p95 `0.0000`
- `diagnostic/command_progress_ratio` mean `0.4908` p95 `0.4924`
- `diagnostic/command_progress_shortfall_cost` mean `0.0119` p95 `0.0124`
- `diagnostic/forward_double_support_steps` mean `0.0000` p95 `0.0000`
- `diagnostic/soft_prior_cost` mean `0.0000` p95 `0.0000`
- `diagnostic/soft_prior_phase` mean `0.0000` p95 `0.0000`
- `diagnostic/target_velocity_cost` mean `0.0000` p95 `0.0000`
- `reward/alive` mean `20.0000` p95 `20.0000`
- `reward/imitation` mean `1.2900` p95 `3.4635`
- `reward/tracking_ang_vel` mean `0.6719` p95 `5.4168`
- `reward/tracking_lin_vel` mean `2.1817` p95 `2.4779`
