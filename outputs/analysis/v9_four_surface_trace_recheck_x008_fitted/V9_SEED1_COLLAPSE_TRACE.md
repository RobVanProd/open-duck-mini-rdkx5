# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/v7_v9_multiseed_baseline_x008_fitted/movement_bootstrap_v9_progress_balanced_standstill_20260623/seed_001/trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `fitted`
samples: `32`
duration_s: `0.6200`

## Termination

- done_seen: `True`
- first_done_tick: `31`
- first_done_time_s: `0.6200`

## Body And Motion

- body_pitch_abs_p95_rad: `0.0496`
- body_pitch_abs_max_rad: `0.0599`
- base_height_min_m: `0.0672`
- local_forward_velocity_mean_m_s: `0.0185`
- local_forward_velocity_p95_m_s: `0.1115`
- progress_x_m: `-0.2538`
- max_body_pitch_tick: `{'tick': 31, 'time_s': 0.62, 'body_pitch_rad': 0.059850022869131936}`

## Contacts

- foot_contact_counts: `{'left': 30, 'right': 2}`
- contact_events: `5`

## Largest Tracking Spike

`{'tick': 1, 'time_s': 0.02, 'joint': 'left_hip_pitch', 'error_rad': 0.22920656204223633, 'sent_target_rad': -0.6215541362762451, 'actual_position_rad': -0.3923475742340088}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 1.7712 | 1.5503 | 0.0738 | 0.1850 | 0.2162 | 0.0000 |
| left_knee | 1.4909 | 1.2453 | 0.0723 | 0.1704 | 0.5107 | 0.0000 |
| left_ankle | 1.3668 | 1.9508 | 0.1272 | 0.1397 | 0.6430 | 0.0000 |
| right_hip_pitch | 1.2450 | 0.9566 | 0.0525 | 0.0718 | 0.2123 | 0.0000 |
| right_knee | 1.6589 | 1.1872 | 0.0823 | 0.1232 | 0.4405 | 0.0000 |
| right_ankle | 1.5209 | 1.1405 | 0.0817 | 0.1222 | 0.3714 | 0.0000 |

## Tail Reward Terms

- `cost/action_rate` mean `0.0050` p95 `0.0323`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0013` p95 `0.0027`
- `reward/alive` mean `20.0000` p95 `20.0000`
- `reward/imitation` mean `-2.0290` p95 `0.2192`
- `reward/tracking_ang_vel` mean `0.3764` p95 `2.0867`
- `reward/tracking_lin_vel` mean `0.0003` p95 `0.0020`
