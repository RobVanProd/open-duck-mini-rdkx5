# Curated BC Trace Records

status: `PASS_CURATED_BC_TRACE_RECORDS_READY`

This is an offline generated trace-curation artifact. It does not train,
deploy, SSH, run robot tests, or change runtime behavior.

## Settings

- drop_source_regex: `/seed_004/`
- transform_source_regex: `/seed_005/`
- joints: `right_ankle`
- max_target_velocity_rad_s: `2.25`
- max_matched_weight: `0.25`
- match_sample_weight_reason_regex: `reverse_velocity|double_support_low_progress`
- match_contact_code: `None`
- match_tick_min: `None`
- match_tick_max: `None`
- match_local_vx_max: `0.0`
- match_body_pitch_abs_min: `0.5`
- match_base_height_max: `0.14`
- match_any: `True`

## Summary

- input_traces: `8`
- output_traces: `7`
- dropped_traces: `1`
- transformed_traces: `1`
- weight_clamped_rows: `219`
- action_delta_capped: `{'13': 4}`

## Traces

| source | dropped | transformed | samples | weight clamped | action capped |
|---|---:|---:|---:|---:|---|
| trace.jsonl | False | False | 250 | 0 | `{}` |
| trace.jsonl | False | False | 250 | 0 | `{}` |
| trace.jsonl | False | False | 250 | 0 | `{}` |
| trace.jsonl | False | False | 250 | 0 | `{}` |
| trace.jsonl | True | None | 0 | 0 | `{}` |
| trace.jsonl | False | True | 250 | 219 | `{'13': 4}` |
| trace.jsonl | False | False | 250 | 0 | `{}` |
| trace.jsonl | False | False | 250 | 0 | `{}` |

## Gate

- This artifact only prepares labels for a later BC fit.
- It is not a deployable candidate and is not a robot-side change.
