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
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0030 | 0.1123 | 0.1538 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0056 | 0.0995 | 0.1527 | 1 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0052 | 0.0823 | 0.1536 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0076 | 0.0741 | 0.1526 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0051 | 0.1569 | 0.1506 | 3 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0074 | 0.1235 | 0.1507 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0079 | 0.1280 | 0.1506 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0098 | 0.0782 | 0.1503 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0023 | 0.1041 | 0.1559 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0060 | 0.1060 | 0.1527 | 1 |
| seed_000.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0060 | 0.0883 | 0.1537 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0080 | 0.0825 | 0.1526 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0056 | 0.1535 | 0.1528 | 3 |
| seed_002.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0077 | 0.1287 | 0.1527 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0078 | 0.1113 | 0.1527 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0103 | 0.0850 | 0.1525 | 1 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0022 | 0.1019 | 0.1518 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0060 | 0.0940 | 0.1521 | 1 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0053 | 0.0764 | 0.1518 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0085 | 0.0803 | 0.1513 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0033 | 0.1394 | 0.1486 | 3 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0080 | 0.1117 | 0.1486 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0074 | 0.1404 | 0.1484 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0108 | 0.0782 | 0.1483 | 2 |
| seed_000.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0054 | 0.1051 | 0.1528 | 2 |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0079 | 0.1031 | 0.1527 | 1 |
| seed_000.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0072 | 0.0838 | 0.1527 | 0 |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0093 | 0.0772 | 0.1526 | 0 |
| seed_000.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0068 | 0.1434 | 0.1497 | 3 |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0092 | 0.1226 | 0.1498 | 3 |
| seed_000.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0096 | 0.1232 | 0.1497 | 2 |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0116 | 0.0826 | 0.1497 | 1 |
| seed_000.jsonl | `primitive_p0p9_hrb0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0047 | 0.0906 | 0.1549 | 0 |
| seed_002.jsonl | `primitive_p0p9_hrb0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0085 | 0.1047 | 0.1527 | 1 |
| seed_000.jsonl | `primitive_p0p9_hrb0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0073 | 0.1070 | 0.1537 | 1 |
| seed_002.jsonl | `primitive_p0p9_hrb0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0092 | 0.0792 | 0.1526 | 0 |
| seed_000.jsonl | `primitive_p0p9_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0073 | 0.1422 | 0.1518 | 3 |
| seed_002.jsonl | `primitive_p0p9_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0099 | 0.1277 | 0.1518 | 3 |
| seed_000.jsonl | `primitive_p0p9_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0096 | 0.1374 | 0.1518 | 2 |
| seed_002.jsonl | `primitive_p0p9_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0117 | 0.0935 | 0.1517 | 1 |
| seed_000.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0042 | 0.0933 | 0.1508 | 1 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0078 | 0.0911 | 0.1508 | 1 |
| seed_000.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0073 | 0.0806 | 0.1506 | 0 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0100 | 0.0789 | 0.1506 | 0 |
| seed_000.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0062 | 0.1452 | 0.1477 | 3 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0097 | 0.1133 | 0.1477 | 3 |
| seed_000.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0093 | 0.1462 | 0.1476 | 2 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0123 | 0.0841 | 0.1475 | 1 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_000.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0775 | 0.0702 | 0.2394 | 0.1515 | 0.0000 | 0.3454 | 0.0654 | None | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p9_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0757 | 0.0831 | 0.2368 | 0.1534 | 0.0000 | 0.3454 | 0.0662 | None | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0746 | 0.1798 | 0.2394 | 0.1515 | 0.0000 | 0.3460 | 0.0863 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0742 | 0.0759 | 0.2335 | 0.1497 | 0.0000 | 0.3454 | 0.0642 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p9_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0737 | 0.1679 | 0.2368 | 0.1534 | 0.0000 | 0.3460 | 0.0858 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0735 | 0.1648 | 0.2014 | 0.1537 | 0.0000 | 0.4466 | 0.0891 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0735 | 0.1745 | 0.2081 | 0.1526 | 0.0000 | 0.4466 | 0.0903 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0718 | 0.0647 | 0.2081 | 0.1525 | 0.0000 | 0.4196 | 0.0640 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0716 | 0.0777 | 0.2014 | 0.1547 | 0.0000 | 0.4196 | 0.0629 | None | `{'01': 8.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p9_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0688 | 0.2071 | 0.1717 | 0.1527 | 0.0000 | 0.3460 | 0.0871 | None | `{'01': 8.0, '10': 8.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0681 | 0.1806 | 0.2330 | 0.1497 | 0.0000 | 0.3460 | 0.0882 | None | `{'01': 24.0, '11': 76.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0669 | 0.2020 | 0.1421 | 0.1527 | 0.0000 | 0.4466 | 0.0887 | None | `{'01': 8.0, '10': 8.0, '11': 84.0}` |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0648 | 0.2028 | 0.1614 | 0.1527 | 0.0000 | 0.3460 | 0.0866 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0646 | 0.2010 | 0.1341 | 0.1527 | 0.0000 | 0.4466 | 0.0880 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0644 | 0.1824 | 0.1536 | 0.1524 | 0.0000 | 0.3460 | 0.0844 | None | `{'01': 12.0, '10': 8.0, '11': 80.0}` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0622 | 0.1831 | 0.1226 | 0.1526 | 0.0000 | 0.4466 | 0.0866 | None | `{'01': 12.0, '10': 8.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 0-24 | 0.0621 | 0.1559 | 0.1907 | 0.1504 | 0.0000 | 0.3443 | 0.0695 | None | `{'01': 20.0, '11': 80.0}` |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0611 | 0.0349 | 0.1679 | 0.1534 | 0.0000 | 0.3454 | 0.0549 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p9_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0607 | 0.0449 | 0.1766 | 0.1549 | 0.0000 | 0.3454 | 0.0572 | None | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0606 | 0.0708 | 0.1936 | 0.1509 | 0.0000 | 0.4196 | 0.0614 | None | `{'01': 8.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0606 | 0.0369 | 0.1606 | 0.1517 | 0.0000 | 0.3454 | 0.0529 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p9_hrb0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0605 | 0.1131 | 0.1766 | 0.1551 | 0.0000 | 0.3454 | 0.0578 | None | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 5-29 | 0.0592 | 0.0563 | 0.1907 | 0.1502 | 0.0000 | 0.3473 | 0.0612 | None | `{'01': 12.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0589 | 0.0936 | 0.1606 | 0.1524 | 0.0000 | 0.3454 | 0.0537 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0580 | 0.1055 | 0.1679 | 0.1539 | 0.0000 | 0.3454 | 0.0555 | None | `{'11': 100.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
