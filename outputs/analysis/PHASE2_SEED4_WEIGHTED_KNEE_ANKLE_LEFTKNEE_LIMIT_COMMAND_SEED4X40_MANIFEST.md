# Weighted BC Manifest

status: `PASS_WEIGHTED_BC_MANIFEST_READY`

This offline artifact applies per-entry sample weights to a BC trace manifest.
It does not copy raw traces, train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- input_manifest: `outputs/analysis/phase2_seed4_weighted_knee_ankle_leftknee_limit_command_manifest.json`
- dataset_id: `d25ae6e6b63e28c5`
- entries: `3`
- samples: `750`
- weighted_samples: `1500.0000`

## Rules

- `seed_004` -> `4.0`

## Entries

| source | samples | weight | weighted_samples | matched_rule |
|---|---:|---:|---:|---|
| phase2_seed4_weighted_knee_ankle_leftknee_limited_traces/phase2_seed4_weighted_right_knee_ankle_limited_traces/phase2_seed4_weighted_right_knee_limited_traces/phase2_transition_action_space_compare_seed2/transition_protected_seed4w/seed_002/trace.jsonl | 250 | 1.0000 | 250.0000 | `default` |
| phase2_seed4_weighted_knee_ankle_leftknee_limited_traces/phase2_seed4_weighted_right_knee_ankle_limited_traces/phase2_seed4_weighted_right_knee_limited_traces/phase2_transition_action_space_compare_seed4/transition_protected_seed4w/seed_004/trace.jsonl | 250 | 4.0000 | 1000.0000 | `seed_004` |
| rollouts_x0/student/seed_000/trace.jsonl | 250 | 1.0000 | 250.0000 | `default` |

## Gate

- Weights are for offline supervised curation only.
- A weighted manifest is not a candidate policy.
- Robot validation remains blocked until closed-loop gates pass.
