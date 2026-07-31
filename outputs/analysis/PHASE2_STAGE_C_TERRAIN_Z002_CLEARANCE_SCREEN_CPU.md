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
| `a2_gain099` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0285 | 0.3560 | 0.1307 | 0.1519 | 1.7640 | 0.0000 | 0.2079 | 0.0153 | 17.6000 | 82.4000 | 0 | NA |
| `c0_245760` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0301 | 0.3758 | 0.1391 | 0.1519 | 1.8078 | 0.0000 | 0.2040 | 0.0159 | 16.8000 | 83.2000 | 0 | NA |
| `c2_163840` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0309 | 0.3866 | 0.1357 | 0.1519 | 1.8222 | 0.0000 | 0.2044 | 0.0163 | 17.2000 | 82.8000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `a2_gain099` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.3560 | 0.0285 | 0.1307 | 0.1519 | 0.0000 | 0.0153 | 17.6000 | 82.4000 | 0.0000 | NA |
| `c0_245760` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.3758 | 0.0301 | 0.1391 | 0.1519 | 0.0000 | 0.0159 | 16.8000 | 83.2000 | 0.0000 | NA |
| `c2_163840` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.3866 | 0.0309 | 0.1357 | 0.1519 | 0.0000 | 0.0163 | 17.2000 | 82.8000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
