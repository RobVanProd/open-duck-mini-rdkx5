# Weighted BC Manifest

status: `PASS_WEIGHTED_BC_MANIFEST_READY`

This offline artifact applies per-entry sample weights to a BC trace manifest.
It does not copy raw traces, train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- input_manifest: `outputs/analysis/phase2_health_routed_parent_seed5_augmented_manifest.json`
- dataset_id: `3dd0f70627d138dc`
- entries: `8`
- samples: `6000`
- weighted_samples: `9000.0000`

## Rules

- `seed_005` -> `5.0`

## Entries

| source | samples | weight | weighted_samples | matched_rule |
|---|---:|---:|---:|---|
| phase2_health_routed_parent_ppo_step0_seed5_trace_compare/phase_parent/seed_005/trace.jsonl | 750 | 5.0000 | 3750.0000 | `seed_005` |
| phase2_policy_route_trace_iter24_27/iter24/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_policy_route_trace_iter24_27/iter24/seed_002/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_policy_route_trace_iter24_27/iter24/seed_007/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_policy_route_trace_iter25_26/iter25/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| phase2_policy_route_trace_iter25_26/iter25/seed_006/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x0/student/seed_000/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |
| rollouts_x0/student/seed_001/trace.jsonl | 750 | 1.0000 | 750.0000 | `default` |

## Gate

- Weights are for offline supervised curation only.
- A weighted manifest is not a candidate policy.
- Robot validation remains blocked until closed-loop gates pass.
