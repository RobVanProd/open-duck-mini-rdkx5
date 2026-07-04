# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `16bc074d3ff4c30c`
- entries: `4`
- samples: `175`
- bc_ready_entries: `4`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_000/push_000_6e6c2d394c022b4d.jsonl | 52-112 | 61 | `True` | 0.2680 | 3.3496 | 1.3566 | 0.1356 | 1.1226 | 0.0292 |
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_002/push_009_e969257189933035.jsonl | 561-602 | 42 | `True` | -0.3378 | -4.2226 | 1.4119 | 0.1278 | 1.1762 | 0.1021 |
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_006/push_010_712c01db7c0c749d.jsonl | 607-670 | 64 | `True` | -0.2441 | -3.0509 | 1.4153 | 0.1350 | 1.0869 | 0.0961 |
| phase2_z0075_home_support_push_window_relabel/phase2_z0075_home_support_push_window_snippets/seed_006/push_011_420a187c0ff36573.jsonl | 663-670 | 8 | `True` | -1.0104 | -12.6294 | 1.2869 | 0.1253 | 1.3573 | 0.0961 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
