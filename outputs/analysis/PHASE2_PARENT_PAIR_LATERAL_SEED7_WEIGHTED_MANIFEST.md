# Weighted BC Manifest

status: `PASS_WEIGHTED_BC_MANIFEST_READY`

This offline artifact applies per-entry sample weights to a BC trace manifest.
It does not copy raw traces, train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- input_manifest: `outputs/analysis/phase2_online_router_parent_pair_lateral_selected_manifest.json`
- dataset_id: `cbca4cd9878899ea`
- entries: `5`
- samples: `3750`
- weighted_samples: `5250.0000`

## Rules

- `seed_007` -> `3.0`

## Entries

| source | samples | weight | weighted_samples | matched_rule |
|---|---:|---:|---:|---|
| phase2_health_routed_parent_phase_modulated_trace_gate/phase_mod_parent/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_health_routed_parent_phase_modulated_trace_gate/phase_mod_parent/seed_002/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_health_routed_parent_phase_modulated_trace_gate/phase_mod_parent/seed_006/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_online_router_fresh_rich_context_parent_gate/rich_context_parent/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_online_router_fresh_rich_context_parent_gate/rich_context_parent/seed_007/trace.jsonl | 750 | 3.0000 | 2250.0000 | `seed_007` |

## Gate

- Weights are for offline supervised curation only.
- A weighted manifest is not a candidate policy.
- Robot validation remains blocked until closed-loop gates pass.
