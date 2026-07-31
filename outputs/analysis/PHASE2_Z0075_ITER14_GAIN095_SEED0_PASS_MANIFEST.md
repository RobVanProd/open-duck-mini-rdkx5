# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `dbd9618df8755409`
- entries: `1`
- samples: `750`
- bc_ready_entries: `1`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_z0075_iter13_gain095_seed0_trace/iter13_gain095/seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0210 | 0.2621 | 1.3576 | 0.1319 | 0.1781 | 0.1532 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
