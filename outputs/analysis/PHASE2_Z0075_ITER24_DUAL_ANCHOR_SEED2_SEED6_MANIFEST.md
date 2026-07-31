# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `6efaaf96baee2fe4`
- entries: `2`
- samples: `1500`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| iter_024_history_context_resetsettle10_seed2_active/rollouts_x008/student/seed_006/trace.jsonl | 0-749 | 750 | `True` | 0.0265 | 0.3311 | 1.4321 | 0.1392 | 0.1714 | 0.1577 |
| analysis/phase2_z0075_iter24_live_oracle_seed2_active_history_context_rate150_trace_seed2_6/iter24/seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0262 | 0.3278 | 1.4432 | 0.1397 | 0.1822 | 0.1590 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
