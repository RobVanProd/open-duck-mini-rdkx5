# Curated BC Trace Records

status: `PASS_CURATED_BC_TRACE_RECORDS_READY`

This is an offline generated trace-curation artifact. It does not train,
deploy, SSH, run robot tests, or change runtime behavior.

## Settings

- drop_source_regex: `None`
- transform_source_regex: `None`
- keep_tick_min: `None`
- keep_tick_max: `None`
- joints: ``
- max_target_velocity_rad_s: `None`
- per_joint_max_target_velocity_rad_s: `left_hip_pitch:2.5,left_knee:3.25,left_ankle:2.75,right_hip_pitch:2.25,right_knee:2.75,right_ankle:2.0`
- max_matched_weight: `None`
- match_sample_weight_reason_regex: `None`
- match_contact_code: `None`
- match_tick_min: `None`
- match_tick_max: `None`
- match_local_vx_max: `None`
- match_body_pitch_abs_min: `None`
- match_base_height_max: `None`
- match_any: `True`

## Summary

- input_traces: `3`
- output_traces: `3`
- dropped_traces: `0`
- transformed_traces: `3`
- weight_clamped_rows: `0`
- action_delta_capped: `{'11': 19, '12': 14, '13': 40, '2': 17, '3': 6, '4': 17}`

## Traces

| source | dropped | transformed | input samples | output samples | weight clamped | action capped |
|---|---:|---:|---:|---:|---:|---|
| trace.jsonl | False | True | 750 | 750 | 0 | `{}` |
| trace.jsonl | False | True | 750 | 750 | 0 | `{'11': 11, '12': 6, '13': 25, '2': 9, '3': 5, '4': 12}` |
| trace.jsonl | False | True | 501 | 501 | 0 | `{'11': 8, '12': 8, '13': 15, '2': 8, '3': 1, '4': 5}` |

## Gate

- This artifact only prepares labels for a later BC fit.
- It is not a deployable candidate and is not a robot-side change.
