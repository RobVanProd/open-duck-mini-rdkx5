# Weighted BC Trace Samples

status: `PASS_WEIGHTED_BC_TRACE_SAMPLES_READY`

This offline artifact applies per-row sample weights to BC JSONL traces.
It does not copy traces into git by itself, train, deploy, SSH, run robot
tests, or change runtime behavior.

## Rule

- tick_start: `None`
- tick_end: `None`
- time_start_s: `None`
- time_end_s: `None`
- contact_code: `None`
- min_command_x: `0.08`
- match_weight: `5.0`
- reason: `seed0_antilunge_zero50_tail`

## Traces

| source | samples | matched | contacts | weight reasons |
|---|---:|---:|---|---|
| trace.jsonl | 20 | 20 | `{'00': 2, '01': 2, '10': 5, '11': 11}` | `{'seed0_antilunge_zero50_tail': 20}` |

## Gate

- Output JSONL traces are generated artifacts and should remain ignored
  unless explicitly approved.
- A weighted trace is not a candidate policy.
