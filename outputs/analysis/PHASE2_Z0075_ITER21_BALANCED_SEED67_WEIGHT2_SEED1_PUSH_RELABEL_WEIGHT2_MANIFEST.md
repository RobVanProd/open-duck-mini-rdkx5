# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `46b125451f05ae12`
- entries: `1`
- samples: `44`
- bc_ready_entries: `1`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_z0075_iter21_balanced_seed67_weight2_seed1_push_snippets_relabelled_weight2/analysis/phase2_z0075_iter21_balanced_seed67_weight2_seed1_push_snippets/seed_001/push_007_fba4e22442dd5a9c.jsonl | 409-452 | 44 | `True` | 0.3318 | 4.1469 | 1.3296 | 0.1359 | 1.2409 | 0.0382 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
