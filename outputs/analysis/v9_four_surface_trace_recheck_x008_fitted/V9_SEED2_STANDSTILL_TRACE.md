# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/v9_four_surface_trace_recheck_x008_fitted/seed_002/trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `fitted`
samples: `750`
duration_s: `14.9800`

## Termination

- done_seen: `False`
- first_done_tick: `None`
- first_done_time_s: `NA`

## Body And Motion

- body_pitch_abs_p95_rad: `0.2060`
- body_pitch_abs_max_rad: `0.2609`
- base_height_min_m: `0.1503`
- local_forward_velocity_mean_m_s: `0.0020`
- local_forward_velocity_p95_m_s: `0.0059`
- progress_x_m: `-0.0138`
- max_body_pitch_tick: `{'tick': 27, 'time_s': 0.54, 'body_pitch_rad': 0.26094305273378393}`

## Contacts

- foot_contact_counts: `{'left': 748, 'right': 747}`
- contact_events: `3`

## Largest Tracking Spike

`{'tick': 0, 'time_s': 0.0, 'joint': 'left_knee', 'error_rad': 0.4235750436782837, 'sent_target_rad': 1.4712562561035156, 'actual_position_rad': 1.8948312997817993}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 0.1849 | 0.1755 | 0.0122 | 0.0275 | 0.1940 | 0.0000 |
| left_knee | 0.2337 | 0.2251 | 0.0158 | 0.0807 | 0.3203 | 0.0000 |
| left_ankle | 0.2751 | 0.2512 | 0.0175 | 0.0313 | 0.3825 | 0.0000 |
| right_hip_pitch | 0.1289 | 0.1191 | 0.0082 | 0.0354 | 0.1939 | 0.0000 |
| right_knee | 0.2290 | 0.2242 | 0.0154 | 0.0827 | 0.2605 | 0.0000 |
| right_ankle | 0.2641 | 0.2602 | 0.0180 | 0.0567 | 0.3258 | 0.0000 |

## Tail Reward Terms

- `cost/action_rate` mean `0.0008` p95 `0.0013`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0020` p95 `0.0025`
- `reward/alive` mean `20.0000` p95 `20.0000`
- `reward/imitation` mean `-0.0746` p95 `1.8452`
- `reward/tracking_ang_vel` mean `5.9651` p95 `5.9987`
- `reward/tracking_lin_vel` mean `1.3360` p95 `1.4387`
