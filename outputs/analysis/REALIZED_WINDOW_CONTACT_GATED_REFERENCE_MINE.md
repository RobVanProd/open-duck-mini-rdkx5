# Realized Target Window Mine

status: `PASS_REALIZED_WINDOWS_AVAILABLE`

This mines existing simulated rollout traces for short windows that already
show realized forward motion under actual sim/contact dynamics. It produces
a manifest, not a raw BC dataset.

## Criteria

- window_samples: `25`
- stride_samples: `5`
- min_mean_vx: `0.04`
- max_pitch_abs_p95: `0.45`
- min_base_height: `0.1`
- max_action_saturation_pct: `5.0`
- min_done_margin: `10`

## Trace Summary

| source | mode | samples | done_count | mean_vx | max_vx | min_height | candidates |
|---|---|---:|---:|---:|---:|---:|---:|
| reference_seed_000.jsonl | `reference_target_contact_gated_projected` | 85 | 1 | 0.0078 | 0.1186 | 0.1535 | 1 |
| reference_seed_001.jsonl | `reference_target_contact_gated_projected` | 29 | 1 | -0.0124 | 0.0494 | 0.0820 | 0 |
| reference_seed_002.jsonl | `reference_target_contact_gated_projected` | 140 | 1 | 0.0077 | 0.1548 | 0.1527 | 1 |
| reference_seed_003.jsonl | `reference_target_contact_gated_projected` | 70 | 1 | -0.0132 | 0.1112 | 0.1562 | 0 |
| reference_seed_004.jsonl | `reference_target_contact_gated_projected` | 168 | 1 | 0.0079 | 0.1650 | 0.1518 | 5 |
| reference_seed_005.jsonl | `reference_target_contact_gated_projected` | 250 | 0 | 0.0092 | 0.2119 | 0.1471 | 5 |
| reference_seed_006.jsonl | `reference_target_contact_gated_projected` | 70 | 1 | -0.0107 | 0.0988 | 0.1573 | 0 |
| reference_seed_007.jsonl | `reference_target_contact_gated_projected` | 32 | 1 | 0.0129 | 0.0923 | 0.1007 | 0 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| reference_seed_005.jsonl | `reference_target_contact_gated_projected` | 15-39 | 0.0782 | 0.1569 | 0.1470 | 0.1579 | 0.2857 | 2.4978 | 0.1292 | None | `{'10': 12.0, '11': 88.0}` |
| reference_seed_005.jsonl | `reference_target_contact_gated_projected` | 0-24 | 0.0713 | 0.1997 | 0.2142 | 0.1471 | 1.1429 | 4.1206 | 0.1912 | None | `{'00': 8.0, '01': 12.0, '10': 16.0, '11': 64.0}` |
| reference_seed_005.jsonl | `reference_target_contact_gated_projected` | 5-29 | 0.0708 | 0.1997 | 0.2142 | 0.1619 | 0.8571 | 3.3223 | 0.1378 | None | `{'01': 12.0, '10': 16.0, '11': 72.0}` |
| reference_seed_004.jsonl | `reference_target_contact_gated_projected` | 15-39 | 0.0660 | 0.1290 | 0.1121 | 0.1568 | 0.2857 | 2.6837 | 0.1217 | 128 | `{'01': 8.0, '10': 12.0, '11': 80.0}` |
| reference_seed_005.jsonl | `reference_target_contact_gated_projected` | 10-34 | 0.0653 | 0.1588 | 0.1852 | 0.1579 | 0.5714 | 3.1571 | 0.1475 | None | `{'01': 12.0, '10': 12.0, '11': 76.0}` |
| reference_seed_002.jsonl | `reference_target_contact_gated_projected` | 0-24 | 0.0624 | 0.1576 | 0.0697 | 0.1527 | 0.2857 | 2.5407 | 0.1382 | 115 | `{'01': 16.0, '10': 8.0, '11': 76.0}` |
| reference_seed_005.jsonl | `reference_target_contact_gated_projected` | 20-44 | 0.0607 | 0.1078 | 0.0904 | 0.1575 | 0.2857 | 2.2239 | 0.1005 | None | `{'10': 4.0, '11': 96.0}` |
| reference_seed_004.jsonl | `reference_target_contact_gated_projected` | 10-34 | 0.0600 | 0.1290 | 0.1287 | 0.1568 | 0.0000 | 2.7786 | 0.1270 | 133 | `{'01': 12.0, '10': 12.0, '11': 76.0}` |
| reference_seed_004.jsonl | `reference_target_contact_gated_projected` | 5-29 | 0.0570 | 0.1313 | 0.1301 | 0.1603 | 0.2857 | 2.7907 | 0.1133 | 138 | `{'01': 16.0, '10': 12.0, '11': 72.0}` |
| reference_seed_004.jsonl | `reference_target_contact_gated_projected` | 20-44 | 0.0452 | 0.1249 | 0.0737 | 0.1568 | 0.2857 | 2.2239 | 0.1165 | 123 | `{'01': 4.0, '10': 8.0, '11': 88.0}` |
| reference_seed_004.jsonl | `reference_target_contact_gated_projected` | 0-24 | 0.0449 | 0.1313 | 0.1301 | 0.1518 | 0.5714 | 3.4200 | 0.1359 | 143 | `{'01': 24.0, '10': 20.0, '11': 56.00000000000001}` |
| reference_seed_000.jsonl | `reference_target_contact_gated_projected` | 0-24 | 0.0412 | 0.1060 | 0.0781 | 0.1535 | 0.2857 | 2.1173 | 0.1245 | 60 | `{'01': 12.0, '11': 88.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
