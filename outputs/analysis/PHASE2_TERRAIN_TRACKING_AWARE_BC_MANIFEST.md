# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `7838c25a5b605626`
- entries: `7`
- samples: `1150`
- bc_ready_entries: `7`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| rollouts_x0/student/seed_000/trace.jsonl | 0-249 | 250 | `True` | -0.0010 | -0.0125 | 0.2511 | 0.0365 | 0.0457 | 0.1519 |
| phase2_terrain_safe_hard_step_slices/z0p001/seed_002/trace.jsonl | 80-179 | 100 | `True` | 0.0560 | 0.7006 | 2.1892 | 0.1764 | 0.0875 | 0.1598 |
| phase2_terrain_safe_hard_step_slices/z0p001/seed_004/trace.jsonl | 90-189 | 100 | `True` | 0.0493 | 0.6158 | 1.9976 | 0.1714 | 0.1022 | 0.1602 |
| phase2_terrain_safe_hard_step_slices/z0p002/seed_002/trace.jsonl | 60-159 | 100 | `True` | 0.0558 | 0.6975 | 2.0902 | 0.1788 | 0.0892 | 0.1606 |
| phase2_terrain_safe_hard_step_slices/z0p002/seed_004/trace.jsonl | 140-239 | 100 | `True` | 0.0532 | 0.6648 | 2.2194 | 0.1704 | 0.0911 | 0.1612 |
| phase2_terrain_tracking_aware_labels/rate_limited_x008/seed_002/trace.jsonl | 0-249 | 250 | `True` | 0.0397 | 0.4968 | 2.1964 | 0.1703 | 0.0968 | 0.1511 |
| phase2_terrain_tracking_aware_labels/rate_limited_x008/seed_004/trace.jsonl | 0-249 | 250 | `True` | 0.0459 | 0.5737 | 2.0583 | 0.1665 | 0.1173 | 0.1507 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
