# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/v7_v9_multiseed_baseline_x008_fitted/movement_bootstrap_v9_progress_balanced_standstill_20260623/seed_000/trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `fitted`
samples: `73`
duration_s: `1.4400`

## Termination

- done_seen: `True`
- first_done_tick: `72`
- first_done_time_s: `1.4400`

## Body And Motion

- body_pitch_abs_p95_rad: `1.2604`
- body_pitch_abs_max_rad: `1.5235`
- base_height_min_m: `0.0305`
- local_forward_velocity_mean_m_s: `0.2217`
- local_forward_velocity_p95_m_s: `0.9827`
- progress_x_m: `-0.1467`
- max_body_pitch_tick: `{'tick': 71, 'time_s': 1.42, 'body_pitch_rad': 1.5234985781367167}`

## Contacts

- foot_contact_counts: `{'left': 61, 'right': 70}`
- contact_events: `10`

## Largest Tracking Spike

`{'tick': 0, 'time_s': 0.0, 'joint': 'left_knee', 'error_rad': 0.4128164052963257, 'sent_target_rad': 1.4599536657333374, 'actual_position_rad': 1.872770071029663}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 2.3669 | 1.5200 | 0.0892 | 0.1161 | 0.3116 | 0.0000 |
| left_knee | 2.0125 | 1.2697 | 0.0562 | 0.1180 | 0.4838 | 0.0000 |
| left_ankle | 1.4498 | 1.1892 | 0.0610 | 0.1450 | 0.4427 | 0.0000 |
| right_hip_pitch | 0.9255 | 0.9744 | 0.0284 | 0.0418 | 0.2596 | 0.0000 |
| right_knee | 1.5637 | 0.7727 | 0.0444 | 0.1072 | 0.3563 | 0.0000 |
| right_ankle | 1.7897 | 1.4253 | 0.0940 | 0.1498 | 0.4465 | 0.0000 |

## Tail Reward Terms

- `cost/action_rate` mean `0.0327` p95 `0.1153`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0025` p95 `0.0034`
- `reward/alive` mean `20.0000` p95 `20.0000`
- `reward/imitation` mean `-2.0553` p95 `0.8461`
- `reward/tracking_ang_vel` mean `1.3975` p95 `4.5322`
- `reward/tracking_lin_vel` mean `0.1443` p95 `0.8465`
