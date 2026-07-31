# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `3639bb388e6f5b44`
- entries: `7`
- samples: `559`
- bc_ready_entries: `7`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_z0075_iter10_spike_local_recovery/seed_000/trace.jsonl | 70-149 | 80 | `True` | 0.2416 | 3.0202 | 1.3367 | 0.1365 | 1.1367 | 0.0025 |
| phase2_z0075_iter10_spike_local_recovery/seed_001/trace.jsonl | 500-579 | 80 | `True` | 0.2220 | 2.7749 | 1.3734 | 0.1295 | 1.1355 | 0.0124 |
| phase2_z0075_iter10_spike_local_recovery/seed_002/trace.jsonl | 74-153 | 80 | `True` | 0.2279 | 2.8481 | 1.3251 | 0.1343 | 1.0973 | 0.0185 |
| phase2_z0075_iter10_spike_local_recovery/seed_003/trace.jsonl | 0-749 | 96 | `True` | 0.0242 | 0.3027 | 1.4166 | 0.1350 | 0.1695 | 0.1558 |
| phase2_z0075_iter10_spike_local_recovery/seed_004/trace.jsonl | 197-276 | 80 | `True` | 0.2522 | 3.1527 | 1.2913 | 0.1233 | 1.1600 | -0.0053 |
| phase2_z0075_iter10_spike_local_recovery/seed_005/trace.jsonl | 0-45 | 46 | `True` | -0.3199 | -3.9985 | 1.4587 | 0.1397 | 1.3732 | 0.0695 |
| phase2_z0075_iter10_spike_local_recovery/seed_006/trace.jsonl | 4-424 | 97 | `True` | 0.1981 | 2.4767 | 1.3699 | 0.1218 | 1.0792 | -0.0021 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
