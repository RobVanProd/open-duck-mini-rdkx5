# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/v7_v9_multiseed_baseline_x008_fitted/movement_bootstrap_v7_checkpoint_anchor_20260623/seed_000/trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `fitted`
samples: `59`
duration_s: `1.1600`

## Termination

- done_seen: `True`
- first_done_tick: `58`
- first_done_time_s: `1.1600`

## Body And Motion

- body_pitch_abs_p95_rad: `1.2927`
- body_pitch_abs_max_rad: `1.4993`
- base_height_min_m: `0.0388`
- local_forward_velocity_mean_m_s: `0.2654`
- local_forward_velocity_p95_m_s: `1.0105`
- progress_x_m: `-0.1432`
- max_body_pitch_tick: `{'tick': 58, 'time_s': 1.16, 'body_pitch_rad': 1.4993353370372606}`

## Contacts

- foot_contact_counts: `{'left': 51, 'right': 57}`
- contact_events: `7`

## Largest Tracking Spike

`{'tick': 0, 'time_s': 0.0, 'joint': 'left_knee', 'error_rad': 0.405664324760437, 'sent_target_rad': 1.4670907258987427, 'actual_position_rad': 1.8727550506591797}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 1.8118 | 1.3940 | 0.0882 | 0.1057 | 0.2940 | 0.0000 |
| left_knee | 1.3423 | 0.9591 | 0.0474 | 0.1080 | 0.4910 | 0.0000 |
| left_ankle | 1.4328 | 1.5328 | 0.0586 | 0.1475 | 0.4404 | 0.0000 |
| right_hip_pitch | 0.6330 | 0.6998 | 0.0224 | 0.0448 | 0.2352 | 0.0000 |
| right_knee | 1.3329 | 0.8373 | 0.0410 | 0.0999 | 0.3483 | 0.0000 |
| right_ankle | 1.8009 | 1.4990 | 0.1043 | 0.2108 | 0.4648 | 0.0000 |

## Tail Reward Terms

- `cost/action_rate` mean `0.0074` p95 `0.0396`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0021` p95 `0.0033`
- `reward/alive` mean `20.0000` p95 `20.0000`
- `reward/imitation` mean `-1.7911` p95 `0.7597`
- `reward/tracking_ang_vel` mean `3.3070` p95 `5.9037`
- `reward/tracking_lin_vel` mean `0.1344` p95 `0.7927`
