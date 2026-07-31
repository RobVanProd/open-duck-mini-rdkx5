# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `3cefa83061fe10a1`
- entries: `1`
- samples: `79`
- bc_ready_entries: `1`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_z0075_iter21_seed5_late_push_recovery_snippets_relabelled/analysis/phase2_z0075_iter21_seed5_late_push_recovery_snippets/seed_005/push_009_200a8ce383346549.jsonl | 519-597 | 79 | `True` | -0.2016 | -2.5196 | 1.3650 | 0.1245 | 1.0836 | 0.0873 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
