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
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0074 | 0.1235 | 0.1507 | 3 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 150 | 0 | 0.0080 | 0.1150 | 0.1507 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854` | 150 | 0 | 0.0085 | 0.0826 | 0.1507 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781` | 150 | 0 | 0.0093 | 0.0803 | 0.1506 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0098 | 0.0782 | 0.1503 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0080 | 0.1117 | 0.1486 | 3 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 150 | 0 | 0.0082 | 0.0863 | 0.1486 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854` | 150 | 0 | 0.0094 | 0.0827 | 0.1486 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781` | 150 | 0 | 0.0102 | 0.0780 | 0.1484 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0108 | 0.0782 | 0.1483 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0075 | 0.1424 | 0.1459 | 3 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 150 | 0 | 0.0080 | 0.1111 | 0.1459 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854` | 150 | 0 | 0.0091 | 0.1073 | 0.1459 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781` | 150 | 0 | 0.0098 | 0.0957 | 0.1457 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0100 | 0.1029 | 0.1457 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0084 | 0.0945 | 0.1433 | 3 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 150 | 0 | 0.0081 | 0.1135 | 0.1433 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854` | 150 | 0 | 0.0089 | 0.1083 | 0.1432 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781` | 150 | 0 | 0.0105 | 0.0852 | 0.1431 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0110 | 0.0821 | 0.1431 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p16_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0081 | 0.0935 | 0.1406 | 3 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p16_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 150 | 0 | 0.0092 | 0.0873 | 0.1405 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p16_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854` | 150 | 0 | 0.0092 | 0.1094 | 0.1404 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p16_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781` | 150 | 0 | 0.0103 | 0.0799 | 0.1404 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p16_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0100 | 0.1128 | 0.1404 | 1 |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0092 | 0.1226 | 0.1498 | 3 |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 150 | 0 | 0.0104 | 0.1282 | 0.1497 | 3 |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854` | 150 | 0 | 0.0110 | 0.0873 | 0.1497 | 1 |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781` | 150 | 0 | 0.0116 | 0.0822 | 0.1497 | 1 |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0116 | 0.0826 | 0.1497 | 1 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0097 | 0.1133 | 0.1477 | 3 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 150 | 0 | 0.0107 | 0.1004 | 0.1477 | 3 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854` | 150 | 0 | 0.0119 | 0.0848 | 0.1476 | 2 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781` | 150 | 0 | 0.0123 | 0.0842 | 0.1476 | 1 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0123 | 0.0841 | 0.1475 | 1 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0104 | 0.1265 | 0.1449 | 3 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 150 | 0 | 0.0106 | 0.1183 | 0.1445 | 3 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854` | 150 | 0 | 0.0111 | 0.1231 | 0.1445 | 2 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781` | 150 | 0 | 0.0108 | 0.1037 | 0.1445 | 1 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0106 | 0.0945 | 0.1445 | 1 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0099 | 0.1195 | 0.1424 | 2 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 150 | 0 | 0.0101 | 0.1154 | 0.1423 | 2 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854` | 150 | 0 | 0.0103 | 0.1115 | 0.1423 | 1 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781` | 150 | 0 | 0.0113 | 0.0829 | 0.1423 | 2 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0108 | 0.0799 | 0.1423 | 2 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p16_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0102 | 0.0887 | 0.1399 | 3 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p16_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 150 | 0 | 0.0107 | 0.0928 | 0.1396 | 3 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p16_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854` | 150 | 0 | 0.0102 | 0.1137 | 0.1397 | 2 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p16_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p1781` | 150 | 0 | 0.0107 | 0.0835 | 0.1397 | 2 |
| seed_002.jsonl | `primitive_p0p9_hrbm0p16_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0100 | 0.0725 | 0.1397 | 2 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_002.jsonl | `primitive_p0p9_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0729 | 0.1879 | 0.1912 | 0.1486 | 0.0000 | 0.3460 | 0.0875 | None | `{'01': 12.0, '10': 16.0, '11': 72.0}` |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 0-24 | 0.0701 | 0.1915 | 0.1694 | 0.1526 | 0.0000 | 0.3471 | 0.0837 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p9_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0692 | 0.1698 | 0.1910 | 0.1454 | 0.0000 | 0.3481 | 0.0881 | None | `{'01': 12.0, '10': 16.0, '11': 72.0}` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0689 | 0.1862 | 0.1549 | 0.1491 | 0.0000 | 0.4466 | 0.0878 | None | `{'01': 12.0, '10': 16.0, '11': 72.0}` |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0648 | 0.2028 | 0.1614 | 0.1527 | 0.0000 | 0.3460 | 0.0866 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0646 | 0.2010 | 0.1341 | 0.1527 | 0.0000 | 0.4466 | 0.0880 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0644 | 0.1824 | 0.1536 | 0.1524 | 0.0000 | 0.3460 | 0.0844 | None | `{'01': 12.0, '10': 8.0, '11': 80.0}` |
| seed_002.jsonl | `primitive_p0p9_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0638 | 0.1473 | 0.1926 | 0.1486 | 0.0000 | 0.3454 | 0.0627 | None | `{'10': 8.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0622 | 0.1831 | 0.1226 | 0.1526 | 0.0000 | 0.4466 | 0.0866 | None | `{'01': 12.0, '10': 8.0, '11': 80.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 0-24 | 0.0618 | 0.1876 | 0.1283 | 0.1526 | 0.0000 | 0.4394 | 0.0838 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0611 | 0.0349 | 0.1679 | 0.1534 | 0.0000 | 0.3454 | 0.0549 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p9_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p7854` | 0-24 | 0.0611 | 0.1765 | 0.1429 | 0.1494 | 0.0000 | 0.3475 | 0.0846 | None | `{'01': 12.0, '10': 16.0, '11': 72.0}` |
| seed_002.jsonl | `primitive_p0p9_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 0-24 | 0.0609 | 0.1781 | 0.1486 | 0.1499 | 0.0000 | 0.3471 | 0.0841 | None | `{'01': 12.0, '10': 12.0, '11': 76.0}` |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 5-29 | 0.0606 | 0.0988 | 0.1708 | 0.1534 | 0.0000 | 0.3446 | 0.0604 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0606 | 0.0369 | 0.1606 | 0.1517 | 0.0000 | 0.3454 | 0.0529 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p9_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 0-24 | 0.0600 | 0.1768 | 0.1613 | 0.1462 | 0.0000 | 0.3502 | 0.0876 | None | `{'01': 12.0, '10': 16.0, '11': 72.0}` |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0589 | 0.0936 | 0.1606 | 0.1524 | 0.0000 | 0.3454 | 0.0537 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p9_hrbm0p04_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 0-24 | 0.0581 | 0.1862 | 0.1307 | 0.1526 | 0.0000 | 0.3471 | 0.0828 | None | `{'01': 12.0, '10': 8.0, '11': 80.0}` |
| seed_002.jsonl | `primitive_p0p9_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0580 | 0.1055 | 0.1679 | 0.1539 | 0.0000 | 0.3454 | 0.0555 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p9_hrbm0p16_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0573 | 0.1862 | 0.1373 | 0.1461 | 0.0000 | 0.3481 | 0.0971 | None | `{'01': 12.0, '10': 4.0, '11': 84.0}` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0572 | 0.2055 | 0.1047 | 0.1490 | 0.0000 | 0.4474 | 0.0880 | None | `{'01': 12.0, '10': 4.0, '11': 84.0}` |
| seed_002.jsonl | `primitive_p0p9_hrbm0p12_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0570 | 0.1240 | 0.1910 | 0.1454 | 0.0000 | 0.3454 | 0.0655 | None | `{'10': 8.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p9_hrbm0p16_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 0-24 | 0.0563 | 0.2213 | 0.1275 | 0.1463 | 0.0000 | 0.3502 | 0.1002 | None | `{'01': 12.0, '10': 4.0, '11': 84.0}` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0562 | 0.1442 | 0.1553 | 0.1488 | 0.0000 | 0.4196 | 0.0608 | None | `{'10': 8.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p08_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0p3927` | 0-24 | 0.0555 | 0.1761 | 0.1142 | 0.1503 | 0.0000 | 0.4394 | 0.0886 | None | `{'01': 12.0, '10': 12.0, '11': 76.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
