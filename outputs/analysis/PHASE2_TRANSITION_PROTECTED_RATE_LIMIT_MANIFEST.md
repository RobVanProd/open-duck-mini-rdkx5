# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `449b65b14d3dd651`
- entries: `2`
- samples: `500`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_transition_protected_rate_limit_traces/rollouts_x008/student/seed_002/trace.jsonl | 0-249 | 250 | `True` | 0.0397 | 0.4968 | 2.1964 | 0.1703 | 0.0968 | 0.1511 |
| phase2_transition_protected_rate_limit_traces/rollouts_x008/student/seed_004/trace.jsonl | 0-249 | 250 | `True` | 0.0459 | 0.5737 | 2.0583 | 0.1665 | 0.1173 | 0.1507 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
