# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
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
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0075`
reset_settle_ticks: `0`
reset_mode: `home-support`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_mod_rate150` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 181 | `fall_or_nan` | 0.1271 | 1.5887 | 0.7706 | 0.0094 | 1.5939 | 0.0000 | 1.3268 | 0.2007 | 0.0169 | 2 | 0.0145 | 18.7845 | 81.2155 | 2 | 1.0000 |
| `phase_mod_rate150` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0309 | 0.3864 | 0.1878 | 0.1533 | 1.5960 | 0.0000 | 0.0000 | 0.1909 | 0.0156 | 15 | 0.0154 | 22.8000 | 77.2000 | 13 | 1.0000 |
| `phase_mod_rate150` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0303 | 0.3784 | 0.1642 | 0.1533 | 1.5628 | 0.0000 | 0.0000 | 0.1834 | 0.0143 | 12 | 0.0247 | 25.4667 | 74.5333 | 13 | 0.9231 |
| `phase_mod_rate150` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0336 | 0.4195 | 0.1864 | 0.1533 | 1.5565 | 0.0000 | 0.0000 | 0.1859 | 0.0170 | 18 | 0.0178 | 25.7333 | 74.2667 | 13 | 1.0000 |
| `phase_mod_rate150` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0282 | 0.3520 | 0.1655 | 0.1533 | 1.5549 | 0.0000 | 0.0000 | 0.1793 | 0.0146 | 10 | 0.0227 | 22.9333 | 77.0667 | 12 | 1.0000 |
| `phase_mod_rate150` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0238 | 0.2969 | 0.1752 | 0.1533 | 1.5650 | 0.0000 | 0.0000 | 0.1860 | 0.0159 | 13 | 0.0239 | 22.9333 | 77.0667 | 13 | 1.0000 |
| `phase_mod_rate150` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0281 | 0.3515 | 0.1623 | 0.1533 | 1.5704 | 0.0000 | 0.0000 | 0.1821 | 0.0137 | 14 | 0.0193 | 26.1333 | 73.8667 | 13 | 0.9231 |
| `phase_mod_rate150` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 550 | `fall_or_nan` | 0.0580 | 0.7245 | 0.3386 | 0.0201 | 1.5628 | 0.0000 | 0.4477 | 0.1872 | 0.0601 | 11 | 0.0225 | 23.4545 | 76.3636 | 7 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_mod_rate150` | 8 | 2 | 6 | 653.8750 | 181 | 750 | 0.5622 | 0.0450 | 0.2688 | 0.1186 | 0.0000 | 0.2218 | 0.0210 | 11.8750 | 0.0201 | 23.5299 | 76.4474 | 10.7500 | 0.9808 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
