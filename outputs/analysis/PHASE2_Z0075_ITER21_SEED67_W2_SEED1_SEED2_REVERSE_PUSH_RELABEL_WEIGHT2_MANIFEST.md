# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `0ef9113b7f52e30b`
- entries: `1`
- samples: `84`
- bc_ready_entries: `1`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_z0075_iter21_seed67_w2_seed1_seed2_reverse_push_snippets_relabelled_weight2/analysis/phase2_z0075_iter21_seed67_w2_seed1_seed2_reverse_push_snippets/seed_002/push_003_385805db95510321.jsonl | 197-280 | 84 | `True` | -0.1678 | -2.0970 | 1.4165 | 0.1320 | 0.9900 | 0.1011 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
