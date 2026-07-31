# Reference Push-Effectiveness Comparison

status: `HOLD_REFERENCE_CONTACT_MISMATCH`
trace_count: `24`
usable_trace_count: `24`
lookahead_s: `0.1`

## Aggregate

- best_reference_single_future_vx_delta_m_s: `-0.0182`
- max_reference_single_actual_double_pct: `56.1735`
- qualifying_labels: `[]`
- positive_but_unstable_labels: `[]`
- high_contact_mismatch_labels: `['reference_motion_rollout_contact_probe_backlash_nearest_cycle_projected_traces', 'reference_motion_rollout_contact_probe_backlash_nearest_raw_traces']`

## By Trace Set

| trace_set | traces | contact_mismatch | ref_single_pct | ref_single_dvx | ref_single_vy95 | ref_single_pitch_vel95 | actual_single_pct | matched_single_pct | ref_single_actual_double_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| reference_motion_rollout_contact_probe_backlash_nearest_contact_synchronized_projected_traces | 8 | 4.6415 | 13.0782 | -0.0182 | 0.1751 | 5.2133 | 12.7721 | 10.9694 | 1.9558 |
| reference_motion_rollout_contact_probe_backlash_nearest_cycle_projected_traces | 8 | 66.9500 | 63.2653 | -0.0397 | 0.1346 | 5.2400 | 11.1735 | 1.0204 | 56.1735 |
| reference_motion_rollout_contact_probe_backlash_nearest_raw_traces | 8 | 67.2202 | 63.7039 | -0.0198 | 0.1806 | 5.2400 | 14.6754 | 3.7280 | 55.5008 |

## Interpretation

- This analyzes existing reference rollout traces only; it does not train, deploy, SSH, or touch the robot.
- `reference_single_support` is the reference asking the body to stand on one foot.
- `reference_single_actual_double` is the key mismatch: the reference asks single support while the sim remains in double support.
- A positive 0.1s future-vx delta during reference single support would show that the reference gait's support phase propels the body forward in this sim.
- Near-zero/negative future-vx delta or persistent actual double support means the controller search should stop treating another teacher variant as the next default move.
