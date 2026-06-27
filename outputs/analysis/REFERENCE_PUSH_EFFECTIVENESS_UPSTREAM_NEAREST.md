# Reference Push-Effectiveness Comparison

status: `HOLD_REFERENCE_CONTACT_MISMATCH`
trace_count: `24`
usable_trace_count: `24`
lookahead_s: `0.1`

## Aggregate

- best_reference_single_future_vx_delta_m_s: `-0.0099`
- max_reference_single_actual_double_pct: `37.9679`
- qualifying_labels: `[]`
- positive_but_unstable_labels: `[]`
- high_contact_mismatch_labels: `['reference_motion_rollout_upstream_nearest_cycle_projected_traces', 'reference_motion_rollout_upstream_nearest_raw_traces']`

## By Trace Set

| trace_set | traces | contact_mismatch | ref_single_pct | ref_single_dvx | ref_single_vy95 | ref_single_pitch_vel95 | actual_single_pct | matched_single_pct | ref_single_actual_double_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| reference_motion_rollout_upstream_nearest_contact_synchronized_projected_traces | 8 | 14.5439 | 38.9878 | -0.0099 | 0.3295 | 5.2400 | 38.1664 | 31.3099 | 5.9628 |
| reference_motion_rollout_upstream_nearest_cycle_projected_traces | 8 | 71.1627 | 62.9800 | -0.0276 | 0.3265 | 5.2400 | 42.2278 | 10.8855 | 37.9679 |
| reference_motion_rollout_upstream_nearest_raw_traces | 8 | 69.5729 | 63.2693 | -0.0512 | 0.3332 | 5.2400 | 50.9455 | 15.8425 | 29.6189 |

## Interpretation

- This analyzes existing reference rollout traces only; it does not train, deploy, SSH, or touch the robot.
- `reference_single_support` is the reference asking the body to stand on one foot.
- `reference_single_actual_double` is the key mismatch: the reference asks single support while the sim remains in double support.
- A positive 0.1s future-vx delta during reference single support would show that the reference gait's support phase propels the body forward in this sim.
- Near-zero/negative future-vx delta or persistent actual double support means the controller search should stop treating another teacher variant as the next default move.
