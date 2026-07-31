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
seeds: `[0, 1, 2, 6, 7]`
eval_push_enable: `True`
eval_push_interval_s: `1.0`-`1.5`
eval_push_magnitude: `0.075`-`0.125`
push_recovery_window_s: `0.5`
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
| `ppo_loc_iter2_step0` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0259 | 0.3240 | 0.2226 | 0.1572 | 1.5870 | 0.0000 | 0.0000 | 0.1871 | 0.0188 | 10 | 0.0218 | 19.8667 | 80.1333 | 12 | 0.9167 |
| `ppo_loc_iter2_step0` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 164 | `fall_or_nan` | 0.1334 | 1.6672 | 0.8829 | -0.0022 | 1.6335 | 0.0000 | 0.0000 | 0.1969 | 0.0622 | 2 | 0.0160 | 11.5854 | 86.5854 | 2 | 1.0000 |
| `ppo_loc_iter2_step0` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0229 | 0.2861 | 0.1829 | 0.1583 | 1.5989 | 0.0000 | 0.0000 | 0.1898 | 0.0171 | 9 | 0.0263 | 19.6000 | 80.4000 | 13 | 0.9231 |
| `ppo_loc_iter2_step0` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0221 | 0.2764 | 0.1809 | 0.1575 | 1.5954 | 0.0000 | 0.0000 | 0.1849 | 0.0139 | 7 | 0.0148 | 18.6667 | 81.3333 | 13 | 0.9231 |
| `ppo_loc_iter2_step0` | 7 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0260 | 0.3247 | 0.2054 | 0.1583 | 1.6041 | 0.0000 | 0.2652 | 0.1882 | 0.0134 | 11 | 0.0253 | 23.0667 | 76.9333 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ppo_loc_iter2_step0` | 5 | 1 | 4 | 632.8000 | 164 | 750 | 0.5757 | 0.0461 | 0.3349 | 0.1258 | 0.0000 | 0.0530 | 0.0251 | 7.8000 | 0.0209 | 18.5571 | 81.0771 | 10.0000 | 0.9526 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
