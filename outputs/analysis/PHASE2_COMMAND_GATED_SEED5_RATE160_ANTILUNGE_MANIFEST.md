# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `aa55227d46236696`
- entries: `1`
- samples: `24`
- bc_ready_entries: `1`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| analysis/phase2_command_gated_seed5_rate160_antilunge_relabel/seed_005/trace.jsonl | 80-157 | 24 | `True` | 0.3357 | 4.1966 | 1.5479 | 0.1464 | 1.3837 | -0.0058 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
