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
- action_delta_capped: `{}`

## Traces

| source | dropped | transformed | input samples | output samples | weight clamped | action capped |
|---|---:|---:|---:|---:|---:|---|
| trace.jsonl | False | True | 750 | 750 | 0 | `{}` |

## Gate

- This artifact only prepares labels for a later BC fit.
- It is not a deployable candidate and is not a robot-side change.
