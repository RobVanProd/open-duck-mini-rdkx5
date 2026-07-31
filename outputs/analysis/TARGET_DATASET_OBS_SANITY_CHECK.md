# Target Dataset Sanity Check

status: `WARN_TARGET_DATASET_SANITY_SOURCE_SKEW`

This check recomputes compact window metrics from local source traces.
It does not copy raw traces and does not start training.

## Summary

- manifest: `outputs/analysis/target_dataset_obs_manifest.json`
- dataset_id: `6c43c18e8f2b72ec`
- entries_checked: `11`
- entries_with_errors: `0`
- bc_ready_entries: `11`
- bc_readiness_status: `PASS_TARGET_DATASET_BC_READY`
- source_files: `2`
- max_source_fraction: `0.9091`

## Warnings

- `source_distribution_skew`

## Entry Results

| id | source | ticks | errors | vx | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| 242c8b4fcaf48d30 | seed_000.jsonl | 5-29 | `none` | 0.0533 | 0.0747 | 0.1777 | 0.1570 | 0.3684 | 0.0642 |
| 4047cd2dba2a194c | seed_000.jsonl | 5-29 | `none` | 0.1077 | 0.0778 | 0.3013 | 0.1497 | 0.7888 | 0.0709 |
| 73dcd1c634a84490 | seed_000.jsonl | 5-29 | `none` | 0.0417 | 0.0847 | 0.1316 | 0.1550 | 0.3338 | 0.0605 |
| 950e47ad0b2d37e5 | seed_000.jsonl | 5-29 | `none` | 0.0443 | 0.0487 | 0.2106 | 0.1490 | 0.4388 | 0.0635 |
| 98b0914e34f3f722 | seed_000.jsonl | 5-29 | `none` | 0.0911 | 0.0829 | 0.2561 | 0.1510 | 0.4196 | 0.0708 |
| d071f8615381de10 | seed_000.jsonl | 5-29 | `none` | 0.0747 | 0.0521 | 0.2354 | 0.1497 | 0.2232 | 0.0549 |
| db65184e78360c9b | seed_000.jsonl | 5-29 | `none` | 0.0783 | 0.0676 | 0.2519 | 0.1509 | 0.2239 | 0.0707 |
| e377c286d6e0803f | seed_000.jsonl | 5-29 | `none` | 0.0666 | 0.0695 | 0.2267 | 0.1530 | 0.2142 | 0.0678 |
| e94f7e850842b146 | seed_000.jsonl | 5-29 | `none` | 0.0773 | 0.0728 | 0.2503 | 0.1515 | 0.1838 | 0.0686 |
| f5c2b6d5730bbcbb | seed_000.jsonl | 5-29 | `none` | 0.0823 | 0.0684 | 0.2267 | 0.1527 | 0.4097 | 0.0671 |
| 814925f5a9233474 | seed_002.jsonl | 5-29 | `none` | 0.0726 | 0.0910 | 0.1825 | 0.1484 | 0.3233 | 0.0552 |

## Gate

- A pass or warning-pass here only proves the compact manifest matches local trace evidence.
- `bc_readiness_status` must pass before behavior cloning or supervised action training.
- Review source skew before any supervised/imitation smoke run.
