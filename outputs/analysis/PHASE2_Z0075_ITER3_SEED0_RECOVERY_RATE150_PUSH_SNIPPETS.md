# Push-Window Trace Snippets

status: `PASS_PUSH_WINDOW_SNIPPETS_READY`

This is an offline trace-curation artifact. It does not train, deploy, SSH, run robot tests, or change runtime behavior.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_iter3_seed0_recovery_rate150_seed0_failure_trace.json`
- output_trace_dir: `outputs/analysis/phase2_z0075_iter3_seed0_recovery_rate150_seed0_push_snippets`
- failed_only: `True`
- include_recovered: `False`
- pre_ticks: `25`
- post_ticks: `45`
- truncate_done: `True`
- sample_weight: `4.0`

## Summary

- snippets: `2`
- samples: `119`

| seed | event | ticks | samples | recovered | terminated | push | pitch max | height min | output |
|---:|---:|---:|---:|---|---|---:|---:|---:|---|
| 0 | 0 | 35-124 | 90 | `False` | `False` | 0.0798 | 1.1207 | 0.0940 | `outputs/analysis/phase2_z0075_iter3_seed0_recovery_rate150_seed0_push_snippets/seed_000/push_000_70c15afbddc5679d.jsonl` |
| 0 | 1 | 96-124 | 29 | `False` | `True` | 0.1203 | 1.3409 | 0.0037 | `outputs/analysis/phase2_z0075_iter3_seed0_recovery_rate150_seed0_push_snippets/seed_000/push_001_52fa7376aaf9cfc5.jsonl` |

## Gate

- These snippets are local data for offline relabeling or supervised recovery checks.
- They are not a candidate policy and do not prove deployability.
