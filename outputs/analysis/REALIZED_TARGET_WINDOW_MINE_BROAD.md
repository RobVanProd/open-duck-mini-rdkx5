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
| phase1_x008_trace.jsonl | `fitted` | 80 | 1 | 0.1892 | 1.2424 | 0.0434 | 6 |
| v7_x008_trace.jsonl | `vanilla` | 750 | 0 | 0.0018 | 0.1921 | 0.1506 | 2 |
| v7_x008_trace.jsonl | `fitted` | 59 | 1 | 0.2654 | 1.3183 | 0.0388 | 3 |
| v7_x008_trace.jsonl | `stress` | 750 | 0 | 0.0016 | 0.1558 | 0.1499 | 4 |
| trace.jsonl | `vanilla` | 250 | 0 | 0.0018 | 0.1123 | 0.1537 | 0 |
| trace.jsonl | `vanilla` | 34 | 1 | -0.1549 | 0.0064 | 0.0884 | 0 |
| trace.jsonl | `vanilla` | 250 | 0 | 0.0033 | 0.0959 | 0.1526 | 0 |
| trace.jsonl | `vanilla` | 250 | 0 | -0.0088 | 0.0096 | 0.1549 | 0 |
| trace.jsonl | `vanilla` | 250 | 0 | 0.0013 | 0.0807 | 0.1539 | 0 |
| trace.jsonl | `vanilla` | 35 | 1 | -0.1641 | -0.0110 | 0.1059 | 0 |
| trace.jsonl | `vanilla` | 250 | 0 | 0.0019 | 0.0882 | 0.1526 | 0 |
| trace.jsonl | `vanilla` | 250 | 0 | -0.0090 | 0.0269 | 0.1558 | 0 |
| reference_seed_000.jsonl | `reference_target_contact_gated_projected` | 85 | 1 | 0.0078 | 0.1186 | 0.1535 | 1 |
| reference_seed_001.jsonl | `reference_target_contact_gated_projected` | 29 | 1 | -0.0124 | 0.0494 | 0.0820 | 0 |
| reference_seed_002.jsonl | `reference_target_contact_gated_projected` | 140 | 1 | 0.0077 | 0.1548 | 0.1527 | 1 |
| reference_seed_003.jsonl | `reference_target_contact_gated_projected` | 70 | 1 | -0.0132 | 0.1112 | 0.1562 | 0 |
| reference_seed_004.jsonl | `reference_target_contact_gated_projected` | 168 | 1 | 0.0079 | 0.1650 | 0.1518 | 5 |
| reference_seed_005.jsonl | `reference_target_contact_gated_projected` | 250 | 0 | 0.0092 | 0.2119 | 0.1471 | 5 |
| reference_seed_006.jsonl | `reference_target_contact_gated_projected` | 70 | 1 | -0.0107 | 0.0988 | 0.1573 | 0 |
| reference_seed_007.jsonl | `reference_target_contact_gated_projected` | 32 | 1 | 0.0129 | 0.0923 | 0.1007 | 0 |
| reference_seed_000.jsonl | `reference_target_contact_synchronized_projected` | 91 | 1 | 0.0078 | 0.1305 | 0.1559 | 3 |
| reference_seed_001.jsonl | `reference_target_contact_synchronized_projected` | 31 | 1 | -0.1310 | 0.0085 | 0.1031 | 0 |
| reference_seed_002.jsonl | `reference_target_contact_synchronized_projected` | 168 | 1 | 0.0079 | 0.1404 | 0.1527 | 2 |
| reference_seed_003.jsonl | `reference_target_contact_synchronized_projected` | 70 | 1 | -0.0106 | 0.0620 | 0.1595 | 0 |
| reference_seed_004.jsonl | `reference_target_contact_synchronized_projected` | 245 | 1 | 0.0079 | 0.1867 | 0.1518 | 5 |
| reference_seed_005.jsonl | `reference_target_contact_synchronized_projected` | 250 | 0 | 0.0095 | 0.2114 | 0.1471 | 5 |
| reference_seed_006.jsonl | `reference_target_contact_synchronized_projected` | 70 | 1 | -0.0041 | 0.1478 | 0.1585 | 3 |
| reference_seed_007.jsonl | `reference_target_contact_synchronized_projected` | 38 | 1 | -0.0087 | 0.0498 | 0.0646 | 0 |
| reference_seed_000.jsonl | `reference_target_cycle_projected` | 70 | 1 | 0.0055 | 0.0964 | 0.1559 | 1 |
| reference_seed_001.jsonl | `reference_target_cycle_projected` | 34 | 1 | -0.0991 | 0.0059 | 0.0995 | 0 |
| reference_seed_002.jsonl | `reference_target_cycle_projected` | 111 | 1 | 0.0074 | 0.1434 | 0.1527 | 1 |
| reference_seed_003.jsonl | `reference_target_cycle_projected` | 70 | 1 | -0.0196 | 0.0786 | 0.1570 | 0 |
| reference_seed_004.jsonl | `reference_target_cycle_projected` | 112 | 1 | 0.0079 | 0.1364 | 0.1517 | 2 |
| reference_seed_005.jsonl | `reference_target_cycle_projected` | 52 | 1 | -0.2814 | 0.1668 | 0.0707 | 0 |
| reference_seed_006.jsonl | `reference_target_cycle_projected` | 70 | 1 | -0.0170 | 0.0890 | 0.1569 | 0 |
| reference_seed_007.jsonl | `reference_target_cycle_projected` | 36 | 1 | 0.0074 | 0.0639 | 0.0894 | 0 |
| reference_seed_000.jsonl | `reference_target_cycle_projected` | 70 | 1 | 0.0040 | 0.1349 | 0.1537 | 1 |
| reference_seed_001.jsonl | `reference_target_cycle_projected` | 33 | 1 | -0.1382 | 0.0068 | 0.1036 | 0 |
| reference_seed_002.jsonl | `reference_target_cycle_projected` | 83 | 1 | 0.0077 | 0.1556 | 0.1526 | 1 |
| reference_seed_003.jsonl | `reference_target_cycle_projected` | 70 | 1 | -0.0167 | 0.0884 | 0.1559 | 0 |
| reference_seed_004.jsonl | `reference_target_cycle_projected` | 110 | 1 | 0.0077 | 0.1341 | 0.1517 | 2 |
| reference_seed_005.jsonl | `reference_target_cycle_projected` | 180 | 1 | 0.0078 | 0.1763 | 0.1471 | 4 |
| reference_seed_006.jsonl | `reference_target_cycle_projected` | 70 | 1 | -0.0074 | 0.1611 | 0.1569 | 0 |
| reference_seed_007.jsonl | `reference_target_cycle_projected` | 37 | 1 | -0.0223 | 0.1096 | 0.0805 | 0 |
| reference_seed_000.jsonl | `reference_target_cycle_projected` | 70 | 1 | 0.0017 | 0.0861 | 0.1534 | 0 |
| reference_seed_001.jsonl | `reference_target_cycle_projected` | 34 | 1 | -0.0835 | 0.0101 | 0.0932 | 0 |
| reference_seed_002.jsonl | `reference_target_cycle_projected` | 88 | 1 | 0.0080 | 0.1623 | 0.1526 | 1 |
| reference_seed_003.jsonl | `reference_target_cycle_projected` | 70 | 1 | -0.0108 | 0.1074 | 0.1552 | 0 |
| reference_seed_004.jsonl | `reference_target_cycle_projected` | 101 | 1 | 0.0079 | 0.1374 | 0.1518 | 4 |
| reference_seed_005.jsonl | `reference_target_cycle_projected` | 195 | 1 | 0.0078 | 0.2126 | 0.1471 | 5 |
| reference_seed_006.jsonl | `reference_target_cycle_projected` | 70 | 1 | -0.0119 | 0.1300 | 0.1565 | 1 |
| reference_seed_007.jsonl | `reference_target_cycle_projected` | 36 | 1 | 0.0009 | 0.0989 | 0.0947 | 0 |
| reference_seed_000.jsonl | `reference_target_raw` | 70 | 1 | -0.0028 | 0.1102 | 0.1534 | 0 |
| reference_seed_001.jsonl | `reference_target_raw` | 34 | 1 | -0.0886 | 0.0159 | 0.0969 | 0 |
| reference_seed_002.jsonl | `reference_target_raw` | 73 | 1 | 0.0079 | 0.1940 | 0.1526 | 0 |
| reference_seed_003.jsonl | `reference_target_raw` | 70 | 1 | -0.0208 | 0.0584 | 0.1570 | 0 |
| reference_seed_004.jsonl | `reference_target_raw` | 101 | 1 | 0.0079 | 0.0926 | 0.1518 | 0 |
| reference_seed_005.jsonl | `reference_target_raw` | 181 | 1 | 0.0078 | 0.2310 | 0.1471 | 0 |
| reference_seed_006.jsonl | `reference_target_raw` | 70 | 1 | -0.0050 | 0.0647 | 0.1582 | 0 |
| reference_seed_007.jsonl | `reference_target_raw` | 36 | 1 | 0.0099 | 0.1556 | 0.1021 | 0 |
| trace_seed0.jsonl | `fitted` | 750 | 0 | 0.0015 | 0.1381 | 0.1511 | 2 |
| trace.jsonl | `fitted` | 750 | 0 | 0.0015 | 0.1381 | 0.1511 | 2 |
| trace.jsonl | `fitted` | 31 | 1 | 0.0045 | 0.0737 | 0.0673 | 0 |
| trace.jsonl | `fitted` | 54 | 1 | -0.3111 | 0.1639 | 0.0332 | 0 |
| trace.jsonl | `fitted` | 750 | 0 | 0.0006 | 0.1638 | 0.1508 | 4 |
| trace.jsonl | `fitted` | 27 | 1 | 0.0044 | 0.1289 | 0.0911 | 0 |
| trace.jsonl | `vanilla` | 60 | 1 | 0.0111 | 0.1025 | 0.1536 | 2 |
| trace.jsonl | `vanilla` | 32 | 1 | -0.0996 | -0.0138 | 0.1026 | 0 |
| trace.jsonl | `vanilla` | 60 | 1 | 0.0182 | 0.1052 | 0.1525 | 1 |
| trace.jsonl | `vanilla` | 60 | 1 | -0.0055 | 0.0841 | 0.1561 | 0 |
| trace.jsonl | `vanilla` | 70 | 1 | 0.0014 | 0.1060 | 0.1536 | 0 |
| trace.jsonl | `vanilla` | 70 | 1 | 0.0014 | 0.1060 | 0.1536 | 0 |
| trace.jsonl | `vanilla` | 34 | 1 | -0.0913 | -0.0160 | 0.0916 | 0 |
| trace.jsonl | `vanilla` | 70 | 1 | 0.0077 | 0.1033 | 0.1526 | 0 |
| trace.jsonl | `vanilla` | 70 | 1 | -0.0157 | 0.0250 | 0.1579 | 0 |
| trace.jsonl | `vanilla` | 152 | 1 | 0.0080 | 0.1044 | 0.1513 | 1 |
| trace.jsonl | `vanilla` | 50 | 1 | -0.3133 | 0.1354 | 0.0506 | 0 |
| trace.jsonl | `vanilla` | 70 | 1 | -0.0143 | 0.0315 | 0.1588 | 0 |
| trace.jsonl | `vanilla` | 33 | 1 | -0.0135 | 0.0341 | 0.0961 | 0 |
| trace.jsonl | `fitted` | 59 | 1 | 0.2654 | 1.3183 | 0.0388 | 3 |
| trace.jsonl | `fitted` | 32 | 1 | 0.0005 | 0.0537 | 0.0688 | 0 |
| trace.jsonl | `fitted` | 73 | 1 | 0.2217 | 1.3564 | 0.0305 | 5 |
| trace.jsonl | `fitted` | 32 | 1 | 0.0185 | 0.1341 | 0.0672 | 0 |
| trace.jsonl | `fitted` | 750 | 0 | 0.0020 | 0.1932 | 0.1503 | 3 |
| trace.jsonl | `fitted` | 56 | 1 | -0.3045 | 0.1649 | 0.0298 | 0 |
| trace.jsonl | `fitted` | 58 | 1 | 0.2749 | 1.3888 | 0.0233 | 3 |
| trace.jsonl | `fitted` | 27 | 1 | -0.0060 | 0.1323 | 0.0919 | 0 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| trace.jsonl | `fitted` | 10-34 | 0.1325 | 0.2814 | 0.4271 | 0.1497 | 0.0000 | 1.3621 | 0.0744 | 23 | `{'01': 28.000000000000004, '11': 72.0}` |
| v7_x008_trace.jsonl | `fitted` | 5-29 | 0.1071 | 0.1649 | 0.3954 | 0.1500 | 0.0000 | 1.3416 | 0.0907 | 29 | `{'01': 20.0, '11': 80.0}` |
| trace.jsonl | `fitted` | 5-29 | 0.1071 | 0.1649 | 0.3954 | 0.1500 | 0.0000 | 1.3416 | 0.0907 | 29 | `{'01': 20.0, '11': 80.0}` |
| v7_x008_trace.jsonl | `fitted` | 10-34 | 0.1057 | 0.1500 | 0.4356 | 0.1500 | 0.0000 | 0.6808 | 0.0818 | 24 | `{'01': 4.0, '11': 96.0}` |
| trace.jsonl | `fitted` | 10-34 | 0.1057 | 0.1500 | 0.4356 | 0.1500 | 0.0000 | 0.6808 | 0.0818 | 24 | `{'01': 4.0, '11': 96.0}` |
| phase1_x008_trace.jsonl | `fitted` | 5-29 | 0.1023 | 0.1676 | 0.3555 | 0.1489 | 0.0000 | 1.2030 | 0.0812 | 50 | `{'01': 20.0, '10': 4.0, '11': 76.0}` |
| trace.jsonl | `fitted` | 5-29 | 0.0995 | 0.2814 | 0.3655 | 0.1497 | 0.0000 | 1.5740 | 0.0750 | 28 | `{'01': 48.0, '11': 52.0}` |
| v7_x008_trace.jsonl | `fitted` | 0-24 | 0.0985 | 0.1792 | 0.3629 | 0.1500 | 0.0000 | 2.0062 | 0.1111 | 34 | `{'01': 28.000000000000004, '11': 72.0}` |
| trace.jsonl | `fitted` | 0-24 | 0.0985 | 0.1792 | 0.3629 | 0.1500 | 0.0000 | 2.0062 | 0.1111 | 34 | `{'01': 28.000000000000004, '11': 72.0}` |
| reference_seed_005.jsonl | `reference_target_contact_synchronized_projected` | 0-24 | 0.0931 | 0.2370 | 0.2243 | 0.1471 | 1.1429 | 5.2400 | 0.1912 | None | `{'00': 8.0, '01': 28.000000000000004, '10': 36.0, '11': 28.000000000000004}` |
| trace.jsonl | `fitted` | 5-29 | 0.0911 | 0.1862 | 0.3644 | 0.1492 | 0.0000 | 1.4711 | 0.1037 | 43 | `{'01': 20.0, '11': 80.0}` |
| phase1_x008_trace.jsonl | `fitted` | 0-24 | 0.0906 | 0.1676 | 0.3144 | 0.1506 | 0.0000 | 2.3110 | 0.1095 | 55 | `{'01': 28.000000000000004, '10': 4.0, '11': 68.0}` |
| trace.jsonl | `fitted` | 10-34 | 0.0901 | 0.2578 | 0.3262 | 0.1508 | 0.0000 | 1.1649 | 0.0664 | None | `{'01': 28.000000000000004, '10': 4.0, '11': 68.0}` |
| trace.jsonl | `fitted` | 0-24 | 0.0890 | 0.1934 | 0.3455 | 0.1492 | 0.0000 | 2.2965 | 0.1203 | 48 | `{'01': 28.000000000000004, '11': 72.0}` |
| reference_seed_004.jsonl | `reference_target_contact_synchronized_projected` | 15-39 | 0.0867 | 0.0834 | 0.1345 | 0.1587 | 0.8571 | 2.7182 | 0.0828 | 205 | `{'11': 100.0}` |
| reference_seed_005.jsonl | `reference_target_contact_synchronized_projected` | 5-29 | 0.0863 | 0.2086 | 0.2243 | 0.1590 | 1.1429 | 5.1861 | 0.1645 | None | `{'01': 28.000000000000004, '10': 32.0, '11': 40.0}` |
| phase1_x008_trace.jsonl | `fitted` | 10-34 | 0.0857 | 0.1609 | 0.3853 | 0.1474 | 0.0000 | 0.7491 | 0.0674 | 45 | `{'10': 4.0, '11': 96.0}` |
| reference_seed_004.jsonl | `reference_target_contact_synchronized_projected` | 10-34 | 0.0846 | 0.0853 | 0.1347 | 0.1592 | 0.5714 | 2.8451 | 0.0821 | 210 | `{'11': 100.0}` |
| reference_seed_005.jsonl | `reference_target_contact_synchronized_projected` | 10-34 | 0.0834 | 0.1539 | 0.1884 | 0.1590 | 1.1429 | 4.0332 | 0.1612 | None | `{'01': 16.0, '10': 28.000000000000004, '11': 56.00000000000001}` |
| reference_seed_005.jsonl | `reference_target_contact_synchronized_projected` | 15-39 | 0.0832 | 0.1218 | 0.1594 | 0.1590 | 0.8571 | 3.6675 | 0.1456 | None | `{'10': 28.000000000000004, '11': 72.0}` |
| trace.jsonl | `fitted` | 15-39 | 0.0791 | 0.2578 | 0.3279 | 0.1508 | 0.0000 | 1.1456 | 0.0674 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| trace.jsonl | `fitted` | 10-34 | 0.0790 | 0.1013 | 0.3752 | 0.1492 | 0.0000 | 0.8458 | 0.0876 | 38 | `{'01': 4.0, '11': 96.0}` |
| reference_seed_005.jsonl | `reference_target_contact_gated_projected` | 15-39 | 0.0782 | 0.1569 | 0.1470 | 0.1579 | 0.2857 | 2.4978 | 0.1292 | None | `{'10': 12.0, '11': 88.0}` |
| reference_seed_005.jsonl | `reference_target_cycle_projected` | 0-24 | 0.0780 | 0.2192 | 0.2279 | 0.1471 | 1.1429 | 3.1142 | 0.2287 | 155 | `{'00': 8.0, '01': 24.0, '10': 32.0, '11': 36.0}` |
| trace.jsonl | `fitted` | 5-29 | 0.0770 | 0.2578 | 0.3033 | 0.1509 | 0.0000 | 1.3935 | 0.0694 | None | `{'01': 48.0, '10': 4.0, '11': 48.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
