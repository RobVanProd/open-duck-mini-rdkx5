# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `6ccbb7ea49f243c6`
- entries: `5`
- samples: `3750`
- bc_ready_entries: `5`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| phase2_health_routed_parent_phase_modulated_trace_gate/phase_mod_parent/seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0258 | 0.3230 | 1.4087 | 0.1383 | 0.2077 | 0.1554 |
| phase2_health_routed_parent_phase_modulated_trace_gate/phase_mod_parent/seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0263 | 0.3285 | 1.4180 | 0.1379 | 0.1764 | 0.1592 |
| phase2_health_routed_parent_phase_modulated_trace_gate/phase_mod_parent/seed_006/trace.jsonl | 0-749 | 750 | `True` | 0.0241 | 0.3009 | 1.4152 | 0.1385 | 0.1850 | 0.1572 |
| phase2_online_router_fresh_rich_context_parent_gate/rich_context_parent/seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0232 | 0.2897 | 1.4186 | 0.1385 | 0.1661 | 0.1591 |
| phase2_online_router_fresh_rich_context_parent_gate/rich_context_parent/seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0264 | 0.3302 | 1.4231 | 0.1407 | 0.1775 | 0.1589 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
