# Target Dataset Manifest

status: `PASS_TARGET_DATASET_MANIFEST_READY`

This is a compact manifest of curated low-command target windows.
It does not include raw trace contents and does not start training.

## Summary

- input_curation_json: `outputs/analysis/target_generator_dynamic_roll_lateral_fix_robust_modes_curation_50.json`
- dataset_id: `47153f26ab48ef14`
- entries: `9`
- source_files: `2`
- source_mode_pairs: `6`
- raw_traces_present: `True`

## Source Distribution

| source | windows |
|---|---:|
| seed_000.jsonl | 3 |
| seed_002.jsonl | 6 |

## Metric Summary

| metric | min | mean | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| mean_vx_m_s | 0.0401 | 0.0417 | 0.0416 | 0.0436 | 0.0437 |
| vy_abs_p95_m_s | 0.0431 | 0.0702 | 0.0716 | 0.0902 | 0.0910 |
| body_pitch_abs_p95_rad | 0.2417 | 0.2785 | 0.2782 | 0.3243 | 0.3294 |
| base_height_min_m | 0.1455 | 0.1468 | 0.1467 | 0.1484 | 0.1488 |
| sent_target_velocity_p95_rad_s | 0.5022 | 0.5133 | 0.5085 | 0.5296 | 0.5296 |
| joint_tracking_p95_rad | 0.0676 | 0.0714 | 0.0717 | 0.0751 | 0.0762 |
| contact_dominance_pct | 88.0000 | 92.6667 | 94.0000 | 94.0000 | 94.0000 |

## Windows

| id | source | ticks | vx | vy95 | pitch95 | height | sent_vel95 | track95 | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 049f91faaf0f89ce | seed_000.jsonl | 5-54 | 0.0416 | 0.0716 | 0.2789 | 0.1466 | 0.5022 | 0.0692 | 90.0000 |
| a3223fecee75c157 | seed_000.jsonl | 5-54 | 0.0423 | 0.0889 | 0.3294 | 0.1469 | 0.5025 | 0.0697 | 88.0000 |
| cdbc4efa2b19db62 | seed_000.jsonl | 5-54 | 0.0401 | 0.0881 | 0.3167 | 0.1455 | 0.5296 | 0.0719 | 92.0000 |
| 13248f6e57891bfd | seed_002.jsonl | 5-54 | 0.0410 | 0.0643 | 0.2417 | 0.1488 | 0.5025 | 0.0676 | 94.0000 |
| a0d2bef05974584b | seed_002.jsonl | 5-54 | 0.0435 | 0.0910 | 0.2782 | 0.1458 | 0.5296 | 0.0735 | 94.0000 |
| b106a81e6738ba7f | seed_002.jsonl | 5-54 | 0.0437 | 0.0736 | 0.2592 | 0.1475 | 0.5022 | 0.0717 | 94.0000 |
| 3e685b9f6658c91f | seed_002.jsonl | 10-59 | 0.0417 | 0.0586 | 0.2950 | 0.1455 | 0.5296 | 0.0762 | 94.0000 |
| c23b3f13d9cb14be | seed_002.jsonl | 10-59 | 0.0403 | 0.0522 | 0.2596 | 0.1467 | 0.5134 | 0.0717 | 94.0000 |
| e501ccdd19c42b18 | seed_002.jsonl | 10-59 | 0.0411 | 0.0431 | 0.2476 | 0.1478 | 0.5085 | 0.0707 | 94.0000 |

## Gate

- This manifest is only seed material for a future supervised/imitation experiment.
- Do not train until the manifest and source skew are reviewed.
- Do not commit raw JSONL traces unless explicitly approved.
