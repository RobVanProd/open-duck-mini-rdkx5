# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/v9_four_surface_trace_recheck_x008_fitted/seed_005/trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `fitted`
samples: `56`
duration_s: `1.1000`

## Termination

- done_seen: `True`
- first_done_tick: `55`
- first_done_time_s: `1.1000`

## Body And Motion

- body_pitch_abs_p95_rad: `1.3208`
- body_pitch_abs_max_rad: `1.5673`
- base_height_min_m: `0.0298`
- local_forward_velocity_mean_m_s: `-0.3045`
- local_forward_velocity_p95_m_s: `0.1021`
- progress_x_m: `0.1478`
- max_body_pitch_tick: `{'tick': 54, 'time_s': 1.08, 'body_pitch_rad': -1.5672565528748845}`

## Contacts

- foot_contact_counts: `{'left': 49, 'right': 49}`
- contact_events: `11`

## Largest Tracking Spike

`{'tick': 0, 'time_s': 0.0, 'joint': 'right_knee', 'error_rad': 0.5412642955780029, 'sent_target_rad': 1.3664737939834595, 'actual_position_rad': 1.9077380895614624}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 2.1236 | 1.4364 | 0.0903 | 0.1309 | 0.3687 | 0.0000 |
| left_knee | 1.2673 | 1.2561 | 0.0827 | 0.1251 | 0.5547 | 0.0000 |
| left_ankle | 1.0750 | 1.6262 | 0.0923 | 0.1182 | 0.5828 | 0.0000 |
| right_hip_pitch | 1.1215 | 0.9807 | 0.0467 | 0.0897 | 0.2433 | 0.0000 |
| right_knee | 2.1837 | 1.2175 | 0.0309 | 0.1647 | 0.4525 | 0.0000 |
| right_ankle | 1.5434 | 2.2500 | 0.1189 | 0.1291 | 0.8130 | 0.0000 |

## Tail Reward Terms

- `cost/action_rate` mean `0.0142` p95 `0.0432`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0010` p95 `0.0013`
- `reward/alive` mean `20.0000` p95 `20.0000`
- `reward/imitation` mean `-1.6503` p95 `0.7367`
- `reward/tracking_ang_vel` mean `2.6705` p95 `5.4252`
- `reward/tracking_lin_vel` mean `0.0000` p95 `0.0000`
