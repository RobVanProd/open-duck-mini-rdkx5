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
- reason: `iter2_seed7_pass_control`

## Traces

| source | samples | matched | contacts | weight reasons |
|---|---:|---:|---|---|
| trace.jsonl | 750 | 750 | `{'01': 78, '10': 122, '11': 550}` | `{'iter2_seed7_pass_control': 750}` |

## Gate

- Output JSONL traces are generated artifacts and should remain ignored
  unless explicitly approved.
- A weighted trace is not a candidate policy.
