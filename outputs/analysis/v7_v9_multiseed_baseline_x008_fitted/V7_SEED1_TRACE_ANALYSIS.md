# Closed-Loop Failure Trace Analysis

source: `outputs/analysis/v7_v9_multiseed_baseline_x008_fitted/movement_bootstrap_v7_checkpoint_anchor_20260623/seed_001/trace.jsonl`
status: `PASS_TRACE_ANALYZED`
mode: `fitted`
samples: `32`
duration_s: `0.6200`

## Termination

- done_seen: `True`
- first_done_tick: `31`
- first_done_time_s: `0.6200`

## Body And Motion

- body_pitch_abs_p95_rad: `0.0499`
- body_pitch_abs_max_rad: `0.0507`
- base_height_min_m: `0.0688`
- local_forward_velocity_mean_m_s: `0.0005`
- local_forward_velocity_p95_m_s: `0.0478`
- progress_x_m: `-0.2541`
- max_body_pitch_tick: `{'tick': 19, 'time_s': 0.38, 'body_pitch_rad': -0.05068909598104993}`

## Contacts

- foot_contact_counts: `{'left': 28, 'right': 2}`
- contact_events: `8`

## Largest Tracking Spike

`{'tick': 0, 'time_s': 0.0, 'joint': 'right_ankle', 'error_rad': 0.23666024208068848, 'sent_target_rad': -0.7780523300170898, 'actual_position_rad': -1.0147125720977783}`

## Pitch-Chain Joints

| joint | sent_vel_p95 | applied_vel_p95 | bridge_track_p95 | joint_track_p95 | action_abs_p95 | sat_pct |
|---|---:|---:|---:|---:|---:|---:|
| left_hip_pitch | 1.5790 | 1.4054 | 0.0682 | 0.1796 | 0.1901 | 0.0000 |
| left_knee | 1.6299 | 1.4377 | 0.0707 | 0.1732 | 0.4983 | 0.0000 |
| left_ankle | 1.2154 | 1.8290 | 0.1240 | 0.1337 | 0.6131 | 0.0000 |
| right_hip_pitch | 0.9944 | 0.8792 | 0.0422 | 0.0707 | 0.1771 | 0.0000 |
| right_knee | 1.7057 | 1.1871 | 0.0811 | 0.1206 | 0.4335 | 0.0000 |
| right_ankle | 1.5586 | 0.9818 | 0.0621 | 0.1241 | 0.3273 | 0.0000 |

## Tail Reward Terms

- `cost/action_rate` mean `0.0074` p95 `0.0304`
- `cost/stand_still` mean `0.0000` p95 `0.0000`
- `cost/torques` mean `0.0011` p95 `0.0022`
- `reward/alive` mean `20.0000` p95 `20.0000`
- `reward/imitation` mean `-2.0724` p95 `0.1573`
- `reward/tracking_ang_vel` mean `0.6151` p95 `4.1950`
- `reward/tracking_lin_vel` mean `0.0002` p95 `0.0015`
