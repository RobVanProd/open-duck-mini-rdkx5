# Target Dataset Sanity Check

status: `HOLD_TARGET_DATASET_SANITY_ERRORS`

This check recomputes compact window metrics from local source traces.
It does not copy raw traces and does not start training.

## Summary

- manifest: `outputs/analysis/phase2_a2_seed5_z005_recovery_from_z002_bc_manifest.json`
- dataset_id: `7101dabd524e54f0`
- entries_checked: `1`
- entries_with_errors: `1`
- bc_ready_entries: `1`
- bc_readiness_status: `PASS_TARGET_DATASET_BC_READY`
- source_files: `1`
- max_source_fraction: `1.0000`

## Warnings

- `source_distribution_skew`
- `single_source_file`

## Entry Results

| id | source | ticks | errors | vx | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| b24fb89a31a70490 | analysis/phase2_a2_seed5_z005_recovery_from_z002_relabel_trace.jsonl | 20-60 | `contact_dominance_pct_mismatch, done_inside_window, high_body_pitch, low_base_height, low_forward_velocity` | -0.4044 | 0.1008 | 1.4070 | 0.0512 | 0.7768 | 0.0718 |

## Gate

- A pass or warning-pass here only proves the compact manifest matches local trace evidence.
- `bc_readiness_status` must pass before behavior cloning or supervised action training.
- Review source skew before any supervised/imitation smoke run.
