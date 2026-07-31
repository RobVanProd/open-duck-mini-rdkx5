# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `0ded32d984e81201`
- entries: `5`
- samples: `2132`
- bc_ready_entries: `5`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| lunge_neighbor_relabel/iter7_seed_diverse_recovery_rate150/seed_001/trace.jsonl | 0-511 | 512 | `True` | 0.0624 | 0.7795 | 1.4232 | 0.1406 | 0.2960 | 0.0327 |
| lunge_neighbor_relabel/iter7_seed_diverse_recovery_rate150/seed_002/trace.jsonl | 0-153 | 154 | `True` | 0.1278 | 1.5977 | 1.3959 | 0.1369 | 0.7813 | 0.0254 |
| lunge_neighbor_relabel/iter7_seed_diverse_recovery_rate150/seed_004/trace.jsonl | 0-420 | 421 | `True` | 0.0588 | 0.7346 | 1.4319 | 0.1377 | 0.3808 | 0.0359 |
| lunge_neighbor_relabel/iter7_seed_diverse_recovery_rate150/seed_006/trace.jsonl | 0-428 | 429 | `True` | 0.0654 | 0.8177 | 1.4173 | 0.1404 | 0.3708 | 0.0208 |
| lunge_neighbor_relabel/iter7_seed_diverse_recovery_rate150/seed_007/trace.jsonl | 0-615 | 616 | `True` | 0.0517 | 0.6465 | 1.4223 | 0.1403 | 0.2509 | 0.0295 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
