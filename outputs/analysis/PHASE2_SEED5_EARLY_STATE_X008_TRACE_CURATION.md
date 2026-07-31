# Curated BC Trace Records

status: `PASS_CURATED_BC_TRACE_RECORDS_READY`

This is an offline generated trace-curation artifact. It does not train,
deploy, SSH, run robot tests, or change runtime behavior.

## Settings

- drop_source_regex: `None`
- transform_source_regex: `None`
- keep_tick_min: `None`
- keep_tick_max: `24`
- joints: `left_hip_pitch,left_knee,left_ankle,right_hip_pitch,right_knee,right_ankle`
- max_target_velocity_rad_s: `2.25`
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

- input_traces: `1`
- output_traces: `1`
- dropped_traces: `0`
- transformed_traces: `1`
- weight_clamped_rows: `0`
- action_delta_capped: `{'12': 1, '13': 2, '2': 2, '4': 2}`

## Traces

| source | dropped | transformed | input samples | output samples | weight clamped | action capped |
|---|---:|---:|---:|---:|---:|---|
| trace.jsonl | False | True | 55 | 25 | 0 | `{'12': 1, '13': 2, '2': 2, '4': 2}` |

## Gate

- This artifact only prepares labels for a later BC fit.
- It is not a deployable candidate and is not a robot-side change.
