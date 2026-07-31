# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `9d84d49a6b74b7f9`
- entries: `1`
- samples: `688`
- bc_ready_entries: `1`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_z0075_iter2_seed0_push_window_weighted/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_rate150_seed0_trace/iter2_recovery_rate150/seed_000/trace.jsonl | 0-687 | 688 | `True` | 0.0562 | 0.7024 | 1.4475 | 0.1420 | 0.2744 | 0.0402 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
