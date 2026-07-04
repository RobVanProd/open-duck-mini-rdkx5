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
eval_push_magnitude: `0.05`-`0.1`
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
| `phase_mod_rate150` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0264 | 0.3301 | 0.1711 | 0.1533 | 1.5633 | 0.0000 | 0.0000 | 0.1864 | 0.0131 | 10 | 0.0182 | 21.8667 | 78.1333 | 12 | 0.9167 |
| `phase_mod_rate150` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0276 | 0.3450 | 0.1744 | 0.1533 | 1.5563 | 0.0000 | 0.0000 | 0.1861 | 0.0158 | 15 | 0.0158 | 22.8000 | 77.2000 | 13 | 1.0000 |
| `phase_mod_rate150` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0273 | 0.3415 | 0.1726 | 0.1533 | 1.5533 | 0.0000 | 0.0000 | 0.1869 | 0.0139 | 13 | 0.0163 | 24.2667 | 75.7333 | 13 | 0.9231 |
| `phase_mod_rate150` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0297 | 0.3714 | 0.1893 | 0.1533 | 1.5483 | 0.0000 | 0.0000 | 0.1882 | 0.0166 | 14 | 0.0169 | 23.7333 | 76.2667 | 13 | 1.0000 |
| `phase_mod_rate150` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0302 | 0.3773 | 0.1683 | 0.1533 | 1.5574 | 0.0000 | 0.0000 | 0.1859 | 0.0136 | 9 | 0.0266 | 23.0667 | 76.9333 | 12 | 1.0000 |
| `phase_mod_rate150` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0292 | 0.3649 | 0.1999 | 0.1533 | 1.5446 | 0.0000 | 0.0000 | 0.1888 | 0.0167 | 10 | 0.0200 | 22.8000 | 77.2000 | 13 | 1.0000 |
| `phase_mod_rate150` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0295 | 0.3692 | 0.1739 | 0.1533 | 1.5527 | 0.0000 | 0.0000 | 0.1848 | 0.0163 | 15 | 0.0202 | 22.9333 | 77.0667 | 13 | 0.9231 |
| `phase_mod_rate150` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0252 | 0.3152 | 0.1804 | 0.1533 | 1.5757 | 0.0000 | 0.0000 | 0.1891 | 0.0148 | 10 | 0.0229 | 22.0000 | 78.0000 | 10 | 1.0000 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase_mod_rate150` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3518 | 0.0281 | 0.1788 | 0.1533 | 0.0000 | 0.0000 | 0.0151 | 12.0000 | 0.0196 | 22.9333 | 77.0667 | 12.3750 | 0.9704 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
