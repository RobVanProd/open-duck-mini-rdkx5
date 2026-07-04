# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `e53596b35a38e009`
- entries: `1`
- samples: `20`
- bc_ready_entries: `1`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_z0075_iter4_seed0_antilunge_zero50_tail_weighted/phase2_z0075_control_preserving_recovery_rate150_seed0_trace/iter4_control_preserving_rate150/seed_000/trace.jsonl | 121-140 | 20 | `True` | 0.6641 | 8.3006 | 1.3104 | 0.1415 | 1.3080 | 0.0233 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
