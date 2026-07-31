# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `710f49343186daf4`
- entries: `6`
- samples: `2112`
- bc_ready_entries: `6`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_001/trace.jsonl | 0-492 | 493 | `True` | -0.0058 | -0.0726 | 1.4270 | 0.1406 | 0.2827 | 0.1047 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_002/trace.jsonl | 0-155 | 156 | `True` | 0.1269 | 1.5861 | 1.4552 | 0.1442 | 0.7764 | 0.0245 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_003/trace.jsonl | 0-448 | 449 | `True` | -0.0186 | -0.2329 | 1.4263 | 0.1377 | 0.2721 | 0.0996 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_004/trace.jsonl | 0-722 | 723 | `True` | 0.0518 | 0.6475 | 1.4326 | 0.1404 | 0.2414 | 0.0246 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_005/trace.jsonl | 0-45 | 46 | `True` | -0.2873 | -3.5913 | 1.4343 | 0.1333 | 1.2367 | 0.0928 |
| phase2_z0075_weight2_control_rate150_failed_seed_traces/iter6_weight2_control_rate150/seed_006/trace.jsonl | 0-244 | 245 | `True` | -0.0458 | -0.5729 | 1.3961 | 0.1334 | 0.5608 | 0.0923 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
