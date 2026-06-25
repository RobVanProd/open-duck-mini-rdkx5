# Realized Target Window Mine

status: `PASS_REALIZED_WINDOWS_AVAILABLE`

This mines existing simulated rollout traces for short windows that already
show realized forward motion under actual sim/contact dynamics. It produces
a manifest, not a raw BC dataset.

## Criteria

- window_samples: `25`
- stride_samples: `5`
- min_mean_vx: `0.04`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_action_saturation_pct: `5.0`
- min_done_margin: `50`

## Trace Summary

| source | mode | samples | done_count | mean_vx | max_vx | min_height | candidates |
|---|---|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0097 | 0.1409 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0114 | 0.0872 | 0.1466 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0098 | 0.1636 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0113 | 0.1003 | 0.1468 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0085 | 0.1437 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0105 | 0.1092 | 0.1470 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0100 | 0.1690 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0113 | 0.0951 | 0.1471 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0096 | 0.1795 | 0.1458 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0113 | 0.1250 | 0.1465 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0089 | 0.1632 | 0.1470 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0107 | 0.1084 | 0.1467 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0083 | 0.1438 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0100 | 0.1092 | 0.1464 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0087 | 0.1506 | 0.1484 | 3 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0109 | 0.0920 | 0.1481 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0087 | 0.1403 | 0.1484 | 3 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0110 | 0.0907 | 0.1480 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0077 | 0.1568 | 0.1477 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0098 | 0.1005 | 0.1472 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0095 | 0.1523 | 0.1473 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0111 | 0.0971 | 0.1468 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0090 | 0.1609 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0107 | 0.1260 | 0.1472 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0079 | 0.1429 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0098 | 0.1085 | 0.1466 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p3_ls1` | 200 | 0 | 0.0104 | 0.1694 | 0.1457 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p3_ls1` | 200 | 0 | 0.0120 | 0.1247 | 0.1460 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0098 | 0.1507 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0110 | 0.1336 | 0.1457 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0093 | 0.1602 | 0.1476 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0110 | 0.1224 | 0.1470 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0088 | 0.1384 | 0.1473 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p03_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0106 | 0.0815 | 0.1468 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0096 | 0.1407 | 0.1474 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p03_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0118 | 0.0937 | 0.1470 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0085 | 0.1670 | 0.1469 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0105 | 0.0921 | 0.1474 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0088 | 0.1626 | 0.1454 | 5 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0109 | 0.1092 | 0.1463 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0105 | 0.1941 | 0.1455 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0121 | 0.1010 | 0.1451 | 7 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0098 | 0.1921 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0115 | 0.0908 | 0.1460 | 7 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0104 | 0.1549 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0116 | 0.1012 | 0.1470 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0084 | 0.1504 | 0.1474 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0103 | 0.0862 | 0.1470 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0097 | 0.1667 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0119 | 0.1071 | 0.1455 | 6 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0075 | 0.1384 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0092 | 0.1191 | 0.1478 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0100 | 0.1655 | 0.1462 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0116 | 0.1447 | 0.1462 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0095 | 0.1603 | 0.1470 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0111 | 0.1035 | 0.1469 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0083 | 0.1499 | 0.1484 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0104 | 0.0903 | 0.1483 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0083 | 0.1439 | 0.1484 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0103 | 0.0879 | 0.1482 | 6 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0088 | 0.1490 | 0.1484 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0105 | 0.0841 | 0.1483 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0097 | 0.1577 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0111 | 0.0872 | 0.1469 | 6 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0096 | 0.1778 | 0.1461 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0114 | 0.1476 | 0.1464 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0102 | 0.1781 | 0.1454 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0118 | 0.1253 | 0.1459 | 6 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0094 | 0.1599 | 0.1469 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0112 | 0.1336 | 0.1469 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0092 | 0.1398 | 0.1472 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0110 | 0.0857 | 0.1468 | 7 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0064 | 0.1376 | 0.1481 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0087 | 0.1097 | 0.1481 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0090 | 0.1515 | 0.1464 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0113 | 0.1278 | 0.1464 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0081 | 0.1529 | 0.1483 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0100 | 0.0881 | 0.1483 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0092 | 0.1806 | 0.1458 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0114 | 0.1247 | 0.1469 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0091 | 0.1610 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0109 | 0.1141 | 0.1469 | 7 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p03_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0073 | 0.1498 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p03_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0093 | 0.0860 | 0.1472 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0100 | 0.1847 | 0.1453 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0117 | 0.1066 | 0.1462 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0109 | 0.1903 | 0.1449 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0129 | 0.1392 | 0.1461 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0080 | 0.1554 | 0.1471 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0102 | 0.0987 | 0.1472 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0087 | 0.1392 | 0.1480 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0111 | 0.0895 | 0.1479 | 6 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0086 | 0.1369 | 0.1480 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0110 | 0.0898 | 0.1478 | 6 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0081 | 0.1483 | 0.1473 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0095 | 0.1029 | 0.1473 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0091 | 0.1982 | 0.1462 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0101 | 0.1061 | 0.1458 | 5 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0079 | 0.1413 | 0.1475 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0095 | 0.0821 | 0.1474 | 5 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0069 | 0.1525 | 0.1474 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0085 | 0.1219 | 0.1475 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0078 | 0.1680 | 0.1472 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0092 | 0.1046 | 0.1472 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0086 | 0.1670 | 0.1470 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0097 | 0.0865 | 0.1468 | 6 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0079 | 0.1683 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0095 | 0.1231 | 0.1472 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0056 | 0.1359 | 0.1479 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0078 | 0.1129 | 0.1478 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0079 | 0.1353 | 0.1474 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0099 | 0.0880 | 0.1473 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 77 | 1 | 0.1964 | 1.2289 | 0.0448 | 1 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0096 | 0.1153 | 0.1464 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0082 | 0.1527 | 0.1468 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0099 | 0.1107 | 0.1468 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0088 | 0.1769 | 0.1460 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0108 | 0.1324 | 0.1459 | 7 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p3_ls1` | 68 | 1 | 0.2316 | 1.2547 | 0.0368 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p3_ls1` | 200 | 0 | 0.0114 | 0.1332 | 0.1458 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0069 | 0.1546 | 0.1473 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p03_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0090 | 0.0913 | 0.1473 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0066 | 0.1562 | 0.1477 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p03_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0089 | 0.0930 | 0.1477 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0072 | 0.1479 | 0.1481 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0091 | 0.0844 | 0.1481 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0081 | 0.1822 | 0.1450 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0099 | 0.1021 | 0.1461 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0082 | 0.1837 | 0.1451 | 5 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0102 | 0.1387 | 0.1461 | 5 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0090 | 0.1825 | 0.1458 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0108 | 0.1163 | 0.1466 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0053 | 0.1359 | 0.1470 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0077 | 0.1213 | 0.1474 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0074 | 0.1621 | 0.1457 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0096 | 0.1111 | 0.1463 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0068 | 0.1373 | 0.1473 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0089 | 0.0924 | 0.1473 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0064 | 0.1421 | 0.1482 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0085 | 0.0909 | 0.1483 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0058 | 0.1437 | 0.1469 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0082 | 0.0869 | 0.1472 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0060 | 0.1587 | 0.1471 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0083 | 0.1310 | 0.1474 | 4 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 5-29 | 0.1011 | 0.0754 | 0.2900 | 0.1481 | 0.0000 | 0.3767 | 0.0654 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-29 | 0.0999 | 0.1014 | 0.2908 | 0.1488 | 0.0000 | 0.3902 | 0.0715 | None | `{'01': 8.0, '10': 12.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 5-29 | 0.0975 | 0.1151 | 0.2943 | 0.1462 | 0.0000 | 0.4310 | 0.0739 | None | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 5-29 | 0.0975 | 0.1099 | 0.2945 | 0.1476 | 0.0000 | 0.3920 | 0.0686 | None | `{'01': 16.0, '10': 4.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 5-29 | 0.0965 | 0.1117 | 0.2907 | 0.1466 | 0.0000 | 0.4310 | 0.0707 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-29 | 0.0963 | 0.0936 | 0.2928 | 0.1469 | 0.0000 | 0.3777 | 0.0734 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 0-24 | 0.0943 | 0.1853 | 0.2538 | 0.1503 | 0.0000 | 0.4254 | 0.0943 | 52 | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-29 | 0.0941 | 0.0955 | 0.2880 | 0.1472 | 0.0000 | 0.3777 | 0.0741 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 0-24 | 0.0940 | 0.1776 | 0.2487 | 0.1500 | 0.0000 | 0.4457 | 0.0952 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls1` | 5-29 | 0.0928 | 0.0958 | 0.2738 | 0.1488 | 0.0000 | 0.3875 | 0.0681 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 5-29 | 0.0928 | 0.0778 | 0.2791 | 0.1489 | 0.0000 | 0.2680 | 0.0682 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0928 | 0.0879 | 0.3115 | 0.1461 | 0.0000 | 0.6601 | 0.0626 | None | `{'01': 16.0, '10': 12.0, '11': 72.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls1` | 5-29 | 0.0919 | 0.1030 | 0.2796 | 0.1479 | 0.0000 | 0.3760 | 0.0729 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 0-24 | 0.0915 | 0.1922 | 0.2429 | 0.1511 | 0.0000 | 0.3789 | 0.0899 | None | `{'01': 16.0, '10': 12.0, '11': 72.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p3_ls1` | 5-29 | 0.0914 | 0.1081 | 0.2957 | 0.1468 | 0.0000 | 0.5173 | 0.0751 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-29 | 0.0912 | 0.0957 | 0.3042 | 0.1471 | 0.0000 | 0.5769 | 0.0739 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 5-29 | 0.0912 | 0.0953 | 0.2694 | 0.1488 | 0.0000 | 0.2940 | 0.0658 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 0-24 | 0.0895 | 0.1954 | 0.2313 | 0.1503 | 0.0000 | 0.4296 | 0.0952 | None | `{'01': 32.0, '11': 68.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 0-24 | 0.0893 | 0.1962 | 0.2441 | 0.1505 | 0.0000 | 0.3837 | 0.0891 | None | `{'01': 24.0, '10': 4.0, '11': 72.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 0-24 | 0.0892 | 0.2055 | 0.2332 | 0.1508 | 0.0000 | 0.3676 | 0.0933 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 0-24 | 0.0891 | 0.1855 | 0.2586 | 0.1479 | 0.0000 | 0.4802 | 0.1002 | None | `{'01': 24.0, '10': 12.0, '11': 64.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 0-24 | 0.0889 | 0.1933 | 0.2310 | 0.1505 | 0.0000 | 0.4293 | 0.0963 | None | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 5-29 | 0.0886 | 0.0925 | 0.2718 | 0.1476 | 0.0000 | 0.3777 | 0.0714 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 5-29 | 0.0881 | 0.1058 | 0.3007 | 0.1467 | 0.0000 | 0.4794 | 0.0765 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 0-24 | 0.0878 | 0.1888 | 0.2309 | 0.1508 | 0.0000 | 0.3676 | 0.0950 | None | `{'01': 20.0, '11': 80.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
