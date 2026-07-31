# Push-Window Trace Snippets

status: `PASS_PUSH_WINDOW_SNIPPETS_READY`

This is an offline trace-curation artifact. It does not train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_iter21_seed67_w2_seed1_seed2_reverse_trace.json`
- output_trace_dir: `outputs/analysis/phase2_z0075_iter21_seed67_w2_seed1_seed2_reverse_push_snippets`
- failed_only: `True`
- include_recovered: `False`
- pre_ticks: `30`
- post_ticks: `35`
- truncate_done: `True`
- sample_weight: `2.0`

## Summary

- snippets: `1`
- samples: `84`

| seed | event | ticks | samples | recovered | terminated | push | pitch max | height min | output |
|---:|---:|---:|---:|---|---|---:|---:|---:|---|
| 2 | 3 | 197-280 | 84 | `False` | `True` | 0.1149 | 1.3561 | 0.0816 | `outputs/analysis/phase2_z0075_iter21_seed67_w2_seed1_seed2_reverse_push_snippets/seed_002/push_003_385805db95510321.jsonl` |

## Gate

- These snippets are local data for offline relabeling or supervised recovery checks.
- They are not a candidate policy and do not prove deployability.
