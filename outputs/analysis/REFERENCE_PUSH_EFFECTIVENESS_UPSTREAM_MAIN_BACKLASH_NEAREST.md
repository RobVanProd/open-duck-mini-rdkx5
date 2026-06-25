# Reference Push-Effectiveness Comparison

status: `HOLD_REFERENCE_CONTACT_MISMATCH`
trace_count: `24`
usable_trace_count: `24`
lookahead_s: `0.1`

## Aggregate

- best_reference_single_future_vx_delta_m_s: `-0.0051`
- max_reference_single_actual_double_pct: `51.0204`
- qualifying_labels: `[]`
- positive_but_unstable_labels: `[]`
- high_contact_mismatch_labels: `['reference_motion_rollout_upstream_main_backlash_nearest_cycle_projected_traces', 'reference_motion_rollout_upstream_main_backlash_nearest_raw_traces']`

## By Trace Set

| trace_set | traces | contact_mismatch | ref_single_pct | ref_single_dvx | ref_single_vy95 | ref_single_pitch_vel95 | actual_single_pct | matched_single_pct | ref_single_actual_double_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| reference_motion_rollout_upstream_main_backlash_nearest_contact_synchronized_projected_traces | 8 | 20.1366 | 19.9768 | -0.0051 | 0.1696 | 5.2400 | 19.0074 | 9.4434 | 9.8006 |
| reference_motion_rollout_upstream_main_backlash_nearest_cycle_projected_traces | 8 | 72.9500 | 63.2653 | -0.0356 | 0.1713 | 5.2400 | 24.3878 | 3.1122 | 51.0204 |
| reference_motion_rollout_upstream_main_backlash_nearest_raw_traces | 8 | 66.9833 | 63.2653 | -0.0390 | 0.1859 | 5.2400 | 41.0714 | 11.9388 | 37.2449 |

## Interpretation

- This analyzes existing reference rollout traces only; it does not train, deploy, SSH, or touch the robot.
- `reference_single_support` is the reference asking the body to stand on one foot.
- `reference_single_actual_double` is the key mismatch: the reference asks single support while the sim remains in double support.
- A positive 0.1s future-vx delta during reference single support would show that the reference gait's support phase propels the body forward in this sim.
- Near-zero/negative future-vx delta or persistent actual double support means the controller search should stop treating another teacher variant as the next default move.
