# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `c7_35120` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0208 | 0.2606 | 0.1129 | 0.1519 | 1.5158 | 0.0000 | 0.1885 | 0.0104 | 11.2000 | 88.8000 | 0 | NA |
| `c7_35120` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0262 | 0.3281 | 0.1126 | 0.1562 | 1.5429 | 0.0000 | 0.1729 | 0.0080 | 16.4000 | 83.2000 | 0 | NA |
| `c7_35120` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0286 | 0.3577 | 0.1057 | 0.1511 | 1.5021 | 0.0000 | 0.1815 | 0.0096 | 18.8000 | 81.2000 | 0 | NA |
| `c7_35120` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0132 | 0.1649 | 0.1253 | 0.1555 | 1.4786 | 0.0000 | 0.1811 | 0.0098 | 9.2000 | 90.8000 | 0 | NA |
| `c7_35120` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0153 | 0.1918 | 0.0761 | 0.1506 | 1.5353 | 0.0000 | 0.1739 | 0.0015 | 4.0000 | 96.0000 | 0 | NA |
| `c7_35120` | 5 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0260 | 0.3245 | 0.1121 | 0.1462 | 1.5948 | 0.0000 | 0.1918 | 0.0183 | 10.0000 | 89.2000 | 0 | NA |
| `c7_35120` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0209 | 0.2617 | 0.0967 | 0.1530 | 1.4707 | 0.0000 | 0.1787 | 0.0166 | 12.0000 | 88.0000 | 0 | NA |
| `c7_35120` | 7 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0198 | 0.2477 | 0.0979 | 0.1564 | 1.4558 | 0.0000 | 0.1818 | 0.0095 | 9.6000 | 90.4000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `c7_35120` | 8 | 0 | 8 | 250.0000 | 250 | 250 | 0.2671 | 0.0214 | 0.1049 | 0.1526 | 0.0000 | 0.0105 | 11.4000 | 88.4500 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
