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
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p3927_ld0p38_ls1` | 200 | 0 | 0.0088 | 0.1628 | 0.1467 | 3 |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p3927_ld0p38_ls1` | 200 | 0 | 0.0106 | 0.1266 | 0.1467 | 4 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47_ld0p3_ls0p35` | 136 | 1 | 0.1172 | 1.2765 | 0.0283 | 4 |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47_ld0p3_ls0p35` | 103 | 1 | 0.1552 | 1.2768 | 0.0324 | 6 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_am0p014_ph0p47_ld0p38_ls0p65` | 65 | 1 | 0.2313 | 1.2269 | 0.0455 | 0 |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_am0p014_ph0p47_ld0p38_ls0p65` | 200 | 0 | 0.0127 | 0.1346 | 0.1446 | 6 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927_ld0p3_ls0p35` | 200 | 0 | 0.0085 | 0.1456 | 0.1473 | 4 |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927_ld0p3_ls0p35` | 200 | 0 | 0.0098 | 0.0995 | 0.1468 | 7 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p38_ls1` | 200 | 0 | 0.0091 | 0.1645 | 0.1465 | 4 |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p38_ls1` | 200 | 0 | 0.0108 | 0.1062 | 0.1463 | 5 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0105 | 0.1562 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_a0_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0124 | 0.1267 | 0.1472 | 4 |
| seed_000.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p0075_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0110 | 0.1809 | 0.1469 | 4 |
| seed_002.jsonl | `primitive_p0p56_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p0075_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0126 | 0.1103 | 0.1469 | 5 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p54_ld0p22_ls1` | 200 | 0 | 0.0068 | 0.1344 | 0.1491 | 3 |
| seed_002.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p54_ld0p22_ls1` | 200 | 0 | 0.0087 | 0.0976 | 0.1490 | 4 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_a0_ph0p54_ld0p3_ls1` | 106 | 1 | 0.1513 | 1.2846 | 0.0291 | 3 |
| seed_002.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_a0_ph0p54_ld0p3_ls1` | 200 | 0 | 0.0126 | 0.1333 | 0.1460 | 5 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p38_ls0p35` | 200 | 0 | 0.0094 | 0.1532 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p38_ls0p35` | 200 | 0 | 0.0108 | 0.0979 | 0.1458 | 7 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p00875_ph0p32_ld0p38_ls0p35` | 146 | 1 | 0.1112 | 1.2959 | 0.0290 | 4 |
| seed_002.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p00875_ph0p32_ld0p38_ls0p35` | 125 | 1 | 0.1275 | 1.2483 | 0.0354 | 8 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p06_am0p014_ph0p47_ld0p3_ls0p35` | 76 | 1 | 0.2132 | 1.3125 | 0.0251 | 1 |
| seed_002.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p06_am0p014_ph0p47_ld0p3_ls0p35` | 91 | 1 | 0.1786 | 1.2998 | 0.0320 | 4 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p0035_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0061 | 0.1313 | 0.1497 | 3 |
| seed_002.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p0035_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0080 | 0.1002 | 0.1497 | 4 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927_ld0p3_ls0p35` | 200 | 0 | 0.0082 | 0.1574 | 0.1482 | 3 |
| seed_002.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927_ld0p3_ls0p35` | 200 | 0 | 0.0096 | 0.0863 | 0.1481 | 7 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p54_ld0p22_ls0p35` | 200 | 0 | 0.0109 | 0.1748 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p54_ld0p22_ls0p35` | 200 | 0 | 0.0126 | 0.1044 | 0.1464 | 7 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p3927_ld0p38_ls0p65` | 200 | 0 | 0.0110 | 0.1920 | 0.1458 | 4 |
| seed_002.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p3927_ld0p38_ls0p65` | 200 | 0 | 0.0129 | 0.1230 | 0.1458 | 5 |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p003_ph0p54_ld0p3_ls0p65` | 200 | 0 | 0.0083 | 0.1505 | 0.1479 | 4 |
| seed_002.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p003_ph0p54_ld0p3_ls0p65` | 200 | 0 | 0.0099 | 0.0957 | 0.1476 | 5 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_a0_ph0p47_ld0p3_ls1` | 70 | 1 | 0.2172 | 1.2592 | 0.0425 | 0 |
| seed_002.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0128 | 0.1422 | 0.1451 | 5 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p00875_ph0p47_ld0p22_ls0p35` | 200 | 0 | 0.0082 | 0.1566 | 0.1473 | 3 |
| seed_002.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p00875_ph0p47_ld0p22_ls0p35` | 200 | 0 | 0.0101 | 0.0939 | 0.1471 | 7 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p3927_ld0p22_ls0p35` | 200 | 0 | 0.0111 | 0.1888 | 0.1441 | 4 |
| seed_002.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p3927_ld0p22_ls0p35` | 88 | 1 | 0.1781 | 1.2400 | 0.0417 | 3 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0082 | 0.1510 | 0.1478 | 3 |
| seed_002.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0101 | 0.0868 | 0.1476 | 6 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p0035_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0079 | 0.1579 | 0.1469 | 3 |
| seed_002.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p0035_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0100 | 0.1091 | 0.1464 | 7 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p0075_ph0p32_ld0p38_ls0p65` | 200 | 0 | 0.0086 | 0.1511 | 0.1473 | 3 |
| seed_002.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p0075_ph0p32_ld0p38_ls0p65` | 200 | 0 | 0.0104 | 0.0819 | 0.1469 | 5 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p0075_ph0p54_ld0p22_ls0p35` | 200 | 0 | 0.0081 | 0.1471 | 0.1471 | 3 |
| seed_002.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p0075_ph0p54_ld0p22_ls0p35` | 200 | 0 | 0.0101 | 0.0940 | 0.1469 | 7 |
| seed_000.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p38_ls0p65` | 200 | 0 | 0.0092 | 0.1642 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p56_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p38_ls0p65` | 200 | 0 | 0.0107 | 0.0916 | 0.1455 | 6 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p3927_ld0p22_ls0p35` | 200 | 0 | 0.0083 | 0.1389 | 0.1469 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p3927_ld0p22_ls0p35` | 200 | 0 | 0.0098 | 0.0835 | 0.1467 | 7 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p01_ph0p47_ld0p38_ls0p35` | 200 | 0 | 0.0087 | 0.1531 | 0.1470 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p01_ph0p47_ld0p38_ls0p35` | 200 | 0 | 0.0101 | 0.0839 | 0.1469 | 7 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p0025_ph0p47_ld0p38_ls0p35` | 96 | 1 | 0.1634 | 1.2804 | 0.0347 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p0025_ph0p47_ld0p38_ls0p35` | 93 | 1 | 0.1753 | 1.3098 | 0.0279 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p54_ld0p38_ls1` | 200 | 0 | 0.0080 | 0.1795 | 0.1461 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p54_ld0p38_ls1` | 200 | 0 | 0.0096 | 0.1301 | 0.1466 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p0035_ph0p47_ld0p3_ls0p35` | 200 | 0 | 0.0090 | 0.1628 | 0.1466 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p0035_ph0p47_ld0p3_ls0p35` | 200 | 0 | 0.0103 | 0.1067 | 0.1448 | 9 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_a0_ph0p54_ld0p22_ls1` | 200 | 0 | 0.0100 | 0.1566 | 0.1470 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_a0_ph0p54_ld0p22_ls1` | 200 | 0 | 0.0121 | 0.1364 | 0.1470 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p32_ld0p38_ls0p35` | 200 | 0 | 0.0082 | 0.1500 | 0.1472 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p32_ld0p38_ls0p35` | 200 | 0 | 0.0098 | 0.0901 | 0.1471 | 5 |
| seed_000.jsonl | `primitive_p0p64_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p014_ph0p32_ld0p38_ls0p65` | 59 | 1 | 0.2697 | 1.3121 | 0.0306 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p014_ph0p32_ld0p38_ls0p65` | 200 | 0 | 0.0125 | 0.1531 | 0.1459 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p0075_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0079 | 0.1543 | 0.1486 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p0075_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0093 | 0.0973 | 0.1486 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p00625_ph0p54_ld0p22_ls0p35` | 200 | 0 | 0.0084 | 0.1487 | 0.1468 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p00625_ph0p54_ld0p22_ls0p35` | 200 | 0 | 0.0102 | 0.0885 | 0.1467 | 7 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0068 | 0.1443 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0089 | 0.0925 | 0.1472 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p00625_ph0p54_ld0p22_ls1` | 200 | 0 | 0.0097 | 0.1689 | 0.1455 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p00625_ph0p54_ld0p22_ls1` | 200 | 0 | 0.0119 | 0.0950 | 0.1456 | 5 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p01_ph0p32_ld0p3_ls1` | 200 | 0 | 0.0069 | 0.1383 | 0.1480 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p01_ph0p32_ld0p3_ls1` | 200 | 0 | 0.0087 | 0.0905 | 0.1478 | 5 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p01_ph0p54_ld0p38_ls1` | 200 | 0 | 0.0072 | 0.1411 | 0.1474 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p01_ph0p54_ld0p38_ls1` | 200 | 0 | 0.0091 | 0.0871 | 0.1469 | 5 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p54_ld0p22_ls1` | 200 | 0 | 0.0067 | 0.1451 | 0.1480 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p54_ld0p22_ls1` | 200 | 0 | 0.0088 | 0.1103 | 0.1480 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p00875_ph0p54_ld0p22_ls0p65` | 200 | 0 | 0.0076 | 0.1470 | 0.1483 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p00875_ph0p54_ld0p22_ls0p65` | 200 | 0 | 0.0096 | 0.0883 | 0.1483 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_a0_ph0p54_ld0p3_ls0p35` | 103 | 1 | 0.1530 | 1.2782 | 0.0345 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_a0_ph0p54_ld0p3_ls0p35` | 92 | 1 | 0.1777 | 1.3080 | 0.0277 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p54_ld0p22_ls0p65` | 200 | 0 | 0.0081 | 0.1533 | 0.1477 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p54_ld0p22_ls0p65` | 200 | 0 | 0.0101 | 0.0841 | 0.1476 | 5 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p54_ld0p22_ls0p35` | 200 | 0 | 0.0087 | 0.1639 | 0.1465 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p54_ld0p22_ls0p35` | 200 | 0 | 0.0106 | 0.1111 | 0.1460 | 8 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p014_ph0p3927_ld0p38_ls0p35` | 73 | 1 | 0.2200 | 1.2857 | 0.0316 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p014_ph0p3927_ld0p38_ls0p35` | 200 | 0 | 0.0126 | 0.0857 | 0.1455 | 8 |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0071 | 0.1428 | 0.1476 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0091 | 0.0872 | 0.1475 | 4 |
| seed_000.jsonl | `primitive_p0p68_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p3927_ld0p38_ls1` | 58 | 1 | 0.2779 | 1.2931 | 0.0252 | 0 |
| seed_002.jsonl | `primitive_p0p68_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p3927_ld0p38_ls1` | 200 | 0 | 0.0135 | 0.1606 | 0.1455 | 5 |
| seed_000.jsonl | `primitive_p0p68_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p38_ls0p65` | 200 | 0 | 0.0106 | 0.1694 | 0.1461 | 4 |
| seed_002.jsonl | `primitive_p0p68_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p38_ls0p65` | 200 | 0 | 0.0119 | 0.1106 | 0.1465 | 4 |
| seed_000.jsonl | `primitive_p0p68_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p32_ld0p38_ls0p35` | 200 | 0 | 0.0105 | 0.1679 | 0.1471 | 3 |
| seed_002.jsonl | `primitive_p0p68_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p32_ld0p38_ls0p35` | 200 | 0 | 0.0121 | 0.1003 | 0.1471 | 5 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p54_ld0p3_ls1` | 200 | 0 | 0.0084 | 0.1518 | 0.1476 | 4 |
| seed_002.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p54_ld0p3_ls1` | 200 | 0 | 0.0104 | 0.1186 | 0.1477 | 4 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_a0_ph0p32_ld0p38_ls0p65` | 62 | 1 | 0.2625 | 1.3129 | 0.0244 | 0 |
| seed_002.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_a0_ph0p32_ld0p38_ls0p65` | 200 | 0 | 0.0140 | 0.1383 | 0.1458 | 4 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p54_ld0p38_ls0p35` | 90 | 1 | 0.1812 | 1.3033 | 0.0235 | 3 |
| seed_002.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p54_ld0p38_ls0p35` | 127 | 1 | 0.1274 | 1.2967 | 0.0298 | 8 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_a0_ph0p54_ld0p22_ls0p35` | 200 | 0 | 0.0092 | 0.1349 | 0.1480 | 3 |
| seed_002.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_a0_ph0p54_ld0p22_ls0p35` | 200 | 0 | 0.0108 | 0.0797 | 0.1479 | 5 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p0025_ph0p32_ld0p3_ls0p65` | 107 | 1 | 0.1478 | 1.2722 | 0.0350 | 3 |
| seed_002.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p0025_ph0p32_ld0p3_ls0p65` | 200 | 0 | 0.0137 | 0.1293 | 0.1468 | 4 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_a0_ph0p54_ld0p22_ls0p35` | 120 | 1 | 0.1308 | 1.2502 | 0.0326 | 4 |
| seed_002.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_a0_ph0p54_ld0p22_ls0p35` | 105 | 1 | 0.1502 | 1.2491 | 0.0408 | 5 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p06_am0p014_ph0p54_ld0p22_ls0p35` | 99 | 1 | 0.1601 | 1.2916 | 0.0322 | 4 |
| seed_002.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p06_am0p014_ph0p54_ld0p22_ls0p35` | 94 | 1 | 0.1664 | 1.2588 | 0.0380 | 4 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_a0_ph0p3927_ld0p38_ls0p65` | 200 | 0 | 0.0091 | 0.1504 | 0.1486 | 4 |
| seed_002.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_a0_ph0p3927_ld0p38_ls0p65` | 200 | 0 | 0.0105 | 0.1056 | 0.1486 | 4 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p0075_ph0p47_ld0p22_ls0p65` | 63 | 1 | 0.2537 | 1.3084 | 0.0303 | 0 |
| seed_002.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p0075_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0136 | 0.1257 | 0.1463 | 4 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p012_ph0p32_ld0p3_ls1` | 58 | 1 | 0.2758 | 1.3091 | 0.0278 | 0 |
| seed_002.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p012_ph0p32_ld0p3_ls1` | 200 | 0 | 0.0134 | 0.1763 | 0.1460 | 5 |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p012_ph0p32_ld0p38_ls1` | 200 | 0 | 0.0080 | 0.1566 | 0.1469 | 4 |
| seed_002.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p012_ph0p32_ld0p38_ls1` | 200 | 0 | 0.0097 | 0.1222 | 0.1480 | 4 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p54_ld0p22_ls1` | 200 | 0 | 0.0074 | 0.1320 | 0.1478 | 3 |
| seed_002.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p54_ld0p22_ls1` | 200 | 0 | 0.0092 | 0.0988 | 0.1478 | 4 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p00625_ph0p3927_ld0p38_ls0p35` | 200 | 0 | 0.0101 | 0.1510 | 0.1465 | 3 |
| seed_002.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p00625_ph0p3927_ld0p38_ls0p35` | 200 | 0 | 0.0119 | 0.0956 | 0.1465 | 4 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p54_ld0p3_ls0p35` | 200 | 0 | 0.0124 | 0.1878 | 0.1450 | 4 |
| seed_002.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p54_ld0p3_ls0p35` | 149 | 1 | 0.1076 | 1.2446 | 0.0349 | 9 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p54_ld0p38_ls0p35` | 200 | 0 | 0.0107 | 0.1452 | 0.1458 | 3 |
| seed_002.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p00625_ph0p54_ld0p38_ls0p35` | 200 | 0 | 0.0124 | 0.1103 | 0.1458 | 6 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p00625_ph0p54_ld0p22_ls1` | 200 | 0 | 0.0071 | 0.1322 | 0.1486 | 3 |
| seed_002.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p00625_ph0p54_ld0p22_ls1` | 200 | 0 | 0.0094 | 0.0946 | 0.1486 | 4 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_a0_ph0p32_ld0p38_ls1` | 200 | 0 | 0.0090 | 0.1732 | 0.1456 | 4 |
| seed_002.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_a0_ph0p32_ld0p38_ls1` | 200 | 0 | 0.0108 | 0.0881 | 0.1465 | 3 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p00875_ph0p47_ld0p38_ls0p35` | 200 | 0 | 0.0094 | 0.1485 | 0.1473 | 3 |
| seed_002.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p00875_ph0p47_ld0p38_ls0p35` | 200 | 0 | 0.0112 | 0.0852 | 0.1473 | 3 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p54_ld0p3_ls1` | 200 | 0 | 0.0085 | 0.1576 | 0.1470 | 4 |
| seed_002.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p54_ld0p3_ls1` | 200 | 0 | 0.0106 | 0.0947 | 0.1468 | 3 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p32_ld0p38_ls0p35` | 200 | 0 | 0.0103 | 0.1646 | 0.1468 | 3 |
| seed_002.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p32_ld0p38_ls0p35` | 200 | 0 | 0.0120 | 0.0948 | 0.1468 | 5 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_a0_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0117 | 0.1626 | 0.1462 | 4 |
| seed_002.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_a0_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0136 | 0.1082 | 0.1462 | 5 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p012_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0118 | 0.1813 | 0.1457 | 4 |
| seed_002.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p012_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0136 | 0.1280 | 0.1457 | 4 |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0081 | 0.1297 | 0.1488 | 3 |
| seed_002.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0102 | 0.0873 | 0.1488 | 3 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p47_ld0p22_ls0p35` | 200 | 0 | 0.0102 | 0.1340 | 0.1471 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p0025_ph0p47_ld0p22_ls0p35` | 200 | 0 | 0.0120 | 0.0901 | 0.1470 | 7 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p00875_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0098 | 0.1706 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p00875_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0113 | 0.0796 | 0.1471 | 7 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0121 | 0.1772 | 0.1467 | 4 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0139 | 0.1166 | 0.1467 | 4 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p47_ld0p3_ls1` | 85 | 1 | 0.1872 | 1.2838 | 0.0305 | 2 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0129 | 0.1357 | 0.1457 | 5 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p0075_ph0p54_ld0p22_ls1` | 200 | 0 | 0.0106 | 0.1709 | 0.1468 | 4 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p0075_ph0p54_ld0p22_ls1` | 200 | 0 | 0.0128 | 0.1349 | 0.1468 | 5 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p0075_ph0p54_ld0p38_ls0p65` | 200 | 0 | 0.0092 | 0.1480 | 0.1485 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p0075_ph0p54_ld0p38_ls0p65` | 200 | 0 | 0.0106 | 0.0810 | 0.1483 | 5 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0081 | 0.1449 | 0.1478 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0099 | 0.1039 | 0.1477 | 4 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p00625_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0123 | 0.1860 | 0.1458 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p00625_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0138 | 0.1173 | 0.1465 | 5 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p0035_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0072 | 0.1396 | 0.1489 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p0035_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0090 | 0.1079 | 0.1489 | 4 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_a0_ph0p54_ld0p3_ls1` | 200 | 0 | 0.0077 | 0.1378 | 0.1486 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_a0_ph0p54_ld0p3_ls1` | 200 | 0 | 0.0093 | 0.1092 | 0.1486 | 4 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p54_ld0p22_ls0p65` | 200 | 0 | 0.0125 | 0.1883 | 0.1469 | 4 |
| seed_002.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p54_ld0p22_ls0p65` | 200 | 0 | 0.0141 | 0.1176 | 0.1469 | 4 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p003_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0073 | 0.1433 | 0.1483 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p003_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0092 | 0.1146 | 0.1483 | 4 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p012_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0084 | 0.1566 | 0.1480 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p012_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0099 | 0.1261 | 0.1478 | 4 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p003_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0073 | 0.1453 | 0.1486 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p003_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0091 | 0.1092 | 0.1486 | 4 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p012_ph0p32_ld0p3_ls0p35` | 200 | 0 | 0.0098 | 0.1484 | 0.1483 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p012_ph0p32_ld0p3_ls0p35` | 200 | 0 | 0.0113 | 0.0836 | 0.1482 | 6 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p47_ld0p38_ls0p65` | 200 | 0 | 0.0120 | 0.1951 | 0.1456 | 4 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p47_ld0p38_ls0p65` | 200 | 0 | 0.0136 | 0.1205 | 0.1454 | 5 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p01_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0084 | 0.1527 | 0.1469 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p01_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0104 | 0.1116 | 0.1468 | 4 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p01_ph0p47_ld0p38_ls0p65` | 111 | 1 | 0.1414 | 1.2744 | 0.0332 | 2 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p01_ph0p47_ld0p38_ls0p65` | 200 | 0 | 0.0139 | 0.1286 | 0.1444 | 6 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p0025_ph0p54_ld0p22_ls0p65` | 200 | 0 | 0.0086 | 0.1295 | 0.1489 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p0025_ph0p54_ld0p22_ls0p65` | 200 | 0 | 0.0107 | 0.0862 | 0.1489 | 5 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p0035_ph0p54_ld0p38_ls0p35` | 200 | 0 | 0.0100 | 0.1413 | 0.1476 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p0035_ph0p54_ld0p38_ls0p35` | 200 | 0 | 0.0118 | 0.0835 | 0.1475 | 7 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p014_ph0p32_ld0p38_ls0p35` | 82 | 1 | 0.1876 | 1.2479 | 0.0381 | 2 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p014_ph0p32_ld0p38_ls0p35` | 200 | 0 | 0.0144 | 0.1025 | 0.1454 | 8 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0_ph0p32_ld0p3_ls1` | 200 | 0 | 0.0083 | 0.1533 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0_ph0p32_ld0p3_ls1` | 200 | 0 | 0.0101 | 0.0925 | 0.1467 | 6 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p0075_ph0p54_ld0p38_ls1` | 200 | 0 | 0.0081 | 0.1416 | 0.1473 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p0075_ph0p54_ld0p38_ls1` | 200 | 0 | 0.0099 | 0.0861 | 0.1469 | 5 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p0075_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0107 | 0.1674 | 0.1469 | 4 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p0075_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0128 | 0.1352 | 0.1469 | 4 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p014_ph0p32_ld0p38_ls0p35` | 5-29 | 0.1085 | 0.0794 | 0.3206 | 0.1476 | 0.0000 | 0.3574 | 0.0696 | 52 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p54_ld0p38_ls0p35` | 5-29 | 0.1067 | 0.0743 | 0.3178 | 0.1473 | 0.0000 | 0.2496 | 0.0666 | 60 | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p01_ph0p47_ld0p38_ls0p65` | 5-29 | 0.1047 | 0.0854 | 0.3227 | 0.1460 | 0.0000 | 0.3630 | 0.0682 | 81 | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p0025_ph0p32_ld0p3_ls0p65` | 5-29 | 0.1036 | 0.0895 | 0.3078 | 0.1492 | 0.0000 | 0.2315 | 0.0654 | 77 | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p00625_ph0p32_ld0p22_ls0p65` | 5-29 | 0.1025 | 0.0763 | 0.3068 | 0.1481 | 0.0000 | 0.2824 | 0.0631 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p06_am0p014_ph0p54_ld0p22_ls0p35` | 5-29 | 0.1012 | 0.0652 | 0.3003 | 0.1479 | 0.0000 | 0.3211 | 0.0695 | 69 | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_a0_ph0p32_ld0p38_ls1` | 5-29 | 0.1008 | 0.0930 | 0.2867 | 0.1496 | 0.0000 | 0.3226 | 0.0758 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p06_am0p014_ph0p47_ld0p3_ls0p35` | 0-24 | 0.1001 | 0.1950 | 0.2842 | 0.1484 | 0.0000 | 0.3889 | 0.0817 | 51 | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p47_ld0p3_ls1` | 5-29 | 0.1000 | 0.0942 | 0.3076 | 0.1474 | 0.0000 | 0.3131 | 0.0710 | 55 | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p012_ph0p3927_ld0p22_ls0p65` | 5-29 | 0.0994 | 0.0795 | 0.2966 | 0.1482 | 0.0000 | 0.2761 | 0.0664 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p014_ph0p32_ld0p38_ls0p35` | 0-24 | 0.0993 | 0.2101 | 0.2799 | 0.1481 | 0.0000 | 0.3363 | 0.0786 | 57 | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_a0_ph0p54_ld0p3_ls1` | 5-29 | 0.0992 | 0.0879 | 0.3156 | 0.1464 | 0.0000 | 0.2798 | 0.0750 | 76 | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p47_ld0p38_ls0p65` | 5-29 | 0.0983 | 0.0812 | 0.3071 | 0.1467 | 0.0000 | 0.3111 | 0.0666 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p68_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p32_ld0p38_ls0p65` | 5-29 | 0.0979 | 0.0806 | 0.2819 | 0.1490 | 0.0000 | 0.3245 | 0.0698 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_a0_ph0p3927_ld0p22_ls0p65` | 5-29 | 0.0977 | 0.0809 | 0.2880 | 0.1487 | 0.0000 | 0.2697 | 0.0670 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p54_ld0p38_ls0p35` | 0-24 | 0.0972 | 0.2038 | 0.2839 | 0.1474 | 0.0000 | 0.3251 | 0.0816 | 65 | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p68_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p54_ld0p3_ls0p35` | 5-29 | 0.0970 | 0.0710 | 0.2953 | 0.1472 | 0.0000 | 0.2503 | 0.0682 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p01_ph0p47_ld0p38_ls0p65` | 0-24 | 0.0969 | 0.2064 | 0.2811 | 0.1481 | 0.0000 | 0.3639 | 0.0876 | 86 | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p0025_ph0p47_ld0p38_ls0p35` | 5-29 | 0.0962 | 0.0833 | 0.2971 | 0.1472 | 0.0000 | 0.3340 | 0.0678 | 66 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p64_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_a0_ph0p54_ld0p3_ls0p35` | 5-29 | 0.0953 | 0.0769 | 0.2929 | 0.1475 | 0.0000 | 0.3344 | 0.0624 | 73 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p54_ld0p38_ls1` | 5-29 | 0.0946 | 0.0841 | 0.2732 | 0.1493 | 0.0000 | 0.5752 | 0.0742 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p3927_ld0p38_ls0p65` | 5-29 | 0.0944 | 0.0809 | 0.3055 | 0.1470 | 0.0000 | 0.3667 | 0.0683 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p00625_ph0p32_ld0p22_ls0p65` | 0-24 | 0.0942 | 0.2019 | 0.2652 | 0.1496 | 0.0000 | 0.2824 | 0.0843 | None | `{'01': 20.0, '11': 80.0}` |
| seed_002.jsonl | `primitive_p0p68_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p012_ph0p32_ld0p3_ls1` | 10-34 | 0.0939 | 0.0709 | 0.2914 | 0.1468 | 0.0000 | 0.5382 | 0.0656 | None | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p56_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p00875_ph0p32_ld0p38_ls0p35` | 5-29 | 0.0936 | 0.0811 | 0.2949 | 0.1476 | 0.0000 | 0.3918 | 0.0684 | 116 | `{'01': 16.0, '11': 84.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
