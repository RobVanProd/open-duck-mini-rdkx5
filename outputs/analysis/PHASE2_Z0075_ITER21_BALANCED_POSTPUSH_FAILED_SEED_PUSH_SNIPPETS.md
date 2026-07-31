# Push-Window Trace Snippets

status: `PASS_PUSH_WINDOW_SNIPPETS_READY`

This is an offline trace-curation artifact. It does not train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_iter21_balanced_postpush_failed_seed_traces.json`
- output_trace_dir: `outputs/analysis/phase2_z0075_iter21_balanced_postpush_failed_seed_push_snippets`
- failed_only: `True`
- include_recovered: `False`
- pre_ticks: `30`
- post_ticks: `35`
- truncate_done: `True`
- sample_weight: `4.0`

## Summary

- snippets: `2`
- samples: `147`

| seed | event | ticks | samples | recovered | terminated | push | pitch max | height min | output |
|---:|---:|---:|---:|---|---|---:|---:|---:|---|
| 6 | 2 | 137-210 | 74 | `False` | `True` | 0.1136 | 1.4473 | -0.0091 | `outputs/analysis/phase2_z0075_iter21_balanced_postpush_failed_seed_push_snippets/seed_006/push_002_d58ee50a26422599.jsonl` |
| 7 | 7 | 545-617 | 73 | `False` | `True` | 0.0922 | 1.4154 | -0.0075 | `outputs/analysis/phase2_z0075_iter21_balanced_postpush_failed_seed_push_snippets/seed_007/push_007_0083b1968111b80b.jsonl` |

## Gate

- These snippets are local data for offline relabeling or supervised recovery checks.
- They are not a candidate policy and do not prove deployability.
