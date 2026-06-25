# Reference Push-Effectiveness Comparison

status: `HOLD_REFERENCE_PROPULSION_UNSTABLE`
trace_count: `32`
usable_trace_count: `32`
lookahead_s: `0.1`

## Aggregate

- best_reference_single_future_vx_delta_m_s: `0.0161`
- max_reference_single_actual_double_pct: `44.0437`
- qualifying_labels: `[]`
- positive_but_unstable_labels: `['reference_motion_rollout_v20_contact_gated_projected_traces']`
- high_contact_mismatch_labels: `['reference_motion_rollout_v20_contact_gated_projected_traces', 'reference_motion_rollout_v20_projected_traces', 'reference_motion_rollout_v20_traces']`

## By Trace Set

| trace_set | traces | contact_mismatch | ref_single_pct | ref_single_dvx | ref_single_vy95 | ref_single_pitch_vel95 | actual_single_pct | matched_single_pct | ref_single_actual_double_pct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| reference_motion_rollout_v20_contact_gated_projected_traces | 8 | 69.4217 | 62.0365 | 0.0161 | 0.2688 | 5.1133 | 29.2461 | 7.2853 | 44.0437 |
| reference_motion_rollout_v20_contact_synchronized_projected_traces | 8 | 7.7531 | 31.0938 | -0.0170 | 0.3181 | 5.2033 | 29.4108 | 27.2833 | 1.5931 |
| reference_motion_rollout_v20_projected_traces | 8 | 68.8478 | 63.5537 | -0.0258 | 0.3115 | 5.2400 | 34.6089 | 9.2133 | 40.8770 |
| reference_motion_rollout_v20_traces | 8 | 69.4964 | 63.4650 | -0.0174 | 0.3158 | 5.2400 | 35.4222 | 9.9714 | 40.5030 |

## Interpretation

- This analyzes existing reference rollout traces only; it does not train, deploy, SSH, or touch the robot.
- `reference_single_support` is the reference asking the body to stand on one foot.
- `reference_single_actual_double` is the key mismatch: the reference asks single support while the sim remains in double support.
- A positive 0.1s future-vx delta during reference single support would show that the reference gait's support phase propels the body forward in this sim.
- Near-zero/negative future-vx delta or persistent actual double support means the controller search should stop treating another teacher variant as the next default move.
