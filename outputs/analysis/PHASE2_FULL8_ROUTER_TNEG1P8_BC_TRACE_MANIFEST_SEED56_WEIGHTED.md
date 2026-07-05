# Weighted BC Manifest

status: `PASS_WEIGHTED_BC_MANIFEST_READY`

This offline artifact applies per-entry sample weights to a BC trace manifest.
It does not copy raw traces, train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- input_manifest: `outputs/analysis/phase2_full8_router_tneg1p8_bc_trace_manifest.json`
- dataset_id: `0d70a9bc13b02924`
- entries: `16`
- samples: `12000`
- weighted_samples: `16500.0000`

## Rules

- `x008.*/seed_005` -> `4.0`
- `x008.*/seed_006` -> `4.0`

## Entries

| source | samples | weight | weighted_samples | matched_rule |
|---|---:|---:|---:|---|
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_002/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_003/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_004/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_005/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_006/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_full8_router_tneg1p8_trace_x000/full8_router_tneg1p8/seed_007/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_002/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_003/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_004/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_005/trace.jsonl | 750 | 4.0000 | 3000.0000 | `x008.*/seed_005` |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_006/trace.jsonl | 750 | 4.0000 | 3000.0000 | `x008.*/seed_006` |
| phase2_full8_router_tneg1p8_trace_x008/full8_router_tneg1p8/seed_007/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |

## Gate

- Weights are for offline supervised curation only.
- A weighted manifest is not a candidate policy.
- Robot validation remains blocked until closed-loop gates pass.
