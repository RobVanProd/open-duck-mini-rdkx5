# Weighted BC Manifest

status: `PASS_WEIGHTED_BC_MANIFEST_READY`

This offline artifact applies per-entry sample weights to a BC trace manifest.
It does not copy raw traces, train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- input_manifest: `outputs/analysis/phase2_transition_protected_rate_limit_manifest.json`
- dataset_id: `92a4f63a6fa0b869`
- entries: `2`
- samples: `500`
- weighted_samples: `1000.0000`

## Rules

- `seed_004` -> `3.0`

## Entries

| source | samples | weight | weighted_samples | matched_rule |
|---|---:|---:|---:|---|
| phase2_transition_protected_rate_limit_traces/rollouts_x008/student/seed_002/trace.jsonl | 250 | 1.0000 | 250.0000 | `default` |
| phase2_transition_protected_rate_limit_traces/rollouts_x008/student/seed_004/trace.jsonl | 250 | 3.0000 | 750.0000 | `seed_004` |

## Gate

- Weights are for offline supervised curation only.
- A weighted manifest is not a candidate policy.
- Robot validation remains blocked until closed-loop gates pass.
