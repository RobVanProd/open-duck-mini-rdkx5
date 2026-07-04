# Push-Window Trace Snippets

status: `PASS_PUSH_WINDOW_SNIPPETS_READY`

This is an offline trace-curation artifact. It does not train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_iter21_resetsettle10_seed0_5_fullobs_push_contrast_gate.json`
- output_trace_dir: `outputs/analysis/phase2_z0075_iter21_seed5_late_push_recovery_snippets`
- failed_only: `True`
- include_recovered: `False`
- pre_ticks: `30`
- post_ticks: `35`
- truncate_done: `True`
- sample_weight: `4.0`

## Summary

- snippets: `1`
- samples: `79`

| seed | event | ticks | samples | recovered | terminated | push | pitch max | height min | output |
|---:|---:|---:|---:|---|---|---:|---:|---:|---|
| 5 | 9 | 519-597 | 79 | `False` | `True` | 0.0884 | 1.5047 | 0.0630 | `outputs/analysis/phase2_z0075_iter21_seed5_late_push_recovery_snippets/seed_005/push_009_200a8ce383346549.jsonl` |

## Gate

- These snippets are local data for offline relabeling or supervised recovery checks.
- They are not a candidate policy and do not prove deployability.
