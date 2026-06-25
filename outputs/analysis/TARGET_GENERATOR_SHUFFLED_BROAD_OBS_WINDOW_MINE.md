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
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p015_ph1p1781` | 150 | 0 | 0.0084 | 0.1525 | 0.1486 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p015_ph1p1781` | 150 | 0 | 0.0111 | 0.1345 | 0.1483 | 3 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p05_kb0_k0p12_ab0p04_am0p015_ph0p3927` | 150 | 0 | 0.0051 | 0.1485 | 0.1526 | 1 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p05_kb0_k0p12_ab0p04_am0p015_ph0p3927` | 150 | 0 | 0.0080 | 0.0939 | 0.1526 | 1 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p07_kb0p06_k0p12_ab0p04_am0p021_ph0` | 150 | 0 | 0.0092 | 0.2376 | 0.1437 | 4 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p07_kb0p06_k0p12_ab0p04_am0p021_ph0` | 150 | 0 | 0.0108 | 0.1793 | 0.1453 | 3 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p03_kb0p03_k0p04_ab0p04_am0p009_ph0` | 150 | 0 | 0.0050 | 0.0864 | 0.1534 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p03_kb0p03_k0p04_ab0p04_am0p009_ph0` | 150 | 0 | 0.0078 | 0.0940 | 0.1527 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0p04_hb0p04_h0p03_kb0_k0p08_ab0p08_am0p024_ph1p5708` | 150 | 0 | 0.0080 | 0.1336 | 0.1537 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrb0p04_hb0p04_h0p03_kb0_k0p08_ab0p08_am0p024_ph1p5708` | 150 | 0 | 0.0112 | 0.1209 | 0.1526 | 3 |
| seed_000.jsonl | `primitive_p0p55_hrb0p04_hb0p04_h0p07_kb0p06_k0p12_ab0p08_am0p056_ph0` | 49 | 1 | 0.3437 | 1.4013 | 0.0175 | 1 |
| seed_002.jsonl | `primitive_p0p55_hrb0p04_hb0p04_h0p07_kb0p06_k0p12_ab0p08_am0p056_ph0` | 53 | 1 | 0.3235 | 1.3645 | 0.0199 | 2 |
| seed_000.jsonl | `primitive_p0p55_hrb0p04_hb0p06_h0p03_kb0p06_k0p12_ab0p08_am0p015_ph0p3927` | 67 | 1 | 0.2234 | 1.2067 | 0.0453 | 4 |
| seed_002.jsonl | `primitive_p0p55_hrb0p04_hb0p06_h0p03_kb0p06_k0p12_ab0p08_am0p015_ph0p3927` | 150 | 0 | 0.0175 | 0.1848 | 0.1453 | 4 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p08_hb0p04_h0p05_kb0_k0p04_ab0_am0p04_ph0p7854` | 150 | 0 | -0.0006 | 0.0741 | 0.1533 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p08_hb0p04_h0p05_kb0_k0p04_ab0_am0p04_ph0p7854` | 150 | 0 | 0.0041 | 0.1154 | 0.1526 | 2 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph1p5708` | 68 | 1 | 0.2341 | 1.3411 | 0.0205 | 5 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph1p5708` | 67 | 1 | 0.2395 | 1.3255 | 0.0267 | 5 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p08_hb0p08_h0p07_kb0p03_k0p12_ab0_am0p021_ph0p7854` | 150 | 0 | -0.0007 | 0.1114 | 0.1473 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p08_hb0p08_h0p07_kb0p03_k0p12_ab0_am0p021_ph0p7854` | 150 | 0 | 0.0028 | 0.0765 | 0.1471 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p12_hb0p04_h0p07_kb0p06_k0p04_ab0p04_am0p056_ph1p5708` | 150 | 0 | 0.0049 | 0.1543 | 0.1423 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p12_hb0p04_h0p07_kb0p06_k0p04_ab0p04_am0p056_ph1p5708` | 150 | 0 | 0.0110 | 0.1031 | 0.1408 | 4 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p12_hb0p06_h0p03_kb0p03_k0p08_ab0p04_am0p009_ph0p7854` | 150 | 0 | 0.0025 | 0.0773 | 0.1448 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p12_hb0p06_h0p03_kb0p03_k0p08_ab0p04_am0p009_ph0p7854` | 150 | 0 | 0.0087 | 0.1020 | 0.1447 | 1 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p12_hb0p06_h0p03_kb0p06_k0p08_ab0p08_am0p009_ph0p3927` | 150 | 0 | 0.0068 | 0.1892 | 0.1394 | 3 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p12_hb0p06_h0p03_kb0p06_k0p08_ab0p08_am0p009_ph0p3927` | 150 | 0 | 0.0130 | 0.1713 | 0.1395 | 4 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0_k0p12_ab0p04_am0p015_ph0p7854` | 150 | 0 | 0.0051 | 0.1278 | 0.1523 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0_k0p12_ab0p04_am0p015_ph0p7854` | 150 | 0 | 0.0072 | 0.0832 | 0.1526 | 1 |
| seed_000.jsonl | `primitive_p0p7_hrb0p04_hb0p04_h0p05_kb0_k0p04_ab0p08_am0p015_ph0p7854` | 150 | 0 | 0.0080 | 0.1652 | 0.1537 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrb0p04_hb0p04_h0p05_kb0_k0p04_ab0p08_am0p015_ph0p7854` | 150 | 0 | 0.0109 | 0.1443 | 0.1526 | 2 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p08_hb0p06_h0p07_kb0p06_k0p08_ab0_am0p035_ph1p1781` | 150 | 0 | 0.0047 | 0.1239 | 0.1444 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p08_hb0p06_h0p07_kb0p06_k0p08_ab0_am0p035_ph1p1781` | 150 | 0 | 0.0082 | 0.0959 | 0.1434 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p08_hb0p08_h0p07_kb0p03_k0p12_ab0_am0p021_ph1p5708` | 150 | 0 | 0.0022 | 0.0901 | 0.1467 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p08_hb0p08_h0p07_kb0p03_k0p12_ab0_am0p021_ph1p5708` | 150 | 0 | 0.0042 | 0.0513 | 0.1467 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p12_hb0p08_h0p05_kb0_k0p12_ab0p04_am0p025_ph0` | 150 | 0 | -0.0001 | 0.0447 | 0.1457 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p12_hb0p08_h0p05_kb0_k0p12_ab0p04_am0p025_ph0` | 150 | 0 | 0.0060 | 0.0802 | 0.1457 | 1 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p16_hb0p04_h0p03_kb0_k0p08_ab0p04_am0p024_ph0p3927` | 150 | 0 | 0.0017 | 0.0766 | 0.1444 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p16_hb0p04_h0p03_kb0_k0p08_ab0p04_am0p024_ph0p3927` | 150 | 0 | 0.0077 | 0.0836 | 0.1444 | 1 |
| seed_000.jsonl | `primitive_p0p85_hrb0_hb0p04_h0p03_kb0_k0p04_ab0p08_am0p024_ph0` | 150 | 0 | 0.0078 | 0.1360 | 0.1530 | 2 |
| seed_002.jsonl | `primitive_p0p85_hrb0_hb0p04_h0p03_kb0_k0p04_ab0p08_am0p024_ph0` | 150 | 0 | 0.0109 | 0.1490 | 0.1526 | 3 |
| seed_000.jsonl | `primitive_p0p85_hrb0_hb0p06_h0p07_kb0p06_k0p04_ab0p04_am0p035_ph1p1781` | 150 | 0 | 0.0094 | 0.1889 | 0.1473 | 3 |
| seed_002.jsonl | `primitive_p0p85_hrb0_hb0p06_h0p07_kb0p06_k0p04_ab0p04_am0p035_ph1p1781` | 150 | 0 | 0.0109 | 0.1150 | 0.1473 | 3 |
| seed_000.jsonl | `primitive_p0p85_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0_am0p009_ph0p3927` | 150 | 0 | 0.0005 | 0.0347 | 0.1536 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0_am0p009_ph0p3927` | 150 | 0 | 0.0030 | 0.0734 | 0.1527 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrb0p04_hb0p04_h0p05_kb0_k0p04_ab0p04_am0p025_ph0` | 150 | 0 | 0.0059 | 0.0949 | 0.1538 | 1 |
| seed_002.jsonl | `primitive_p0p85_hrb0p04_hb0p04_h0p05_kb0_k0p04_ab0p04_am0p025_ph0` | 150 | 0 | 0.0083 | 0.1066 | 0.1527 | 1 |
| seed_000.jsonl | `primitive_p0p85_hrb0p04_hb0p06_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927` | 150 | 0 | 0.0106 | 0.1584 | 0.1501 | 3 |
| seed_002.jsonl | `primitive_p0p85_hrb0p04_hb0p06_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927` | 150 | 0 | 0.0131 | 0.1321 | 0.1500 | 3 |
| seed_000.jsonl | `primitive_p0p85_hrbm0p04_hb0p06_h0p07_kb0_k0p04_ab0p08_am0p021_ph0p7854` | 150 | 0 | 0.0090 | 0.1739 | 0.1492 | 3 |
| seed_002.jsonl | `primitive_p0p85_hrbm0p04_hb0p06_h0p07_kb0_k0p04_ab0p08_am0p021_ph0p7854` | 150 | 0 | 0.0130 | 0.1349 | 0.1493 | 3 |
| seed_000.jsonl | `primitive_p0p85_hrbm0p08_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p015_ph1p1781` | 150 | 0 | 0.0036 | 0.1170 | 0.1482 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrbm0p08_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p015_ph1p1781` | 150 | 0 | 0.0067 | 0.0815 | 0.1482 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p03_kb0_k0p04_ab0p04_am0p024_ph0p7854` | 150 | 0 | 0.0023 | 0.0396 | 0.1514 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p03_kb0_k0p04_ab0p04_am0p024_ph0p7854` | 150 | 0 | 0.0074 | 0.0829 | 0.1511 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p05_kb0_k0p12_ab0_am0p04_ph1p1781` | 150 | 0 | -0.0022 | 0.0302 | 0.1509 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p05_kb0_k0p12_ab0_am0p04_ph1p1781` | 150 | 0 | 0.0005 | 0.0570 | 0.1507 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p07_kb0p03_k0p08_ab0p08_am0p056_ph0p3927` | 56 | 1 | 0.2732 | 1.2336 | 0.0362 | 3 |
| seed_002.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p07_kb0p03_k0p08_ab0p08_am0p056_ph0p3927` | 106 | 1 | 0.1445 | 1.2372 | 0.0390 | 6 |
| seed_000.jsonl | `primitive_p0p85_hrbm0p12_hb0p08_h0p07_kb0p03_k0p12_ab0_am0p056_ph0` | 150 | 0 | 0.0006 | 0.0729 | 0.1449 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrbm0p12_hb0p08_h0p07_kb0p03_k0p12_ab0_am0p056_ph0` | 150 | 0 | 0.0073 | 0.0763 | 0.1447 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrbm0p16_hb0p08_h0p03_kb0p06_k0p04_ab0p04_am0p009_ph0` | 150 | 0 | 0.0055 | 0.1043 | 0.1400 | 3 |
| seed_002.jsonl | `primitive_p0p85_hrbm0p16_hb0p08_h0p03_kb0p06_k0p04_ab0p04_am0p009_ph0` | 150 | 0 | 0.0106 | 0.0730 | 0.1400 | 3 |
| seed_000.jsonl | `primitive_p1_hrb0_hb0p04_h0p03_kb0p03_k0p04_ab0p08_am0p015_ph1p1781` | 150 | 0 | 0.0081 | 0.1678 | 0.1502 | 3 |
| seed_002.jsonl | `primitive_p1_hrb0_hb0p04_h0p03_kb0p03_k0p04_ab0p08_am0p015_ph1p1781` | 150 | 0 | 0.0107 | 0.1540 | 0.1501 | 3 |
| seed_000.jsonl | `primitive_p1_hrb0_hb0p04_h0p07_kb0p03_k0p04_ab0_am0p035_ph1p1781` | 150 | 0 | 0.0014 | 0.1112 | 0.1510 | 2 |
| seed_002.jsonl | `primitive_p1_hrb0_hb0p04_h0p07_kb0p03_k0p04_ab0_am0p035_ph1p1781` | 150 | 0 | 0.0032 | 0.0963 | 0.1511 | 2 |
| seed_000.jsonl | `primitive_p1_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p024_ph1p5708` | 150 | 0 | 0.0101 | 0.1441 | 0.1472 | 3 |
| seed_002.jsonl | `primitive_p1_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p024_ph1p5708` | 150 | 0 | 0.0124 | 0.0808 | 0.1471 | 3 |
| seed_000.jsonl | `primitive_p1_hrb0p04_hb0p08_h0p05_kb0_k0p04_ab0p04_am0p015_ph0` | 150 | 0 | -0.0026 | 0.0419 | 0.1574 | 0 |
| seed_002.jsonl | `primitive_p1_hrb0p04_hb0p08_h0p05_kb0_k0p04_ab0p04_am0p015_ph0` | 150 | 0 | 0.0047 | 0.1102 | 0.1527 | 0 |
| seed_000.jsonl | `primitive_p1_hrbm0p04_hb0p04_h0p03_kb0p06_k0p08_ab0_am0p015_ph0p3927` | 150 | 0 | 0.0028 | 0.1170 | 0.1472 | 2 |
| seed_002.jsonl | `primitive_p1_hrbm0p04_hb0p04_h0p03_kb0p06_k0p08_ab0_am0p015_ph0p3927` | 150 | 0 | 0.0057 | 0.0759 | 0.1471 | 0 |
| seed_000.jsonl | `primitive_p1_hrbm0p04_hb0p06_h0p03_kb0_k0p08_ab0_am0p009_ph1p1781` | 150 | 0 | -0.0016 | 0.0347 | 0.1537 | 0 |
| seed_002.jsonl | `primitive_p1_hrbm0p04_hb0p06_h0p03_kb0_k0p08_ab0_am0p009_ph1p1781` | 150 | 0 | 0.0014 | 0.0581 | 0.1526 | 0 |
| seed_000.jsonl | `primitive_p1_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph0p3927` | 69 | 1 | 0.2110 | 1.1658 | 0.0424 | 5 |
| seed_002.jsonl | `primitive_p1_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph0p3927` | 103 | 1 | 0.1576 | 1.2872 | 0.0336 | 7 |
| seed_000.jsonl | `primitive_p1_hrbm0p12_hb0p06_h0p03_kb0_k0p12_ab0_am0p024_ph0p7854` | 150 | 0 | -0.0016 | 0.0758 | 0.1488 | 0 |
| seed_002.jsonl | `primitive_p1_hrbm0p12_hb0p06_h0p03_kb0_k0p12_ab0_am0p024_ph0p7854` | 150 | 0 | 0.0027 | 0.0981 | 0.1488 | 0 |
| seed_000.jsonl | `primitive_p1_hrbm0p16_hb0p08_h0p05_kb0p06_k0p04_ab0_am0p04_ph1p5708` | 150 | 0 | -0.0013 | 0.0813 | 0.1405 | 0 |
| seed_002.jsonl | `primitive_p1_hrbm0p16_hb0p08_h0p05_kb0p06_k0p04_ab0_am0p04_ph1p5708` | 150 | 0 | 0.0022 | 0.0837 | 0.1404 | 0 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_002.jsonl | `primitive_p0p55_hrb0p04_hb0p04_h0p07_kb0p06_k0p12_ab0p08_am0p056_ph0` | 5-29 | 0.1504 | 0.1237 | 0.3985 | 0.1487 | 0.0000 | 0.7888 | 0.0717 | 23 | `{'01': 4.0, '11': 96.0}` |
| seed_000.jsonl | `primitive_p0p55_hrb0p04_hb0p04_h0p07_kb0p06_k0p12_ab0p08_am0p056_ph0` | 0-24 | 0.1412 | 0.1370 | 0.3548 | 0.1490 | 0.0000 | 0.7879 | 0.1008 | 24 | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p07_kb0p03_k0p08_ab0p08_am0p056_ph0p3927` | 10-34 | 0.1399 | 0.0534 | 0.4011 | 0.1448 | 0.0000 | 0.4875 | 0.0706 | 21 | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0p04_hb0p04_h0p07_kb0p06_k0p12_ab0p08_am0p056_ph0` | 0-24 | 0.1380 | 0.1969 | 0.3204 | 0.1487 | 0.0000 | 0.7879 | 0.1041 | 28 | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p07_kb0p03_k0p08_ab0p08_am0p056_ph0p3927` | 5-29 | 0.1322 | 0.0924 | 0.3457 | 0.1461 | 0.0000 | 0.4875 | 0.0693 | 26 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p55_hrb0p04_hb0p06_h0p03_kb0p06_k0p12_ab0p08_am0p015_ph0p3927` | 5-29 | 0.1126 | 0.0655 | 0.3431 | 0.1497 | 0.0000 | 0.7022 | 0.0566 | 37 | `{'01': 12.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p07_kb0p03_k0p08_ab0p08_am0p056_ph0p3927` | 5-29 | 0.1097 | 0.1788 | 0.2812 | 0.1463 | 0.0000 | 0.4875 | 0.0647 | 76 | `{'10': 12.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p07_kb0p03_k0p08_ab0p08_am0p056_ph0p3927` | 10-34 | 0.1081 | 0.0537 | 0.2988 | 0.1460 | 0.0000 | 0.4875 | 0.0655 | 71 | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p07_kb0p06_k0p12_ab0p04_am0p021_ph0` | 5-29 | 0.1077 | 0.0778 | 0.3013 | 0.1497 | 0.0000 | 0.7888 | 0.0709 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p1_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph0p3927` | 5-29 | 0.1060 | 0.1128 | 0.3169 | 0.1454 | 0.0000 | 0.3233 | 0.0689 | 39 | `{'01': 20.0, '11': 80.0}` |
| seed_002.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p07_kb0p03_k0p08_ab0p08_am0p056_ph0p3927` | 0-24 | 0.1058 | 0.1993 | 0.2589 | 0.1474 | 0.0000 | 0.4931 | 0.0884 | 81 | `{'01': 12.0, '10': 20.0, '11': 68.0}` |
| seed_000.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p07_kb0p03_k0p08_ab0p08_am0p056_ph0p3927` | 0-24 | 0.1048 | 0.1888 | 0.3158 | 0.1461 | 0.0000 | 0.4931 | 0.0907 | 31 | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p07_kb0p06_k0p12_ab0p04_am0p021_ph0` | 0-24 | 0.1028 | 0.1706 | 0.2642 | 0.1497 | 0.0000 | 0.7879 | 0.0999 | None | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p55_hrb0p04_hb0p06_h0p03_kb0p06_k0p12_ab0p08_am0p015_ph0p3927` | 10-34 | 0.1026 | 0.0801 | 0.3986 | 0.1462 | 0.0000 | 0.5271 | 0.0584 | 32 | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p1_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph0p3927` | 10-34 | 0.1023 | 0.0704 | 0.3403 | 0.1435 | 0.0000 | 0.3578 | 0.0705 | 34 | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p55_hrb0p04_hb0p06_h0p03_kb0p06_k0p12_ab0p08_am0p015_ph0p3927` | 0-24 | 0.1020 | 0.1612 | 0.3047 | 0.1497 | 0.0000 | 0.4917 | 0.0916 | 42 | `{'01': 20.0, '11': 80.0}` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph1p5708` | 20-44 | 0.0975 | 0.0771 | 0.4036 | 0.1419 | 0.0000 | 0.5782 | 0.0879 | 22 | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph1p5708` | 15-39 | 0.0956 | 0.0757 | 0.3637 | 0.1419 | 0.0000 | 0.8040 | 0.0765 | 27 | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p1_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph0p3927` | 15-39 | 0.0919 | 0.0433 | 0.3608 | 0.1435 | 0.0000 | 0.3233 | 0.0719 | 29 | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph1p5708` | 10-34 | 0.0918 | 0.0870 | 0.3327 | 0.1419 | 0.0000 | 0.5782 | 0.0745 | 32 | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p85_hrb0_hb0p06_h0p07_kb0p06_k0p04_ab0p04_am0p035_ph1p1781` | 0-24 | 0.0915 | 0.1432 | 0.2561 | 0.1510 | 0.0000 | 0.4243 | 0.0742 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p85_hrb0_hb0p06_h0p07_kb0p06_k0p04_ab0p04_am0p035_ph1p1781` | 5-29 | 0.0911 | 0.0829 | 0.2561 | 0.1510 | 0.0000 | 0.4196 | 0.0708 | None | `{'01': 12.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0p04_hb0p06_h0p03_kb0p06_k0p12_ab0p08_am0p015_ph0p3927` | 0-24 | 0.0894 | 0.2228 | 0.2316 | 0.1494 | 0.0000 | 0.4917 | 0.0905 | None | `{'01': 8.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p1_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph0p3927` | 55-79 | 0.0877 | 0.0596 | 0.4107 | 0.1413 | 0.0000 | 0.3233 | 0.0760 | 23 | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p07_kb0p06_k0p12_ab0p04_am0p021_ph0` | 10-34 | 0.0870 | 0.0755 | 0.3607 | 0.1456 | 0.0000 | 0.7979 | 0.0713 | None | `{'11': 100.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
