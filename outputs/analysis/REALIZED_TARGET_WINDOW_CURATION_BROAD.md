# Realized Target Window Curation

status: `HOLD_INSUFFICIENT_CURATED_WINDOWS`

This applies stricter dataset-readiness filters to the mined realized
motion windows. It does not export raw traces or start training.

## Criteria

- min_curated_windows: `8`
- min_mean_vx: `0.04`
- max_vy_abs_p95: `0.12`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_action_saturation_pct: `1.0`
- max_sent_velocity_p95: `2.5`
- max_tracking_p95: `0.12`
- min_done_margin: `50`
- max_contact_dominance_pct: `95.0`
- min_source_files: `2`
- min_source_mode_pairs: `2`

## Counts

- mined_windows: `94`
- pass_curated_seed_windows: `1`
- review_motion_hints: `37`
- rejected_dataset_seeds: `56`
- curated_source_files: `1`
- curated_modes: `1`
- curated_source_mode_pairs: `1`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| v7_x008_trace.jsonl | `vanilla` | 0-24 | 0.0656 | 0.0956 | 0.2717 | 0.1513 | 1.9668 | 0.0971 | None | 92.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| phase1_x008_trace.jsonl | `fitted` | 5-29 | 0.1023 | `high_lateral_velocity, high_body_pitch` |
| phase1_x008_trace.jsonl | `fitted` | 0-24 | 0.0906 | `high_lateral_velocity` |
| phase1_x008_trace.jsonl | `fitted` | 10-34 | 0.0857 | `high_lateral_velocity, high_body_pitch, short_done_margin, single_contact_pattern_dominates` |
| phase1_x008_trace.jsonl | `fitted` | 15-39 | 0.0694 | `high_body_pitch, short_done_margin, single_contact_pattern_dominates` |
| phase1_x008_trace.jsonl | `fitted` | 20-44 | 0.0552 | `high_body_pitch, short_done_margin, single_contact_pattern_dominates` |
| phase1_x008_trace.jsonl | `fitted` | 25-49 | 0.0418 | `high_body_pitch, short_done_margin, single_contact_pattern_dominates` |
| v7_x008_trace.jsonl | `fitted` | 5-29 | 0.1071 | `high_lateral_velocity, high_body_pitch, short_done_margin` |
| v7_x008_trace.jsonl | `fitted` | 10-34 | 0.1057 | `high_lateral_velocity, high_body_pitch, short_done_margin, single_contact_pattern_dominates` |
| v7_x008_trace.jsonl | `fitted` | 0-24 | 0.0985 | `high_lateral_velocity, high_body_pitch, short_done_margin` |
| v7_x008_trace.jsonl | `stress` | 5-29 | 0.0562 | `high_lateral_velocity` |
| v7_x008_trace.jsonl | `stress` | 10-34 | 0.0558 | `high_lateral_velocity` |
| v7_x008_trace.jsonl | `stress` | 0-24 | 0.0534 | `high_lateral_velocity` |
| v7_x008_trace.jsonl | `vanilla` | 5-29 | 0.0515 | `single_contact_pattern_dominates` |
| v7_x008_trace.jsonl | `stress` | 15-39 | 0.0451 | `single_contact_pattern_dominates` |
| reference_seed_004.jsonl | `reference_target_contact_gated_projected` | 20-44 | 0.0452 | `high_lateral_velocity` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
