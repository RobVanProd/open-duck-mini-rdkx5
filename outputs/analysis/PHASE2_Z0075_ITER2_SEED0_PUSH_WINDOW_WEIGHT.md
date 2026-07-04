# Weighted BC Trace Samples

status: `PASS_WEIGHTED_BC_TRACE_SAMPLES_READY`

This offline artifact applies per-row sample weights to BC JSONL traces.
It does not copy traces into git by itself, train, deploy, SSH, run robot
tests, or change runtime behavior.

## Rule

- tick_start: `650`
- tick_end: `687`
- time_start_s: `None`
- time_end_s: `None`
- contact_code: `None`
- min_command_x: `None`
- match_weight: `4.0`
- reason: `seed0_push_window_recovery`

## Traces

| source | samples | matched | contacts | weight reasons |
|---|---:|---:|---|---|
| trace.jsonl | 688 | 38 | `{'00': 1, '01': 71, '10': 124, '11': 492}` | `{'base': 650, 'seed0_push_window_recovery': 38}` |

## Gate

- Output JSONL traces are generated artifacts and should remain ignored
  unless explicitly approved.
- A weighted trace is not a candidate policy.
