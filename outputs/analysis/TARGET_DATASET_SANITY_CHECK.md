# Target Dataset Sanity Check

status: `WARN_TARGET_DATASET_SANITY_SOURCE_SKEW`

This check recomputes compact window metrics from local source traces.
It does not copy raw traces and does not start training.

## Summary

- manifest: `outputs/analysis/target_dataset_manifest.json`
- dataset_id: `e84d27e27fd73419`
- entries_checked: `11`
- entries_with_errors: `0`
- bc_ready_entries: `0`
- bc_readiness_status: `HOLD_TARGET_DATASET_BC_OBSERVATIONS_MISSING`
- source_files: `2`
- max_source_fraction: `0.9091`

## Warnings

- `source_distribution_skew`

## Entry Results

| id | source | ticks | errors | vx | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| 2a7bd9fc33b096a5 | seed_000.jsonl | 5-29 | `none; bc=policy_observation_missing` | 0.0666 | 0.0695 | 0.2267 | 0.1530 | 0.2142 | 0.0678 |
| 3be6bc711c1cb60f | seed_000.jsonl | 5-29 | `none; bc=policy_observation_missing` | 0.0533 | 0.0747 | 0.1777 | 0.1570 | 0.3684 | 0.0642 |
| 6b5719ffa6b03898 | seed_000.jsonl | 5-29 | `none; bc=policy_observation_missing` | 0.0747 | 0.0521 | 0.2354 | 0.1497 | 0.2232 | 0.0549 |
| 820f3a47f60489e9 | seed_000.jsonl | 5-29 | `none; bc=policy_observation_missing` | 0.0443 | 0.0487 | 0.2106 | 0.1490 | 0.4388 | 0.0635 |
| a691b5a0dda671b7 | seed_000.jsonl | 5-29 | `none; bc=policy_observation_missing` | 0.1077 | 0.0778 | 0.3013 | 0.1497 | 0.7888 | 0.0709 |
| b0d6057166e873d6 | seed_000.jsonl | 5-29 | `none; bc=policy_observation_missing` | 0.0783 | 0.0676 | 0.2519 | 0.1509 | 0.2239 | 0.0707 |
| b38385599492fbc0 | seed_000.jsonl | 5-29 | `none; bc=policy_observation_missing` | 0.0773 | 0.0728 | 0.2503 | 0.1515 | 0.1838 | 0.0686 |
| b90fc4db3c6ecc51 | seed_000.jsonl | 5-29 | `none; bc=policy_observation_missing` | 0.0911 | 0.0829 | 0.2561 | 0.1510 | 0.4196 | 0.0708 |
| d1425640dbf28dee | seed_000.jsonl | 5-29 | `none; bc=policy_observation_missing` | 0.0417 | 0.0847 | 0.1316 | 0.1550 | 0.3338 | 0.0605 |
| ef79fe45c63694c6 | seed_000.jsonl | 5-29 | `none; bc=policy_observation_missing` | 0.0823 | 0.0684 | 0.2267 | 0.1527 | 0.4097 | 0.0671 |
| 53731e48e0297c71 | seed_002.jsonl | 5-29 | `none; bc=policy_observation_missing` | 0.0726 | 0.0910 | 0.1825 | 0.1484 | 0.3233 | 0.0552 |

## Gate

- A pass or warning-pass here only proves the compact manifest matches local trace evidence.
- `bc_readiness_status` must pass before behavior cloning or supervised action training.
- Review source skew before any supervised/imitation smoke run.
