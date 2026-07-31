# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `1e7bca437ff3757f`
- entries: `2`
- samples: `119`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| analysis/phase2_z0075_iter3_seed0_recovery_rate150_seed0_push_snippets/seed_000/push_000_70c15afbddc5679d.jsonl | 35-124 | 90 | `True` | 0.1891 | 2.3633 | 1.4899 | 0.1463 | 1.0772 | 0.0269 |
| analysis/phase2_z0075_iter3_seed0_recovery_rate150_seed0_push_snippets/seed_000/push_001_52fa7376aaf9cfc5.jsonl | 96-124 | 29 | `True` | 0.4911 | 6.1388 | 1.4924 | 0.1477 | 1.3173 | 0.0269 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
