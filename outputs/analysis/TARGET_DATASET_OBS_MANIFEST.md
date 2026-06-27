# Target Dataset Manifest

status: `PASS_TARGET_DATASET_MANIFEST_READY`

This is a compact manifest of curated low-command target windows.
It does not include raw trace contents and does not start training.

## Summary

- input_curation_json: `outputs/analysis/target_generator_shuffled_broad_obs_window_curation.json`
- dataset_id: `6c43c18e8f2b72ec`
- entries: `11`
- source_files: `2`
- source_mode_pairs: `11`
- raw_traces_present: `True`

## Source Distribution

| source | windows |
|---|---:|
| seed_000.jsonl | 10 |
| seed_002.jsonl | 1 |

## Metric Summary

| metric | min | mean | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| mean_vx_m_s | 0.0417 | 0.0718 | 0.0747 | 0.0994 | 0.1077 |
| vy_abs_p95_m_s | 0.0487 | 0.0718 | 0.0728 | 0.0879 | 0.0910 |
| body_pitch_abs_p95_rad | 0.1316 | 0.2228 | 0.2267 | 0.2787 | 0.3013 |
| base_height_min_m | 0.1484 | 0.1516 | 0.1510 | 0.1560 | 0.1570 |
| sent_target_velocity_p95_rad_s | 0.1838 | 0.3571 | 0.3338 | 0.6138 | 0.7888 |
| joint_tracking_p95_rad | 0.0549 | 0.0649 | 0.0671 | 0.0709 | 0.0709 |
| contact_dominance_pct | 84.0000 | 89.4545 | 92.0000 | 92.0000 | 92.0000 |

## Windows

| id | source | ticks | vx | vy95 | pitch95 | height | sent_vel95 | track95 | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 242c8b4fcaf48d30 | seed_000.jsonl | 5-29 | 0.0533 | 0.0747 | 0.1777 | 0.1570 | 0.3684 | 0.0642 | 92.0000 |
| 4047cd2dba2a194c | seed_000.jsonl | 5-29 | 0.1077 | 0.0778 | 0.3013 | 0.1497 | 0.7888 | 0.0709 | 84.0000 |
| 73dcd1c634a84490 | seed_000.jsonl | 5-29 | 0.0417 | 0.0847 | 0.1316 | 0.1550 | 0.3338 | 0.0605 | 92.0000 |
| 950e47ad0b2d37e5 | seed_000.jsonl | 5-29 | 0.0443 | 0.0487 | 0.2106 | 0.1490 | 0.4388 | 0.0635 | 92.0000 |
| 98b0914e34f3f722 | seed_000.jsonl | 5-29 | 0.0911 | 0.0829 | 0.2561 | 0.1510 | 0.4196 | 0.0708 | 88.0000 |
| d071f8615381de10 | seed_000.jsonl | 5-29 | 0.0747 | 0.0521 | 0.2354 | 0.1497 | 0.2232 | 0.0549 | 92.0000 |
| db65184e78360c9b | seed_000.jsonl | 5-29 | 0.0783 | 0.0676 | 0.2519 | 0.1509 | 0.2239 | 0.0707 | 92.0000 |
| e377c286d6e0803f | seed_000.jsonl | 5-29 | 0.0666 | 0.0695 | 0.2267 | 0.1530 | 0.2142 | 0.0678 | 88.0000 |
| e94f7e850842b146 | seed_000.jsonl | 5-29 | 0.0773 | 0.0728 | 0.2503 | 0.1515 | 0.1838 | 0.0686 | 88.0000 |
| f5c2b6d5730bbcbb | seed_000.jsonl | 5-29 | 0.0823 | 0.0684 | 0.2267 | 0.1527 | 0.4097 | 0.0671 | 84.0000 |
| 814925f5a9233474 | seed_002.jsonl | 5-29 | 0.0726 | 0.0910 | 0.1825 | 0.1484 | 0.3233 | 0.0552 | 92.0000 |

## Gate

- This manifest is only seed material for a future supervised/imitation experiment.
- Do not train until the manifest and source skew are reviewed.
- Do not commit raw JSONL traces unless explicitly approved.
