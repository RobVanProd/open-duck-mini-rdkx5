# Weighted BC Trace Samples

status: `PASS_WEIGHTED_BC_TRACE_SAMPLES_READY`

This offline artifact applies per-row sample weights to BC JSONL traces.
It does not copy traces into git by itself, train, deploy, SSH, run robot
tests, or change runtime behavior.

## Rule

- contact_code: `10`
- min_command_x: `0.05`
- match_weight: `6.0`
- reason: `seed4_right_swing_contact10`

## Traces

| source | samples | matched | contacts | weight reasons |
|---|---:|---:|---|---|
| trace.jsonl | 250 | 18 | `{'01': 35, '10': 18, '11': 197}` | `{'base': 232, 'seed4_right_swing_contact10': 18}` |

## Gate

- Output JSONL traces are generated artifacts and should remain ignored
  unless explicitly approved.
- A weighted trace is not a candidate policy.
