# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `c73772294002073e`
- entries: `2`
- samples: `147`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_z0075_iter21_balanced_postpush_failed_seed_push_snippets_relabelled_weight2/analysis/phase2_z0075_iter21_balanced_postpush_failed_seed_push_snippets/seed_006/push_002_d58ee50a26422599.jsonl | 137-210 | 74 | `True` | 0.2573 | 3.2162 | 1.3828 | 0.1389 | 1.1246 | 0.0144 |
| phase2_z0075_iter21_balanced_postpush_failed_seed_push_snippets_relabelled_weight2/analysis/phase2_z0075_iter21_balanced_postpush_failed_seed_push_snippets/seed_007/push_007_0083b1968111b80b.jsonl | 545-617 | 73 | `True` | 0.2510 | 3.1371 | 1.3790 | 0.1382 | 1.1783 | 0.0170 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
