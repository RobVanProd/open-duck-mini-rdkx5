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
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0097 | 0.1409 | 0.1471 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0114 | 0.0872 | 0.1466 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0098 | 0.1636 | 0.1471 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0113 | 0.1003 | 0.1468 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0085 | 0.1437 | 0.1471 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0105 | 0.1092 | 0.1470 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0100 | 0.1690 | 0.1475 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0113 | 0.0951 | 0.1471 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0096 | 0.1795 | 0.1458 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0113 | 0.1250 | 0.1465 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0089 | 0.1632 | 0.1470 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0107 | 0.1084 | 0.1467 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0083 | 0.1438 | 0.1472 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0100 | 0.1092 | 0.1464 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0087 | 0.1506 | 0.1484 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0109 | 0.0920 | 0.1481 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0087 | 0.1403 | 0.1484 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0110 | 0.0907 | 0.1480 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0077 | 0.1568 | 0.1477 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0098 | 0.1005 | 0.1472 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0095 | 0.1523 | 0.1473 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0111 | 0.0971 | 0.1468 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0090 | 0.1609 | 0.1471 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0107 | 0.1260 | 0.1472 | 2 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0079 | 0.1429 | 0.1472 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0098 | 0.1085 | 0.1466 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p3_ls1` | 200 | 0 | 0.0104 | 0.1694 | 0.1457 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p3_ls1` | 200 | 0 | 0.0120 | 0.1247 | 0.1460 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0098 | 0.1507 | 0.1471 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0110 | 0.1336 | 0.1457 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0093 | 0.1602 | 0.1476 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0110 | 0.1224 | 0.1470 | 4 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0088 | 0.1384 | 0.1473 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p03_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0106 | 0.0815 | 0.1468 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0096 | 0.1407 | 0.1474 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p03_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0118 | 0.0937 | 0.1470 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0085 | 0.1670 | 0.1469 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0105 | 0.0921 | 0.1474 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0088 | 0.1626 | 0.1454 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0109 | 0.1092 | 0.1463 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0105 | 0.1941 | 0.1455 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0121 | 0.1010 | 0.1451 | 4 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0098 | 0.1921 | 0.1464 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0115 | 0.0908 | 0.1460 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0104 | 0.1549 | 0.1478 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0116 | 0.1012 | 0.1470 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0084 | 0.1504 | 0.1474 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0103 | 0.0862 | 0.1470 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0097 | 0.1667 | 0.1464 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0119 | 0.1071 | 0.1455 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0075 | 0.1384 | 0.1478 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0092 | 0.1191 | 0.1478 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0100 | 0.1655 | 0.1462 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0116 | 0.1447 | 0.1462 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0095 | 0.1603 | 0.1470 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0111 | 0.1035 | 0.1469 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0083 | 0.1499 | 0.1484 | 1 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0104 | 0.0903 | 0.1483 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0083 | 0.1439 | 0.1484 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0103 | 0.0879 | 0.1482 | 2 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0088 | 0.1490 | 0.1484 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0105 | 0.0841 | 0.1483 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0097 | 0.1577 | 0.1471 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0111 | 0.0872 | 0.1469 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0096 | 0.1778 | 0.1461 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0114 | 0.1476 | 0.1464 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0102 | 0.1781 | 0.1454 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0118 | 0.1253 | 0.1459 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0094 | 0.1599 | 0.1469 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0112 | 0.1336 | 0.1469 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0092 | 0.1398 | 0.1472 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0110 | 0.0857 | 0.1468 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0064 | 0.1376 | 0.1481 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0087 | 0.1097 | 0.1481 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0090 | 0.1515 | 0.1464 | 1 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0113 | 0.1278 | 0.1464 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0081 | 0.1529 | 0.1483 | 1 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0100 | 0.0881 | 0.1483 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0092 | 0.1806 | 0.1458 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0114 | 0.1247 | 0.1469 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0091 | 0.1610 | 0.1472 | 1 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0109 | 0.1141 | 0.1469 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p03_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0073 | 0.1498 | 0.1472 | 1 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p03_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0093 | 0.0860 | 0.1472 | 2 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0100 | 0.1847 | 0.1453 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0117 | 0.1066 | 0.1462 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0109 | 0.1903 | 0.1449 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0129 | 0.1392 | 0.1461 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0080 | 0.1554 | 0.1471 | 1 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0102 | 0.0987 | 0.1472 | 2 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0087 | 0.1392 | 0.1480 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0111 | 0.0895 | 0.1479 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0086 | 0.1369 | 0.1480 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0110 | 0.0898 | 0.1478 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0081 | 0.1483 | 0.1473 | 2 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0095 | 0.1029 | 0.1473 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0091 | 0.1982 | 0.1462 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0101 | 0.1061 | 0.1458 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0079 | 0.1413 | 0.1475 | 2 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p01_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0095 | 0.0821 | 0.1474 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0069 | 0.1525 | 0.1474 | 1 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0085 | 0.1219 | 0.1475 | 1 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0078 | 0.1680 | 0.1472 | 2 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0092 | 0.1046 | 0.1472 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0086 | 0.1670 | 0.1470 | 2 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0097 | 0.0865 | 0.1468 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0079 | 0.1683 | 0.1472 | 2 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0095 | 0.1231 | 0.1472 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0056 | 0.1359 | 0.1479 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0078 | 0.1129 | 0.1478 | 0 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0079 | 0.1353 | 0.1474 | 1 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p02_hrphm1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0099 | 0.0880 | 0.1473 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 77 | 1 | 0.1964 | 1.2289 | 0.0448 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0096 | 0.1153 | 0.1464 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0082 | 0.1527 | 0.1468 | 2 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0099 | 0.1107 | 0.1468 | 1 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0088 | 0.1769 | 0.1460 | 2 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0108 | 0.1324 | 0.1459 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p3_ls1` | 68 | 1 | 0.2316 | 1.2547 | 0.0368 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p03_hrph1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p3_ls1` | 200 | 0 | 0.0114 | 0.1332 | 0.1458 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0069 | 0.1546 | 0.1473 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p03_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0090 | 0.0913 | 0.1473 | 0 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p03_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0066 | 0.1562 | 0.1477 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p03_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0089 | 0.0930 | 0.1477 | 0 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0072 | 0.1479 | 0.1481 | 1 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0091 | 0.0844 | 0.1481 | 1 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0081 | 0.1822 | 0.1450 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0099 | 0.1021 | 0.1461 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0082 | 0.1837 | 0.1451 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0102 | 0.1387 | 0.1461 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0090 | 0.1825 | 0.1458 | 2 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0108 | 0.1163 | 0.1466 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0053 | 0.1359 | 0.1470 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0077 | 0.1213 | 0.1474 | 1 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0074 | 0.1621 | 0.1457 | 2 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0096 | 0.1111 | 0.1463 | 1 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0068 | 0.1373 | 0.1473 | 1 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0089 | 0.0924 | 0.1473 | 2 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0064 | 0.1421 | 0.1482 | 1 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0085 | 0.0909 | 0.1483 | 1 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0058 | 0.1437 | 0.1469 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0082 | 0.0869 | 0.1472 | 1 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0060 | 0.1587 | 0.1471 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0083 | 0.1310 | 0.1474 | 1 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 0-49 | 0.0559 | 0.1834 | 0.2879 | 0.1471 | 0.0000 | 0.5347 | 0.0866 | None | `{'01': 4.0, '11': 96.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 0-49 | 0.0556 | 0.1379 | 0.3448 | 0.1454 | 0.0000 | 0.3775 | 0.0813 | None | `{'01': 10.0, '11': 90.0}` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 0-49 | 0.0555 | 0.1947 | 0.2796 | 0.1467 | 0.0000 | 0.4305 | 0.0840 | None | `{'01': 4.0, '11': 96.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p3_ls1` | 0-49 | 0.0549 | 0.1964 | 0.2708 | 0.1468 | 0.0000 | 0.4215 | 0.0882 | None | `{'01': 4.0, '11': 96.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 0-49 | 0.0543 | 0.1127 | 0.3289 | 0.1462 | 0.0000 | 0.5142 | 0.0741 | None | `{'01': 10.0, '11': 90.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p32_ld0p3_ls0p65` | 0-49 | 0.0543 | 0.1918 | 0.2745 | 0.1472 | 0.0000 | 0.5893 | 0.0819 | None | `{'01': 6.0, '10': 2.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 5-54 | 0.0543 | 0.0746 | 0.3289 | 0.1462 | 0.0000 | 0.4952 | 0.0656 | None | `{'01': 6.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls0p65` | 0-49 | 0.0535 | 0.1804 | 0.2781 | 0.1477 | 0.0000 | 0.4821 | 0.0844 | None | `{'01': 4.0, '11': 96.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph1p5708_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p005_ph0p32_ld0p22_ls0p65` | 0-49 | 0.0532 | 0.1811 | 0.2819 | 0.1479 | 0.0000 | 0.4757 | 0.0838 | None | `{'01': 6.0, '11': 94.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p3_ls1` | 0-49 | 0.0530 | 0.1421 | 0.3275 | 0.1457 | 0.0000 | 0.4215 | 0.0863 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 5-54 | 0.0529 | 0.0933 | 0.3448 | 0.1454 | 0.0000 | 0.3767 | 0.0749 | None | `{'01': 6.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p03_hrphm1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p3_ls0p65` | 0-49 | 0.0528 | 0.1658 | 0.2685 | 0.1481 | 0.0000 | 0.5386 | 0.0829 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 0-49 | 0.0527 | 0.2088 | 0.2614 | 0.1484 | 0.0000 | 0.3575 | 0.0882 | None | `{'01': 10.0, '10': 4.0, '11': 86.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls1` | 10-59 | 0.0525 | 0.0671 | 0.3300 | 0.1461 | 0.0000 | 0.3575 | 0.0771 | None | `{'01': 2.0, '11': 98.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 0-49 | 0.0521 | 0.1309 | 0.3431 | 0.1458 | 0.0000 | 0.5347 | 0.0810 | None | `{'01': 12.0, '10': 6.0, '11': 82.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls1` | 0-49 | 0.0518 | 0.1387 | 0.3425 | 0.1458 | 0.0000 | 0.3698 | 0.0826 | None | `{'01': 10.0, '11': 90.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 0-49 | 0.0518 | 0.1293 | 0.3352 | 0.1461 | 0.0000 | 0.3775 | 0.0811 | None | `{'01': 10.0, '11': 90.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 0-49 | 0.0517 | 0.1889 | 0.2502 | 0.1473 | 0.0000 | 0.4217 | 0.0855 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p01_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p3_ls1` | 0-49 | 0.0516 | 0.1911 | 0.2579 | 0.1472 | 0.0000 | 0.3775 | 0.0834 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p03_hrph1p5708_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p47_ld0p22_ls1` | 0-49 | 0.0516 | 0.1860 | 0.2481 | 0.1487 | 0.0000 | 0.3964 | 0.0803 | None | `{'01': 6.0, '10': 4.0, '11': 90.0}` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p03_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p32_ld0p22_ls1` | 0-49 | 0.0515 | 0.1799 | 0.2651 | 0.1477 | 0.0000 | 0.3698 | 0.0859 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p64_hrb0_hra0p04_hrph0p7854_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 0-49 | 0.0514 | 0.1906 | 0.2781 | 0.1470 | 0.0000 | 0.3920 | 0.0775 | None | `{'01': 4.0, '11': 96.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls1` | 0-49 | 0.0511 | 0.1799 | 0.2542 | 0.1472 | 0.0000 | 0.4778 | 0.0899 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p02_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 0-49 | 0.0511 | 0.1881 | 0.2672 | 0.1470 | 0.0000 | 0.3775 | 0.0837 | None | `{'01': 4.0, '11': 96.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p01_hrph0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p005_ph0p3927_ld0p22_ls0p65` | 0-49 | 0.0510 | 0.1624 | 0.2727 | 0.1480 | 0.0000 | 0.4680 | 0.0819 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
