# Push-Window Trace Snippets

status: `PASS_PUSH_WINDOW_SNIPPETS_READY`

This is an offline trace-curation artifact. It does not train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_home_support_push_failure_trace_seeds_0_2_6.json`
- output_trace_dir: `outputs/analysis/phase2_z0075_home_support_push_window_snippets`
- failed_only: `True`
- include_recovered: `False`
- pre_ticks: `8`
- post_ticks: `8`
- truncate_done: `True`
- sample_weight: `4.0`

## Summary

- snippets: `4`
- samples: `175`

| seed | event | ticks | samples | recovered | terminated | push | pitch max | height min | output |
|---:|---:|---:|---:|---|---|---:|---:|---:|---|
| 0 | 0 | 52-112 | 61 | `False` | `True` | 0.0798 | 1.3779 | 0.0059 | `outputs/analysis/phase2_z0075_home_support_push_window_snippets/seed_000/push_000_6e6c2d394c022b4d.jsonl` |
| 2 | 9 | 561-602 | 42 | `False` | `True` | 0.1063 | 1.4035 | 0.0821 | `outputs/analysis/phase2_z0075_home_support_push_window_snippets/seed_002/push_009_e969257189933035.jsonl` |
| 6 | 10 | 607-670 | 64 | `False` | `True` | 0.0759 | 1.3916 | 0.0755 | `outputs/analysis/phase2_z0075_home_support_push_window_snippets/seed_006/push_010_712c01db7c0c749d.jsonl` |
| 6 | 11 | 663-670 | 8 | `False` | `True` | 0.1065 | 1.3916 | 0.0755 | `outputs/analysis/phase2_z0075_home_support_push_window_snippets/seed_006/push_011_420a187c0ff36573.jsonl` |

## Gate

- These snippets are local data for offline relabeling or supervised recovery checks.
- They are not a candidate policy and do not prove deployability.
