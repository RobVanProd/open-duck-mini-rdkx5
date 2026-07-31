# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/v9_four_surface_trace_recheck_x008_fitted/seed_006/trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `fitted`
samples: `58`
duration_s: `1.1400`

## Termination

- done_seen: `True`
- first_done_tick: `57`
- first_done_time_s: `1.1400`

## Body And Motion

- body_pitch_abs_p95_rad: `1.3675`
- body_pitch_abs_max_rad: `1.5263`
- base_height_min_m: `0.0233`
- local_forward_velocity_mean_m_s: `0.2749`
- local_forward_velocity_p95_m_s: `1.0882`
- progress_x_m: `0.0210`
- max_body_pitch_tick: `{'tick': 56, 'time_s': 1.12, 'body_pitch_rad': 1.5262652724651304}`

## Contacts

- foot_contact_counts: `{'left': 42, 'right': 48}`
- contact_events: `9`

## Largest Tracking Spike

`{'tick': 0, 'time_s': 0.0, 'joint': 'left_knee', 'error_rad': 0.46053338050842285, 'sent_target_rad': 1.4728000164031982, 'actual_position_rad': 1.0122666358947754}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 2.5044 | 1.5545 | 0.0673 | 0.0880 | 0.4027 | 0.0000 |
| left_knee | 2.1586 | 1.1781 | 0.0710 | 0.1616 | 0.3509 | 0.0000 |
| left_ankle | 1.8191 | 1.5694 | 0.0538 | 0.0811 | 0.3962 | 0.0000 |
| right_hip_pitch | 0.8665 | 0.5218 | 0.0345 | 0.0785 | 0.2322 | 0.0000 |
| right_knee | 1.5833 | 0.9408 | 0.0422 | 0.0719 | 0.3474 | 0.0000 |
| right_ankle | 1.9968 | 1.1123 | 0.0522 | 0.1415 | 0.3917 | 0.0000 |

## Tail Reward Terms

- `cost/action_rate` mean `0.0195` p95 `0.0759`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0021` p95 `0.0033`
- `reward/alive` mean `20.0000` p95 `20.0000`
- `reward/imitation` mean `-1.7633` p95 `0.6293`
- `reward/tracking_ang_vel` mean `2.7765` p95 `5.8223`
- `reward/tracking_lin_vel` mean `0.0593` p95 `0.3636`
