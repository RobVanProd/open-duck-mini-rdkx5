# Weighted BC Manifest

status: `PASS_WEIGHTED_BC_MANIFEST_READY`

This offline artifact applies per-entry sample weights to a BC trace manifest.
It does not copy raw traces, train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- input_manifest: `outputs/analysis/phase2_seed5_early_state_aggregate_manifest.json`
- dataset_id: `ca1396ea4ded6b94`
- entries: `14`
- samples: `3043`
- weighted_samples: `3430.0000`

## Rules

- `phase2_seed5_capped_neighbor_trace_compare` -> `10.0`

## Entries

| source | samples | weight | weighted_samples | matched_rule |
|---|---:|---:|---:|---|
| phase2_seed4_right_swing_weighted_traces/phase2_transition_action_space_compare_seed4/transition_protected_seed4w/seed_004/trace.jsonl | 250 | 1.0000 | 250.0000 | `default` |
| phase2_seed4_weighted_right_knee_limited_traces/phase2_transition_action_space_compare_seed2/transition_protected_seed4w/seed_002/trace.jsonl | 250 | 1.0000 | 250.0000 | `default` |
| phase2_seed5_capped_neighbor_trace_compare_x0/seed5_capped/seed_005/trace.jsonl | 18 | 10.0000 | 180.0000 | `phase2_seed5_capped_neighbor_trace_compare` |
| phase2_seed5_capped_neighbor_trace_compare_x008/seed5_capped/seed_005/trace.jsonl | 25 | 10.0000 | 250.0000 | `phase2_seed5_capped_neighbor_trace_compare` |
| relabel_x0/rollouts_x0/student/seed_000/trace.jsonl | 250 | 1.0000 | 250.0000 | `default` |
| rollouts_x0/student/seed_000/trace.jsonl | 250 | 1.0000 | 250.0000 | `default` |
| rollouts_x0/student/seed_004/trace.jsonl | 250 | 1.0000 | 250.0000 | `default` |
| rollouts_x008/student/seed_000/trace.jsonl | 250 | 1.0000 | 250.0000 | `default` |
| rollouts_x008/student/seed_001/trace.jsonl | 250 | 1.0000 | 250.0000 | `default` |
| rollouts_x008/student/seed_002/trace.jsonl | 250 | 1.0000 | 250.0000 | `default` |
| rollouts_x008/student/seed_003/trace.jsonl | 250 | 1.0000 | 250.0000 | `default` |
| rollouts_x008/student/seed_005/trace.jsonl | 250 | 1.0000 | 250.0000 | `default` |
| rollouts_x008/student/seed_006/trace.jsonl | 250 | 1.0000 | 250.0000 | `default` |
| rollouts_x008/student/seed_007/trace.jsonl | 250 | 1.0000 | 250.0000 | `default` |

## Gate

- Weights are for offline supervised curation only.
- A weighted manifest is not a candidate policy.
- Robot validation remains blocked until closed-loop gates pass.
