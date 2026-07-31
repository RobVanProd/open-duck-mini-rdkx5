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
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.0025`
min_swing_segments_per_foot: `1`
min_swing_rel_x_range_p95_m: `0.003`
min_swing_peak_lift_m: `0.005`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `z0025_contactphase_rate1p9` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0289 | 0.3616 | 0.1180 | 0.1519 | 1.9118 | 0.0000 | 0.0000 | 0.1945 | 0.0120 | 14 | 0.0139 | 21.8667 | 78.1333 | 0 | NA |
| `z0025_contactphase_rate1p9` | 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0322 | 0.4028 | 0.1213 | 0.1563 | 1.9202 | 0.0000 | 0.0000 | 0.1935 | 0.0132 | 11 | 0.0137 | 23.6000 | 76.2667 | 0 | NA |
| `z0025_contactphase_rate1p9` | 2 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0316 | 0.3949 | 0.1151 | 0.1512 | 1.9234 | 0.0000 | 0.0000 | 0.1953 | 0.0114 | 10 | 0.0150 | 22.4000 | 77.6000 | 0 | NA |
| `z0025_contactphase_rate1p9` | 3 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0255 | 0.3184 | 0.1177 | 0.1547 | 1.9116 | 0.0000 | 0.0000 | 0.1945 | 0.0121 | 9 | 0.0186 | 18.5333 | 81.4667 | 0 | NA |
| `z0025_contactphase_rate1p9` | 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0318 | 0.3971 | 0.1120 | 0.1506 | 1.9211 | 0.0000 | 0.0000 | 0.1923 | 0.0117 | 12 | 0.0068 | 21.3333 | 78.6667 | 0 | NA |
| `z0025_contactphase_rate1p9` | 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0298 | 0.3721 | 0.1173 | 0.1464 | 1.9118 | 0.0000 | 0.0000 | 0.1940 | 0.0184 | 13 | 0.0059 | 19.3333 | 80.4000 | 0 | NA |
| `z0025_contactphase_rate1p9` | 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0312 | 0.3903 | 0.1130 | 0.1531 | 1.9065 | 0.0000 | 0.0000 | 0.1917 | 0.0181 | 17 | 0.0050 | 24.2667 | 75.7333 | 0 | NA |
| `z0025_contactphase_rate1p9` | 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0285 | 0.3562 | 0.1082 | 0.1564 | 1.9220 | 0.0000 | 0.0000 | 0.1941 | 0.0114 | 7 | 0.0146 | 19.6000 | 80.4000 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `z0025_contactphase_rate1p9` | 8 | 0 | 8 | 750.0000 | 750 | 750 | 0.3742 | 0.0299 | 0.1153 | 0.1526 | 0.0000 | 0.0000 | 0.0135 | 11.6250 | 0.0117 | 21.3667 | 78.5833 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
