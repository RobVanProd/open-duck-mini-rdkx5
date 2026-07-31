# Reference Push-Effectiveness Comparison

status: `HOLD_REFERENCE_CONTACT_MISMATCH`
trace_count: `24`
usable_trace_count: `24`
lookahead_s: `0.1`

## Aggregate

- best_reference_single_future_vx_delta_m_s: `-0.0158`
- max_reference_single_actual_double_pct: `42.3162`
- qualifying_labels: `[]`
- positive_but_unstable_labels: `[]`
- high_contact_mismatch_labels: `['reference_motion_rollout_upstream_main_nearest_cycle_projected_traces', 'reference_motion_rollout_upstream_main_nearest_raw_traces']`

## By Trace Set

| trace_set | traces | contact_mismatch | ref_single_pct | ref_single_dvx | ref_single_vy95 | ref_single_pitch_vel95 | actual_single_pct | matched_single_pct | ref_single_actual_double_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| reference_motion_rollout_upstream_main_nearest_contact_synchronized_projected_traces | 8 | 14.6741 | 32.3618 | -0.0158 | 0.3192 | 5.2400 | 32.5504 | 25.5251 | 6.2755 |
| reference_motion_rollout_upstream_main_nearest_cycle_projected_traces | 8 | 71.4134 | 63.9720 | -0.0312 | 0.3084 | 5.2400 | 37.5818 | 8.5902 | 42.3162 |
| reference_motion_rollout_upstream_main_nearest_raw_traces | 8 | 70.9015 | 64.1328 | -0.0527 | 0.3219 | 5.2400 | 49.0813 | 13.4956 | 32.1464 |

## Interpretation

- This analyzes existing reference rollout traces only; it does not train, deploy, SSH, or touch the robot.
- `reference_single_support` is the reference asking the body to stand on one foot.
- `reference_single_actual_double` is the key mismatch: the reference asks single support while the sim remains in double support.
- A positive 0.1s future-vx delta during reference single support would show that the reference gait's support phase propels the body forward in this sim.
- Near-zero/negative future-vx delta or persistent actual double support means the controller search should stop treating another teacher variant as the next default move.
