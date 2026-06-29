# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
policy_action_gain: `1.0`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
min_swing_segments_per_foot: `None`
min_swing_rel_x_range_p95_m: `None`
min_swing_peak_lift_m: `None`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gated` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0019 | NA | 0.0237 | 0.1519 | 0.4470 | 0.0000 | 0.0787 | 0.0015 | 0 | 0.0000 | 1.2000 | 98.8000 | 0 | NA |
| `gated` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | -0.0009 | NA | 0.0455 | 0.1562 | 0.8180 | 0.0000 | 0.0836 | 0.0045 | 1 | 0.0041 | 4.0000 | 95.6000 | 0 | NA |
| `gated` | 2 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0022 | NA | 0.0375 | 0.1511 | 0.4121 | 0.0000 | 0.0693 | 0.0078 | 1 | 0.0046 | 2.4000 | 97.6000 | 0 | NA |
| `gated` | 3 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | -0.0056 | NA | 0.0590 | 0.1553 | 0.4406 | 0.0000 | 0.0666 | 0.0049 | 0 | 0.0000 | 0.4000 | 99.6000 | 0 | NA |
| `gated` | 4 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0061 | NA | 0.0175 | 0.1506 | 0.8247 | 0.0000 | 0.1008 | 0.0023 | 0 | 0.0000 | 0.8000 | 99.2000 | 0 | NA |
| `gated` | 5 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0110 | NA | 0.0385 | 0.1462 | 0.9804 | 0.0000 | 0.1056 | 0.0198 | 1 | 0.0037 | 1.2000 | 98.0000 | 0 | NA |
| `gated` | 6 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0033 | NA | 0.0170 | 0.1530 | 0.6495 | 0.0000 | 0.0807 | 0.0175 | 1 | 0.0167 | 4.8000 | 95.2000 | 0 | NA |
| `gated` | 7 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0009 | NA | 0.0404 | 0.1564 | 0.5360 | 0.0000 | 0.0689 | 0.0123 | 0 | 0.0000 | 2.4000 | 97.6000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gated` | 8 | 0 | 8 | 250.0000 | 250 | 250 | NA | 0.0024 | 0.0349 | 0.1526 | 0.0000 | 0.0088 | 0.5000 | 0.0036 | 2.1500 | 97.7000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
