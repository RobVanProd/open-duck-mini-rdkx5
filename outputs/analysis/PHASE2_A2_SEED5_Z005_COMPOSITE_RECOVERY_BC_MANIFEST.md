# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `474aed4e249e54b2`
- entries: `2`
- samples: `141`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| analysis/phase2_a2_seed5_z002_x000_2s_fullobs_trace.jsonl | 0-99 | 100 | `True` | 0.0271 | NA | 0.7159 | 0.0804 | 0.1945 | 0.1462 |
| analysis/phase2_a2_seed5_z005_recovery_from_z002_relabel_trace.jsonl | 20-60 | 41 | `True` | -0.4044 | NA | 0.7768 | 0.0718 | 1.4070 | 0.0512 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
