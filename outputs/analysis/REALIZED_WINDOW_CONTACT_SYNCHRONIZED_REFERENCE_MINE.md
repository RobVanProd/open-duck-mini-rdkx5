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
| reference_seed_000.jsonl | `reference_target_contact_synchronized_projected` | 91 | 1 | 0.0078 | 0.1305 | 0.1559 | 3 |
| reference_seed_001.jsonl | `reference_target_contact_synchronized_projected` | 31 | 1 | -0.1310 | 0.0085 | 0.1031 | 0 |
| reference_seed_002.jsonl | `reference_target_contact_synchronized_projected` | 168 | 1 | 0.0079 | 0.1404 | 0.1527 | 2 |
| reference_seed_003.jsonl | `reference_target_contact_synchronized_projected` | 70 | 1 | -0.0106 | 0.0620 | 0.1595 | 0 |
| reference_seed_004.jsonl | `reference_target_contact_synchronized_projected` | 245 | 1 | 0.0079 | 0.1867 | 0.1518 | 5 |
| reference_seed_005.jsonl | `reference_target_contact_synchronized_projected` | 250 | 0 | 0.0095 | 0.2114 | 0.1471 | 5 |
| reference_seed_006.jsonl | `reference_target_contact_synchronized_projected` | 70 | 1 | -0.0041 | 0.1478 | 0.1585 | 3 |
| reference_seed_007.jsonl | `reference_target_contact_synchronized_projected` | 38 | 1 | -0.0087 | 0.0498 | 0.0646 | 0 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| reference_seed_005.jsonl | `reference_target_contact_synchronized_projected` | 0-24 | 0.0931 | 0.2370 | 0.2243 | 0.1471 | 1.1429 | 5.2400 | 0.1912 | None | `{'00': 8.0, '01': 28.000000000000004, '10': 36.0, '11': 28.000000000000004}` |
| reference_seed_004.jsonl | `reference_target_contact_synchronized_projected` | 15-39 | 0.0867 | 0.0834 | 0.1345 | 0.1587 | 0.8571 | 2.7182 | 0.0828 | 205 | `{'11': 100.0}` |
| reference_seed_005.jsonl | `reference_target_contact_synchronized_projected` | 5-29 | 0.0863 | 0.2086 | 0.2243 | 0.1590 | 1.1429 | 5.1861 | 0.1645 | None | `{'01': 28.000000000000004, '10': 32.0, '11': 40.0}` |
| reference_seed_004.jsonl | `reference_target_contact_synchronized_projected` | 10-34 | 0.0846 | 0.0853 | 0.1347 | 0.1592 | 0.5714 | 2.8451 | 0.0821 | 210 | `{'11': 100.0}` |
| reference_seed_005.jsonl | `reference_target_contact_synchronized_projected` | 10-34 | 0.0834 | 0.1539 | 0.1884 | 0.1590 | 1.1429 | 4.0332 | 0.1612 | None | `{'01': 16.0, '10': 28.000000000000004, '11': 56.00000000000001}` |
| reference_seed_005.jsonl | `reference_target_contact_synchronized_projected` | 15-39 | 0.0832 | 0.1218 | 0.1594 | 0.1590 | 0.8571 | 3.6675 | 0.1456 | None | `{'10': 28.000000000000004, '11': 72.0}` |
| reference_seed_006.jsonl | `reference_target_contact_synchronized_projected` | 15-39 | 0.0723 | 0.1235 | 0.1462 | 0.1585 | 0.8571 | 5.2400 | 0.1444 | 30 | `{'01': 16.0, '10': 24.0, '11': 60.0}` |
| reference_seed_004.jsonl | `reference_target_contact_synchronized_projected` | 5-29 | 0.0709 | 0.0930 | 0.1404 | 0.1619 | 0.8571 | 2.7182 | 0.0883 | 215 | `{'11': 100.0}` |
| reference_seed_002.jsonl | `reference_target_contact_synchronized_projected` | 0-24 | 0.0700 | 0.1307 | 0.1081 | 0.1527 | 0.5714 | 5.2400 | 0.1363 | 143 | `{'01': 16.0, '10': 12.0, '11': 72.0}` |
| reference_seed_004.jsonl | `reference_target_contact_synchronized_projected` | 20-44 | 0.0608 | 0.0708 | 0.1345 | 0.1587 | 0.5714 | 2.8451 | 0.0843 | 200 | `{'11': 100.0}` |
| reference_seed_000.jsonl | `reference_target_contact_synchronized_projected` | 10-34 | 0.0603 | 0.0956 | 0.1201 | 0.1594 | 0.8571 | 2.7182 | 0.0843 | 56 | `{'11': 100.0}` |
| reference_seed_006.jsonl | `reference_target_contact_synchronized_projected` | 10-34 | 0.0564 | 0.2450 | 0.1167 | 0.1587 | 0.5714 | 5.2400 | 0.1516 | 35 | `{'01': 32.0, '10': 24.0, '11': 44.0}` |
| reference_seed_006.jsonl | `reference_target_contact_synchronized_projected` | 20-44 | 0.0552 | 0.1235 | 0.1462 | 0.1585 | 0.5714 | 4.7386 | 0.1280 | 25 | `{'01': 16.0, '10': 4.0, '11': 80.0}` |
| reference_seed_002.jsonl | `reference_target_contact_synchronized_projected` | 5-29 | 0.0531 | 0.1204 | 0.1174 | 0.1601 | 0.5714 | 3.9165 | 0.1057 | 138 | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| reference_seed_000.jsonl | `reference_target_contact_synchronized_projected` | 5-29 | 0.0491 | 0.1017 | 0.1140 | 0.1596 | 0.5714 | 2.8451 | 0.0975 | 61 | `{'11': 100.0}` |
| reference_seed_004.jsonl | `reference_target_contact_synchronized_projected` | 0-24 | 0.0478 | 0.0964 | 0.1404 | 0.1518 | 0.8571 | 3.7658 | 0.1165 | 220 | `{'10': 8.0, '11': 92.0}` |
| reference_seed_005.jsonl | `reference_target_contact_synchronized_projected` | 20-44 | 0.0426 | 0.1218 | 0.1594 | 0.1590 | 0.5714 | 3.3373 | 0.1182 | None | `{'10': 8.0, '11': 92.0}` |
| reference_seed_000.jsonl | `reference_target_contact_synchronized_projected` | 15-39 | 0.0410 | 0.0820 | 0.1201 | 0.1594 | 0.5714 | 2.8451 | 0.0810 | 51 | `{'11': 100.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
