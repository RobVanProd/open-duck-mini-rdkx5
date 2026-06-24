# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/v9_four_surface_trace_recheck_x008_fitted/seed_007/trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `fitted`
samples: `27`
duration_s: `0.5200`

## Termination

- done_seen: `True`
- first_done_tick: `26`
- first_done_time_s: `0.5200`

## Body And Motion

- body_pitch_abs_p95_rad: `0.1007`
- body_pitch_abs_max_rad: `0.1032`
- base_height_min_m: `0.0919`
- local_forward_velocity_mean_m_s: `-0.0060`
- local_forward_velocity_p95_m_s: `0.1102`
- progress_x_m: `0.0267`
- max_body_pitch_tick: `{'tick': 21, 'time_s': 0.42, 'body_pitch_rad': 0.10322661356118545}`

## Contacts

- foot_contact_counts: `{'left': 3, 'right': 26}`
- contact_events: `3`

## Largest Tracking Spike

`{'tick': 0, 'time_s': 0.0, 'joint': 'left_knee', 'error_rad': 0.5683431625366211, 'sent_target_rad': 1.4728000164031982, 'actual_position_rad': 0.9044568538665771}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 2.3741 | 1.8431 | 0.0861 | 0.2335 | 0.3644 | 0.0000 |
| left_knee | 1.5239 | 1.2622 | 0.1063 | 0.5010 | 0.4925 | 0.0000 |
| left_ankle | 1.5355 | 2.3412 | 0.1158 | 0.0770 | 0.5695 | 0.0000 |
| right_hip_pitch | 0.8552 | 0.5520 | 0.0305 | 0.0717 | 0.1911 | 0.0000 |
| right_knee | 1.2645 | 1.8128 | 0.1193 | 0.1094 | 0.6232 | 0.0000 |
| right_ankle | 1.1631 | 1.0893 | 0.0719 | 0.1291 | 0.4024 | 0.0000 |

## Tail Reward Terms

- `cost/action_rate` mean `0.0081` p95 `0.0301`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0026` p95 `0.0052`
- `reward/alive` mean `20.0000` p95 `20.0000`
- `reward/imitation` mean `-1.6572` p95 `0.8052`
- `reward/tracking_ang_vel` mean `1.2058` p95 `5.3675`
- `reward/tracking_lin_vel` mean `0.0000` p95 `0.0000`
