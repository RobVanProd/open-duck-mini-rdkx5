# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `31d7463352d8834d`
- entries: `2`
- samples: `1000`
- bc_ready_entries: `2`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| ppo_warmstart_restore_policy_kl100_640/seed_001/trace.jsonl | 0-499 | 500 | `True` | -0.0006 | -0.0078 | 0.7370 | 0.0693 | 0.0502 | 0.1556 |
| ppo_warmstart_step0/seed_001/trace.jsonl | 0-499 | 500 | `True` | 0.0361 | 0.4509 | 2.2016 | 0.1742 | 0.1002 | 0.1556 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
