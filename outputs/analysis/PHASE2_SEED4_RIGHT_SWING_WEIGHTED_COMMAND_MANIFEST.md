# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `b86c263a03fa826f`
- entries: `3`
- samples: `750`
- bc_ready_entries: `3`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_seed4_right_swing_weighted_traces/phase2_transition_action_space_compare_seed4/transition_protected_seed4w/seed_004/trace.jsonl | 0-249 | 250 | `True` | 0.0335 | 0.4184 | 1.9720 | 0.1682 | 0.1007 | 0.1506 |
| phase2_seed4_weighted_right_knee_limited_traces/phase2_transition_action_space_compare_seed2/transition_protected_seed4w/seed_002/trace.jsonl | 0-249 | 250 | `True` | 0.0409 | 0.5112 | 1.9524 | 0.1662 | 0.1007 | 0.1511 |
| relabel_x0/rollouts_x0/student/seed_000/trace.jsonl | 0-249 | 250 | `True` | -0.0010 | -0.0125 | 0.2511 | 0.0365 | 0.0457 | 0.1519 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
