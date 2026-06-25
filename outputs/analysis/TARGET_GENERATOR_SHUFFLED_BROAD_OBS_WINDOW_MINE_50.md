# Realized Target Window Mine

status: `PASS_REALIZED_WINDOWS_AVAILABLE`

This mines existing simulated rollout traces for short windows that already
show realized forward motion under actual sim/contact dynamics. It produces
a manifest, not a raw BC dataset.

## Criteria

- window_samples: `50`
- stride_samples: `5`
- min_mean_vx: `0.04`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_action_saturation_pct: `5.0`
- min_done_margin: `50`

## Trace Summary

| source | mode | samples | done_count | mean_vx | max_vx | min_height | candidates |
|---|---|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p015_ph1p1781` | 150 | 0 | 0.0084 | 0.1525 | 0.1486 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p015_ph1p1781` | 150 | 0 | 0.0111 | 0.1345 | 0.1483 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p05_kb0_k0p12_ab0p04_am0p015_ph0p3927` | 150 | 0 | 0.0051 | 0.1485 | 0.1526 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p05_kb0_k0p12_ab0p04_am0p015_ph0p3927` | 150 | 0 | 0.0080 | 0.0939 | 0.1526 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p07_kb0p06_k0p12_ab0p04_am0p021_ph0` | 150 | 0 | 0.0092 | 0.2376 | 0.1437 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p07_kb0p06_k0p12_ab0p04_am0p021_ph0` | 150 | 0 | 0.0108 | 0.1793 | 0.1453 | 1 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p03_kb0p03_k0p04_ab0p04_am0p009_ph0` | 150 | 0 | 0.0050 | 0.0864 | 0.1534 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p03_kb0p03_k0p04_ab0p04_am0p009_ph0` | 150 | 0 | 0.0078 | 0.0940 | 0.1527 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0p04_hb0p04_h0p03_kb0_k0p08_ab0p08_am0p024_ph1p5708` | 150 | 0 | 0.0080 | 0.1336 | 0.1537 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0p04_hb0p04_h0p03_kb0_k0p08_ab0p08_am0p024_ph1p5708` | 150 | 0 | 0.0112 | 0.1209 | 0.1526 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0p04_hb0p04_h0p07_kb0p06_k0p12_ab0p08_am0p056_ph0` | 49 | 1 | 0.3437 | 1.4013 | 0.0175 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0p04_hb0p04_h0p07_kb0p06_k0p12_ab0p08_am0p056_ph0` | 53 | 1 | 0.3235 | 1.3645 | 0.0199 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0p04_hb0p06_h0p03_kb0p06_k0p12_ab0p08_am0p015_ph0p3927` | 67 | 1 | 0.2234 | 1.2067 | 0.0453 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0p04_hb0p06_h0p03_kb0p06_k0p12_ab0p08_am0p015_ph0p3927` | 150 | 0 | 0.0175 | 0.1848 | 0.1453 | 3 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p08_hb0p04_h0p05_kb0_k0p04_ab0_am0p04_ph0p7854` | 150 | 0 | -0.0006 | 0.0741 | 0.1533 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p08_hb0p04_h0p05_kb0_k0p04_ab0_am0p04_ph0p7854` | 150 | 0 | 0.0041 | 0.1154 | 0.1526 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph1p5708` | 68 | 1 | 0.2341 | 1.3411 | 0.0205 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph1p5708` | 67 | 1 | 0.2395 | 1.3255 | 0.0267 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p08_hb0p08_h0p07_kb0p03_k0p12_ab0_am0p021_ph0p7854` | 150 | 0 | -0.0007 | 0.1114 | 0.1473 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p08_hb0p08_h0p07_kb0p03_k0p12_ab0_am0p021_ph0p7854` | 150 | 0 | 0.0028 | 0.0765 | 0.1471 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p12_hb0p04_h0p07_kb0p06_k0p04_ab0p04_am0p056_ph1p5708` | 150 | 0 | 0.0049 | 0.1543 | 0.1423 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p12_hb0p04_h0p07_kb0p06_k0p04_ab0p04_am0p056_ph1p5708` | 150 | 0 | 0.0110 | 0.1031 | 0.1408 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p12_hb0p06_h0p03_kb0p03_k0p08_ab0p04_am0p009_ph0p7854` | 150 | 0 | 0.0025 | 0.0773 | 0.1448 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p12_hb0p06_h0p03_kb0p03_k0p08_ab0p04_am0p009_ph0p7854` | 150 | 0 | 0.0087 | 0.1020 | 0.1447 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p12_hb0p06_h0p03_kb0p06_k0p08_ab0p08_am0p009_ph0p3927` | 150 | 0 | 0.0068 | 0.1892 | 0.1394 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p12_hb0p06_h0p03_kb0p06_k0p08_ab0p08_am0p009_ph0p3927` | 150 | 0 | 0.0130 | 0.1713 | 0.1395 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0_k0p12_ab0p04_am0p015_ph0p7854` | 150 | 0 | 0.0051 | 0.1278 | 0.1523 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0_k0p12_ab0p04_am0p015_ph0p7854` | 150 | 0 | 0.0072 | 0.0832 | 0.1526 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0p04_hb0p04_h0p05_kb0_k0p04_ab0p08_am0p015_ph0p7854` | 150 | 0 | 0.0080 | 0.1652 | 0.1537 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p04_hb0p04_h0p05_kb0_k0p04_ab0p08_am0p015_ph0p7854` | 150 | 0 | 0.0109 | 0.1443 | 0.1526 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p08_hb0p06_h0p07_kb0p06_k0p08_ab0_am0p035_ph1p1781` | 150 | 0 | 0.0047 | 0.1239 | 0.1444 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p08_hb0p06_h0p07_kb0p06_k0p08_ab0_am0p035_ph1p1781` | 150 | 0 | 0.0082 | 0.0959 | 0.1434 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p08_hb0p08_h0p07_kb0p03_k0p12_ab0_am0p021_ph1p5708` | 150 | 0 | 0.0022 | 0.0901 | 0.1467 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p08_hb0p08_h0p07_kb0p03_k0p12_ab0_am0p021_ph1p5708` | 150 | 0 | 0.0042 | 0.0513 | 0.1467 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p12_hb0p08_h0p05_kb0_k0p12_ab0p04_am0p025_ph0` | 150 | 0 | -0.0001 | 0.0447 | 0.1457 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p12_hb0p08_h0p05_kb0_k0p12_ab0p04_am0p025_ph0` | 150 | 0 | 0.0060 | 0.0802 | 0.1457 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p16_hb0p04_h0p03_kb0_k0p08_ab0p04_am0p024_ph0p3927` | 150 | 0 | 0.0017 | 0.0766 | 0.1444 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p16_hb0p04_h0p03_kb0_k0p08_ab0p04_am0p024_ph0p3927` | 150 | 0 | 0.0077 | 0.0836 | 0.1444 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrb0_hb0p04_h0p03_kb0_k0p04_ab0p08_am0p024_ph0` | 150 | 0 | 0.0078 | 0.1360 | 0.1530 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrb0_hb0p04_h0p03_kb0_k0p04_ab0p08_am0p024_ph0` | 150 | 0 | 0.0109 | 0.1490 | 0.1526 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrb0_hb0p06_h0p07_kb0p06_k0p04_ab0p04_am0p035_ph1p1781` | 150 | 0 | 0.0094 | 0.1889 | 0.1473 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrb0_hb0p06_h0p07_kb0p06_k0p04_ab0p04_am0p035_ph1p1781` | 150 | 0 | 0.0109 | 0.1150 | 0.1473 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0_am0p009_ph0p3927` | 150 | 0 | 0.0005 | 0.0347 | 0.1536 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0_am0p009_ph0p3927` | 150 | 0 | 0.0030 | 0.0734 | 0.1527 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrb0p04_hb0p04_h0p05_kb0_k0p04_ab0p04_am0p025_ph0` | 150 | 0 | 0.0059 | 0.0949 | 0.1538 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrb0p04_hb0p04_h0p05_kb0_k0p04_ab0p04_am0p025_ph0` | 150 | 0 | 0.0083 | 0.1066 | 0.1527 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrb0p04_hb0p06_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927` | 150 | 0 | 0.0106 | 0.1584 | 0.1501 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrb0p04_hb0p06_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927` | 150 | 0 | 0.0131 | 0.1321 | 0.1500 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrbm0p04_hb0p06_h0p07_kb0_k0p04_ab0p08_am0p021_ph0p7854` | 150 | 0 | 0.0090 | 0.1739 | 0.1492 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrbm0p04_hb0p06_h0p07_kb0_k0p04_ab0p08_am0p021_ph0p7854` | 150 | 0 | 0.0130 | 0.1349 | 0.1493 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrbm0p08_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p015_ph1p1781` | 150 | 0 | 0.0036 | 0.1170 | 0.1482 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrbm0p08_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p015_ph1p1781` | 150 | 0 | 0.0067 | 0.0815 | 0.1482 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p03_kb0_k0p04_ab0p04_am0p024_ph0p7854` | 150 | 0 | 0.0023 | 0.0396 | 0.1514 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p03_kb0_k0p04_ab0p04_am0p024_ph0p7854` | 150 | 0 | 0.0074 | 0.0829 | 0.1511 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p05_kb0_k0p12_ab0_am0p04_ph1p1781` | 150 | 0 | -0.0022 | 0.0302 | 0.1509 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p05_kb0_k0p12_ab0_am0p04_ph1p1781` | 150 | 0 | 0.0005 | 0.0570 | 0.1507 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p07_kb0p03_k0p08_ab0p08_am0p056_ph0p3927` | 56 | 1 | 0.2732 | 1.2336 | 0.0362 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrbm0p08_hb0p08_h0p07_kb0p03_k0p08_ab0p08_am0p056_ph0p3927` | 106 | 1 | 0.1445 | 1.2372 | 0.0390 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrbm0p12_hb0p08_h0p07_kb0p03_k0p12_ab0_am0p056_ph0` | 150 | 0 | 0.0006 | 0.0729 | 0.1449 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrbm0p12_hb0p08_h0p07_kb0p03_k0p12_ab0_am0p056_ph0` | 150 | 0 | 0.0073 | 0.0763 | 0.1447 | 0 |
| seed_000.jsonl | `primitive_p0p85_hrbm0p16_hb0p08_h0p03_kb0p06_k0p04_ab0p04_am0p009_ph0` | 150 | 0 | 0.0055 | 0.1043 | 0.1400 | 0 |
| seed_002.jsonl | `primitive_p0p85_hrbm0p16_hb0p08_h0p03_kb0p06_k0p04_ab0p04_am0p009_ph0` | 150 | 0 | 0.0106 | 0.0730 | 0.1400 | 0 |
| seed_000.jsonl | `primitive_p1_hrb0_hb0p04_h0p03_kb0p03_k0p04_ab0p08_am0p015_ph1p1781` | 150 | 0 | 0.0081 | 0.1678 | 0.1502 | 0 |
| seed_002.jsonl | `primitive_p1_hrb0_hb0p04_h0p03_kb0p03_k0p04_ab0p08_am0p015_ph1p1781` | 150 | 0 | 0.0107 | 0.1540 | 0.1501 | 0 |
| seed_000.jsonl | `primitive_p1_hrb0_hb0p04_h0p07_kb0p03_k0p04_ab0_am0p035_ph1p1781` | 150 | 0 | 0.0014 | 0.1112 | 0.1510 | 0 |
| seed_002.jsonl | `primitive_p1_hrb0_hb0p04_h0p07_kb0p03_k0p04_ab0_am0p035_ph1p1781` | 150 | 0 | 0.0032 | 0.0963 | 0.1511 | 0 |
| seed_000.jsonl | `primitive_p1_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p024_ph1p5708` | 150 | 0 | 0.0101 | 0.1441 | 0.1472 | 0 |
| seed_002.jsonl | `primitive_p1_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p024_ph1p5708` | 150 | 0 | 0.0124 | 0.0808 | 0.1471 | 0 |
| seed_000.jsonl | `primitive_p1_hrb0p04_hb0p08_h0p05_kb0_k0p04_ab0p04_am0p015_ph0` | 150 | 0 | -0.0026 | 0.0419 | 0.1574 | 0 |
| seed_002.jsonl | `primitive_p1_hrb0p04_hb0p08_h0p05_kb0_k0p04_ab0p04_am0p015_ph0` | 150 | 0 | 0.0047 | 0.1102 | 0.1527 | 0 |
| seed_000.jsonl | `primitive_p1_hrbm0p04_hb0p04_h0p03_kb0p06_k0p08_ab0_am0p015_ph0p3927` | 150 | 0 | 0.0028 | 0.1170 | 0.1472 | 0 |
| seed_002.jsonl | `primitive_p1_hrbm0p04_hb0p04_h0p03_kb0p06_k0p08_ab0_am0p015_ph0p3927` | 150 | 0 | 0.0057 | 0.0759 | 0.1471 | 0 |
| seed_000.jsonl | `primitive_p1_hrbm0p04_hb0p06_h0p03_kb0_k0p08_ab0_am0p009_ph1p1781` | 150 | 0 | -0.0016 | 0.0347 | 0.1537 | 0 |
| seed_002.jsonl | `primitive_p1_hrbm0p04_hb0p06_h0p03_kb0_k0p08_ab0_am0p009_ph1p1781` | 150 | 0 | 0.0014 | 0.0581 | 0.1526 | 0 |
| seed_000.jsonl | `primitive_p1_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph0p3927` | 69 | 1 | 0.2110 | 1.1658 | 0.0424 | 0 |
| seed_002.jsonl | `primitive_p1_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph0p3927` | 103 | 1 | 0.1576 | 1.2872 | 0.0336 | 1 |
| seed_000.jsonl | `primitive_p1_hrbm0p12_hb0p06_h0p03_kb0_k0p12_ab0_am0p024_ph0p7854` | 150 | 0 | -0.0016 | 0.0758 | 0.1488 | 0 |
| seed_002.jsonl | `primitive_p1_hrbm0p12_hb0p06_h0p03_kb0_k0p12_ab0_am0p024_ph0p7854` | 150 | 0 | 0.0027 | 0.0981 | 0.1488 | 0 |
| seed_000.jsonl | `primitive_p1_hrbm0p16_hb0p08_h0p05_kb0p06_k0p04_ab0_am0p04_ph1p5708` | 150 | 0 | -0.0013 | 0.0813 | 0.1405 | 0 |
| seed_002.jsonl | `primitive_p1_hrbm0p16_hb0p08_h0p05_kb0p06_k0p04_ab0_am0p04_ph1p5708` | 150 | 0 | 0.0022 | 0.0837 | 0.1404 | 0 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_002.jsonl | `primitive_p0p55_hrb0p04_hb0p06_h0p03_kb0p06_k0p12_ab0p08_am0p015_ph0p3927` | 0-49 | 0.0595 | 0.1833 | 0.3221 | 0.1468 | 0.0000 | 0.5727 | 0.0814 | None | `{'01': 4.0, '11': 96.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0p04_hb0p06_h0p03_kb0p06_k0p12_ab0p08_am0p015_ph0p3927` | 5-54 | 0.0527 | 0.0642 | 0.3232 | 0.1468 | 0.0000 | 0.6385 | 0.0715 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p07_kb0p06_k0p12_ab0p04_am0p021_ph0` | 0-49 | 0.0462 | 0.1699 | 0.2483 | 0.1465 | 0.0000 | 0.7927 | 0.0794 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0p04_hb0p06_h0p03_kb0p06_k0p12_ab0p08_am0p015_ph0p3927` | 10-59 | 0.0444 | 0.0642 | 0.3240 | 0.1464 | 0.0000 | 0.6456 | 0.0743 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p1_hrbm0p08_hb0p08_h0p05_kb0p03_k0p12_ab0p08_am0p015_ph0p3927` | 0-49 | 0.0401 | 0.1821 | 0.2157 | 0.1456 | 0.0000 | 0.3428 | 0.0738 | 53 | `{'01': 10.0, '11': 90.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
