# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/movement_bootstrap_v5_phase1_x008_failure_trace/phase1_x008_trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `fitted`
samples: `80`
duration_s: `1.5800`

## Termination

- done_seen: `True`
- first_done_tick: `79`
- first_done_time_s: `1.5800`

## Body And Motion

- body_pitch_abs_p95_rad: `1.1841`
- body_pitch_abs_max_rad: `1.4642`
- base_height_min_m: `0.0434`
- local_forward_velocity_mean_m_s: `0.1892`
- local_forward_velocity_p95_m_s: `0.8536`
- progress_x_m: `-0.1389`
- max_body_pitch_tick: `{'tick': 79, 'time_s': 1.58, 'body_pitch_rad': 1.4642007440723617}`

## Contacts

- foot_contact_counts: `{'left': 71, 'right': 74}`
- contact_events: `13`

## Largest Tracking Spike

`{'tick': 1, 'time_s': 0.02, 'joint': 'right_ankle', 'error_rad': 0.4179847836494446, 'sent_target_rad': -0.6080620884895325, 'actual_position_rad': -1.026046872138977}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 1.2992 | 1.3415 | 0.0853 | 0.1253 | 0.3881 | 0.0000 |
| left_knee | 0.9235 | 0.7040 | 0.0402 | 0.1052 | 0.3929 | 0.0000 |
| left_ankle | 1.1361 | 1.0456 | 0.0528 | 0.0859 | 0.4945 | 0.0000 |
| right_hip_pitch | 0.6453 | 0.7428 | 0.0236 | 0.0468 | 0.2108 | 0.0000 |
| right_knee | 1.9529 | 1.1268 | 0.0413 | 0.0841 | 0.2298 | 0.0000 |
| right_ankle | 1.3538 | 1.4963 | 0.1049 | 0.1429 | 0.5707 | 0.0000 |

## Tail Reward Terms

- `cost/action_rate` mean `0.0113` p95 `0.0446`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0022` p95 `0.0029`
- `reward/alive` mean `20.0000` p95 `20.0000`
- `reward/imitation` mean `-1.5913` p95 `0.0992`
- `reward/tracking_ang_vel` mean `0.6176` p95 `3.9604`
- `reward/tracking_lin_vel` mean `0.2053` p95 `1.1716`
