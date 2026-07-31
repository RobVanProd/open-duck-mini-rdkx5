# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `53343f2de7eca0e6`
- entries: `5`
- samples: `400`
- bc_ready_entries: `5`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| lunge_neighbor_relabel/iter7_seed_diverse_recovery_rate150/seed_001/trace.jsonl | 432-511 | 80 | `True` | 0.2169 | 2.7108 | 1.4290 | 0.1461 | 1.0841 | 0.0327 |
| lunge_neighbor_relabel/iter7_seed_diverse_recovery_rate150/seed_002/trace.jsonl | 74-153 | 80 | `True` | 0.2207 | 2.7582 | 1.4137 | 0.1436 | 1.0679 | 0.0254 |
| lunge_neighbor_relabel/iter7_seed_diverse_recovery_rate150/seed_004/trace.jsonl | 341-420 | 80 | `True` | 0.2205 | 2.7562 | 1.3999 | 0.1421 | 1.0793 | 0.0359 |
| lunge_neighbor_relabel/iter7_seed_diverse_recovery_rate150/seed_006/trace.jsonl | 349-428 | 80 | `True` | 0.2282 | 2.8531 | 1.3493 | 0.1402 | 1.1163 | 0.0208 |
| lunge_neighbor_relabel/iter7_seed_diverse_recovery_rate150/seed_007/trace.jsonl | 536-615 | 80 | `True` | 0.2230 | 2.7875 | 1.4134 | 0.1404 | 1.0575 | 0.0295 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
