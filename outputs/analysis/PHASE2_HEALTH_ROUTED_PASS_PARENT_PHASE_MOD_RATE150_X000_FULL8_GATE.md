# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.075`-`0.125`
push_recovery_window_s: `1.2`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `10`
reset_mode: `home-support`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `health_routed_parent` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0008 | NA | 0.0680 | 0.1610 | 0.0342 | 0.0000 | 0.0000 | 0.0420 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 12 | 0.9167 |
| `health_routed_parent` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0010 | NA | 0.0721 | 0.1607 | 0.0345 | 0.0000 | 0.0000 | 0.0430 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `health_routed_parent` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0009 | NA | 0.0690 | 0.1611 | 0.0348 | 0.0000 | 0.0000 | 0.0421 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `health_routed_parent` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0007 | NA | 0.0700 | 0.1609 | 0.0340 | 0.0000 | 0.0000 | 0.0427 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `health_routed_parent` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0007 | NA | 0.0686 | 0.1612 | 0.0336 | 0.0000 | 0.0000 | 0.0418 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 12 | 0.9167 |
| `health_routed_parent` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0007 | NA | 0.0720 | 0.1607 | 0.0343 | 0.0000 | 0.0000 | 0.0438 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `health_routed_parent` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0008 | NA | 0.0746 | 0.1609 | 0.0331 | 0.0000 | 0.0000 | 0.0434 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 13 | 0.9231 |
| `health_routed_parent` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0009 | NA | 0.0695 | 0.1610 | 0.0343 | 0.0000 | 0.0000 | 0.0410 | NA | 0 | 0.0000 | 0.0000 | 100.0000 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `health_routed_parent` | 8 | 0 | 8 | 750.0000 | 750 | 750 | NA | 0.0008 | 0.0705 | 0.1610 | 0.0000 | 0.0000 | NA | 0.0000 | 0.0000 | 0.0000 | 100.0000 | 12.3750 | 0.9186 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
