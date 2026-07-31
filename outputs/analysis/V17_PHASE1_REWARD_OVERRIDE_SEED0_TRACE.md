# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/v17_phase1_reward_override_seed_sweep_cpu/v17_phase1/seed_000/trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `vanilla`
samples: `60`
duration_s: `1.1800`

## Termination

- done_seen: `True`
- first_done_tick: `59`
- first_done_time_s: `1.1800`

## Body And Motion

- body_pitch_abs_p95_rad: `0.1681`
- body_pitch_abs_max_rad: `0.1695`
- base_height_min_m: `0.1536`
- local_forward_velocity_mean_m_s: `0.0111`
- local_forward_velocity_p95_m_s: `0.0850`
- progress_x_m: `-0.0069`
- max_body_pitch_tick: `{'tick': 25, 'time_s': 0.5, 'body_pitch_rad': 0.16947002874249342}`

## Contacts

- foot_contact_counts: `{'left': 57, 'right': 60}`
- contact_events: `3`

## Largest Tracking Spike

`{'tick': 0, 'time_s': 0.0, 'joint': 'left_knee', 'error_rad': 0.4450857639312744, 'sent_target_rad': 1.4275941848754883, 'actual_position_rad': 1.8726799488067627}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 0.3909 | 0.3909 | 0.0000 | 0.0900 | 0.2081 | 0.0000 |
| left_knee | 0.3057 | 0.3057 | 0.0000 | 0.0686 | 0.2425 | 0.0000 |
| left_ankle | 0.5592 | 0.5592 | 0.0000 | 0.0463 | 0.2498 | 0.0000 |
| right_hip_pitch | 0.3408 | 0.3408 | 0.0000 | 0.0415 | 0.0758 | 0.0000 |
| right_knee | 0.5901 | 0.5901 | 0.0000 | 0.0697 | 0.0945 | 0.0000 |
| right_ankle | 0.1630 | 0.1630 | 0.0000 | 0.1169 | 0.1925 | 0.0000 |

## Tail Reward Terms

- `cost/action_magnitude` mean `0.0001` p95 `0.0001`
- `cost/action_rate` mean `0.0000` p95 `0.0000`
- `cost/base_height` mean `0.0000` p95 `0.0000`
- `cost/command_progress_failure` mean `13.0000` p95 `13.0000`
- `cost/command_progress_shortfall` mean `10.2369` p95 `12.0599`
- `cost/forward_contact_support` mean `0.0000` p95 `0.0000`
- `cost/forward_overshoot` mean `0.0000` p95 `0.0000`
- `cost/forward_pitch` mean `0.0004` p95 `0.0004`
- `cost/forward_pitch_rate` mean `0.0001` p95 `0.0001`
- `cost/forward_shortfall` mean `23.6122` p95 `40.5783`
- `cost/forward_wrong_direction` mean `1.3346` p95 `4.6678`
- `cost/orientation` mean `0.0007` p95 `0.0009`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/target_rate` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0013` p95 `0.0017`
- `diagnostic/actuator_bridge_delay_ticks` mean `0.0000` p95 `0.0000`
- `diagnostic/actuator_bridge_tau_mean_s` mean `0.0200` p95 `0.0200`
- `diagnostic/actuator_bridge_tracking_cost` mean `0.0000` p95 `0.0000`
- `diagnostic/actuator_bridge_velocity_limit_mean_rad_s` mean `5.2400` p95 `5.2400`
- `diagnostic/command_progress_failure` mean `0.0500` p95 `0.0500`
- `diagnostic/command_progress_ratio` mean `0.1743` p95 `0.2360`
- `diagnostic/command_progress_shortfall_cost` mean `0.1422` p95 `0.1675`
- `diagnostic/target_velocity_cost` mean `0.0000` p95 `0.0000`
- `reward/command_progress` mean `5.9259` p95 `8.0245`
- `reward/forward_progress` mean `0.1302` p95 `0.8099`
- `reward/tracking_lin_vel` mean `0.0505` p95 `0.1181`
