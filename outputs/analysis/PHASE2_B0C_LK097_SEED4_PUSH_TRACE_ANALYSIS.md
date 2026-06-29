# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/phase2_b0c_lk097_seed4_push_trace/trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `fitted`
samples: `250`
duration_s: `4.9800`

## Termination

- done_seen: `False`
- first_done_tick: `None`
- first_done_time_s: `NA`

## Body And Motion

- body_pitch_abs_p95_rad: `0.1402`
- body_pitch_abs_max_rad: `0.1830`
- base_height_min_m: `0.1506`
- local_forward_velocity_mean_m_s: `0.0343`
- local_forward_velocity_p95_m_s: `0.1069`
- progress_x_m: `0.0423`
- max_body_pitch_tick: `{'tick': 248, 'time_s': 4.96, 'body_pitch_rad': 0.18299625018107743}`

## Contacts

- foot_contact_counts: `{'left': 230, 'right': 226}`
- contact_events: `31`

## Largest Tracking Spike

`{'tick': 0, 'time_s': 0.0, 'joint': 'right_knee', 'error_rad': 0.31908273696899414, 'sent_target_rad': 1.417540431022644, 'actual_position_rad': 1.7366231679916382}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 1.3104 | 1.2097 | 0.0827 | 0.1368 | 0.7700 | 0.0000 |
| left_knee | 1.6354 | 1.5195 | 0.1022 | 0.2013 | 0.4538 | 0.0000 |
| left_ankle | 1.3957 | 1.3087 | 0.0917 | 0.1526 | 0.8589 | 0.0000 |
| right_hip_pitch | 1.5427 | 1.4565 | 0.0959 | 0.1282 | 0.7613 | 0.0000 |
| right_knee | 1.8002 | 1.6536 | 0.1098 | 0.1743 | 0.4350 | 0.0000 |
| right_ankle | 1.4277 | 1.3061 | 0.0902 | 0.1541 | 0.8265 | 0.0000 |

## Tail Reward Terms

- `cost/action_rate` mean `0.0185` p95 `0.0296`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0059` p95 `0.0092`
- `diagnostic/actuator_bridge_delay_ticks` mean `0.0000` p95 `0.0000`
- `diagnostic/actuator_bridge_tau_mean_s` mean `0.0200` p95 `0.0200`
- `diagnostic/actuator_bridge_tracking_cost` mean `0.0000` p95 `0.0000`
- `diagnostic/actuator_bridge_velocity_limit_mean_rad_s` mean `5.2400` p95 `5.2400`
- `diagnostic/behavior_prior_cost` mean `0.0000` p95 `0.0000`
- `diagnostic/command_progress_failure` mean `0.0000` p95 `0.0000`
- `diagnostic/command_progress_ratio` mean `0.4116` p95 `0.4274`
- `diagnostic/command_progress_shortfall_cost` mean `0.0357` p95 `0.0475`
- `diagnostic/forward_double_support_steps` mean `0.0000` p95 `0.0000`
- `diagnostic/forward_swing_imbalance` mean `0.0000` p95 `0.0000`
- `diagnostic/soft_prior_cost` mean `0.0000` p95 `0.0000`
- `diagnostic/soft_prior_phase` mean `0.0000` p95 `0.0000`
- `diagnostic/swing_peak_forward_advance` mean `0.0000` p95 `0.0000`
- `diagnostic/swing_peak_lift` mean `0.0000` p95 `0.0000`
- `diagnostic/target_velocity_cost` mean `0.0000` p95 `0.0000`
- `reward/alive` mean `20.0000` p95 `20.0000`
- `reward/imitation` mean `-0.0179` p95 `2.6538`
- `reward/tracking_ang_vel` mean `0.3860` p95 `1.8482`
- `reward/tracking_lin_vel` mean `2.2103` p95 `2.4452`
