# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[0]`
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
| `c7_0` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0325 | 0.4061 | 0.1399 | 0.1519 | 1.7902 | 0.0000 | 0.2046 | 0.0165 | 20.8000 | 79.2000 | 0 | NA |
| `c7_35120` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0208 | 0.2606 | 0.1129 | 0.1519 | 1.5158 | 0.0000 | 0.1885 | 0.0104 | 11.2000 | 88.8000 | 0 | NA |
| `c7_70240` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0040 | 0.0499 | 0.0377 | 0.1519 | 1.4579 | 0.0000 | 0.1602 | 0.0207 | 0.8000 | 99.2000 | 0 | NA |
| `c7_105360` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0184 | 0.2295 | 0.1145 | 0.1519 | 1.5606 | 0.0000 | 0.1779 | 0.0121 | 11.2000 | 88.8000 | 0 | NA |
| `c7_140480` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0051 | 0.0633 | 0.0601 | 0.1519 | 1.6781 | 0.0000 | 0.1813 | 0.0207 | 1.2000 | 98.8000 | 0 | NA |
| `c7_175600` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0043 | 0.0536 | 0.0487 | 0.1519 | 1.4992 | 0.0000 | 0.1587 | 0.0206 | 0.8000 | 99.2000 | 0 | NA |
| `c7_210720` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0164 | 0.2052 | 0.1086 | 0.1519 | 1.6933 | 0.0000 | 0.2024 | 0.0114 | 10.0000 | 90.0000 | 0 | NA |
| `c7_245840` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0145 | 0.1811 | 0.1127 | 0.1519 | 1.5812 | 0.0000 | 0.1924 | 0.0103 | 6.4000 | 93.6000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `c7_0` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.4061 | 0.0325 | 0.1399 | 0.1519 | 0.0000 | 0.0165 | 20.8000 | 79.2000 | 0.0000 | NA |
| `c7_35120` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.2606 | 0.0208 | 0.1129 | 0.1519 | 0.0000 | 0.0104 | 11.2000 | 88.8000 | 0.0000 | NA |
| `c7_70240` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.0499 | 0.0040 | 0.0377 | 0.1519 | 0.0000 | 0.0207 | 0.8000 | 99.2000 | 0.0000 | NA |
| `c7_105360` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.2295 | 0.0184 | 0.1145 | 0.1519 | 0.0000 | 0.0121 | 11.2000 | 88.8000 | 0.0000 | NA |
| `c7_140480` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.0633 | 0.0051 | 0.0601 | 0.1519 | 0.0000 | 0.0207 | 1.2000 | 98.8000 | 0.0000 | NA |
| `c7_175600` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.0536 | 0.0043 | 0.0487 | 0.1519 | 0.0000 | 0.0206 | 0.8000 | 99.2000 | 0.0000 | NA |
| `c7_210720` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.2052 | 0.0164 | 0.1086 | 0.1519 | 0.0000 | 0.0114 | 10.0000 | 90.0000 | 0.0000 | NA |
| `c7_245840` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.1811 | 0.0145 | 0.1127 | 0.1519 | 0.0000 | 0.0103 | 6.4000 | 93.6000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
