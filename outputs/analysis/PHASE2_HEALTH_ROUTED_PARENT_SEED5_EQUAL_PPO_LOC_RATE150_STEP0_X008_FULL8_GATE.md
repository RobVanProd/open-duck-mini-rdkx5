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
| `ppo_step0_seed5_equal` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0275 | 0.3437 | 0.1692 | 0.1590 | 1.5158 | 0.0000 | 0.0000 | 0.1857 | 0.0165 | 13 | 0.0228 | 23.4667 | 76.5333 | 12 | 0.9167 |
| `ppo_step0_seed5_equal` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0258 | 0.3221 | 0.1905 | 0.1581 | 1.5183 | 0.0000 | 0.0000 | 0.1899 | 0.0163 | 14 | 0.0198 | 23.4667 | 76.5333 | 13 | 0.9231 |
| `ppo_step0_seed5_equal` | 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 293 | `fall_or_nan` | -0.0398 | -0.4979 | 0.1808 | 0.0763 | 1.5011 | 0.0000 | 0.0000 | 0.1815 | 0.0344 | 7 | 0.0173 | 17.4061 | 81.5700 | 5 | 0.6000 |
| `ppo_step0_seed5_equal` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0303 | 0.3790 | 0.1669 | 0.1582 | 1.5126 | 0.0000 | 0.0000 | 0.1865 | 0.0166 | 19 | 0.0200 | 25.8667 | 74.1333 | 13 | 0.9231 |
| `ppo_step0_seed5_equal` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0258 | 0.3225 | 0.1724 | 0.1590 | 1.5153 | 0.0000 | 0.0000 | 0.1850 | 0.0156 | 10 | 0.0206 | 24.4000 | 75.6000 | 12 | 0.9167 |
| `ppo_step0_seed5_equal` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0259 | 0.3241 | 0.1809 | 0.1586 | 1.5115 | 0.0000 | 0.0000 | 0.1848 | 0.0129 | 12 | 0.0253 | 22.4000 | 77.6000 | 13 | 0.9231 |
| `ppo_step0_seed5_equal` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0225 | 0.2813 | 0.1790 | 0.1578 | 1.5084 | 0.0000 | 0.0000 | 0.1845 | 0.0138 | 12 | 0.0206 | 22.0000 | 78.0000 | 13 | 0.9231 |
| `ppo_step0_seed5_equal` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0270 | 0.3381 | 0.1947 | 0.1590 | 1.5119 | 0.0000 | 0.0000 | 0.1928 | 0.0164 | 12 | 0.0191 | 24.0000 | 76.0000 | 10 | 0.9000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_step0_seed5_equal` | 8 | 1 | 7 | 692.8750 | 293 | 750 | 0.2266 | 0.0181 | 0.1793 | 0.1483 | 0.0000 | 0.0000 | 0.0178 | 12.3750 | 0.0207 | 22.8758 | 76.9962 | 11.3750 | 0.8782 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
