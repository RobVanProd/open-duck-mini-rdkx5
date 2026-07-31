# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `6f720e613ad37ece`
- entries: `3`
- samples: `2250`
- bc_ready_entries: `3`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| analysis/phase2_z0075_iter12_iter10_pass_control_traces/iter10_spike_local_rate150/seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0282 | 0.3521 | 1.4242 | 0.1389 | 0.1695 | 0.1527 |
| analysis/phase2_z0075_iter12_iter10_pass_control_traces/iter10_spike_local_rate150/seed_004/trace.jsonl | 0-749 | 750 | `True` | 0.0298 | 0.3726 | 1.4291 | 0.1391 | 0.1998 | 0.1511 |
| analysis/phase2_z0075_iter12_iter10_pass_control_traces/iter10_spike_local_rate150/seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0254 | 0.3174 | 1.4210 | 0.1377 | 0.1745 | 0.1567 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
