# Push-Window Trace Snippets

status: `PASS_PUSH_WINDOW_SNIPPETS_READY`

This is an offline trace-curation artifact. It does not train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_iter21_balanced_seed67_weight2_seed1_trace.json`
- output_trace_dir: `outputs/analysis/phase2_z0075_iter21_balanced_seed67_weight2_seed1_push_snippets`
- failed_only: `True`
- include_recovered: `False`
- pre_ticks: `30`
- post_ticks: `35`
- truncate_done: `True`
- sample_weight: `2.0`

## Summary

- snippets: `1`
- samples: `44`

| seed | event | ticks | samples | recovered | terminated | push | pitch max | height min | output |
|---:|---:|---:|---:|---|---|---:|---:|---:|---|
| 1 | 7 | 409-452 | 44 | `False` | `True` | 0.0880 | 1.4586 | 0.0153 | `outputs/analysis/phase2_z0075_iter21_balanced_seed67_weight2_seed1_push_snippets/seed_001/push_007_fba4e22442dd5a9c.jsonl` |

## Gate

- These snippets are local data for offline relabeling or supervised recovery checks.
- They are not a candidate policy and do not prove deployability.
