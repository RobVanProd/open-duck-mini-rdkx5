# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `6fbfa42d10a44229`
- entries: `2`
- samples: `462`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_z0075_iter11_reverse_oracle_relabel/phase2_z0075_spike_local_rate150_failed_seed_traces/iter10_spike_local_rate150/seed_001/trace.jsonl | 0-417 | 418 | `True` | -0.0078 | -0.0973 | 1.4230 | 0.1388 | 0.2813 | 0.1046 |
| phase2_z0075_iter11_reverse_oracle_relabel/phase2_z0075_spike_local_rate150_failed_seed_traces/iter10_spike_local_rate150/seed_005/trace.jsonl | 0-43 | 44 | `True` | -0.2740 | -3.4244 | 1.3197 | 0.1339 | 1.1692 | 0.1092 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
