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
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0092 | 0.1301 | 0.1484 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0109 | 0.0911 | 0.1480 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0083 | 0.1495 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0103 | 0.1220 | 0.1466 | 7 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0082 | 0.1486 | 0.1473 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0103 | 0.1073 | 0.1467 | 7 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p16_ls1` | 200 | 0 | 0.0109 | 0.1686 | 0.1465 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p16_ls1` | 200 | 0 | 0.0130 | 0.1346 | 0.1465 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p3927_ld0p16_ls1` | 200 | 0 | 0.0071 | 0.1284 | 0.1492 | 3 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p3927_ld0p16_ls1` | 200 | 0 | 0.0090 | 0.0871 | 0.1490 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p0105_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0075 | 0.1314 | 0.1491 | 3 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p0105_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0094 | 0.0898 | 0.1487 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p0105_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0090 | 0.1543 | 0.1468 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p0105_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0107 | 0.1078 | 0.1466 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0122 | 0.1729 | 0.1462 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0138 | 0.1123 | 0.1461 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p00525_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0110 | 0.1718 | 0.1462 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p00525_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0130 | 0.1393 | 0.1465 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0106 | 0.1601 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 98 | 1 | 0.1680 | 1.3147 | 0.0244 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p47_ld0p16_ls0p65` | 200 | 0 | 0.0095 | 0.1440 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p47_ld0p16_ls0p65` | 200 | 0 | 0.0115 | 0.0916 | 0.1473 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p0105_ph0p3927_ld0p16_ls0p65` | 200 | 0 | 0.0099 | 0.1413 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p0105_ph0p3927_ld0p16_ls0p65` | 200 | 0 | 0.0116 | 0.0957 | 0.1471 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 91 | 1 | 0.1709 | 1.2620 | 0.0344 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 89 | 1 | 0.1725 | 1.2350 | 0.0429 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p16_ls0p65` | 200 | 0 | 0.0123 | 0.1917 | 0.1445 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p16_ls0p65` | 123 | 1 | 0.1318 | 1.2861 | 0.0298 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0_ph0p3927_ld0p16_ls0p65` | 200 | 0 | 0.0103 | 0.1528 | 0.1467 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0_ph0p3927_ld0p16_ls0p65` | 200 | 0 | 0.0121 | 0.1194 | 0.1443 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p3_ls0p65` | 71 | 1 | 0.2240 | 1.3022 | 0.0271 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p3_ls0p65` | 79 | 1 | 0.1978 | 1.2399 | 0.0398 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0_ph0p47_ld0p3_ls0p65` | 82 | 1 | 0.1936 | 1.2792 | 0.0316 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0_ph0p47_ld0p3_ls0p65` | 80 | 1 | 0.2062 | 1.3059 | 0.0269 | 2 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p00525_ph0p3927_ld0p16_ls1` | 200 | 0 | 0.0111 | 0.1757 | 0.1460 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p00525_ph0p3927_ld0p16_ls1` | 200 | 0 | 0.0131 | 0.1336 | 0.1463 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p0105_ph0p47_ld0p3_ls0p65` | 81 | 1 | 0.1999 | 1.3068 | 0.0263 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p0105_ph0p47_ld0p3_ls0p65` | 77 | 1 | 0.2137 | 1.3141 | 0.0251 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p00375_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0107 | 0.1502 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p00375_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0122 | 0.0923 | 0.1457 | 8 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0107 | 0.1439 | 0.1462 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0122 | 0.0947 | 0.1455 | 8 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls1` | 70 | 1 | 0.2219 | 1.2829 | 0.0360 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0139 | 0.1631 | 0.1451 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p3_ls0p65` | 102 | 1 | 0.1496 | 1.2362 | 0.0403 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p3_ls0p65` | 93 | 1 | 0.1661 | 1.2411 | 0.0438 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p16_ls0p65` | 200 | 0 | 0.0100 | 0.1508 | 0.1468 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p16_ls0p65` | 200 | 0 | 0.0119 | 0.0911 | 0.1460 | 7 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0089 | 0.1450 | 0.1483 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0106 | 0.0841 | 0.1478 | 7 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls1` | 82 | 1 | 0.1991 | 1.3319 | 0.0238 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0129 | 0.1493 | 0.1462 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p3_ls1` | 65 | 1 | 0.2377 | 1.2612 | 0.0380 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p3_ls1` | 200 | 0 | 0.0134 | 0.1559 | 0.1454 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 109 | 1 | 0.1445 | 1.3037 | 0.0303 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 94 | 1 | 0.1751 | 1.3070 | 0.0282 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p00525_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0108 | 0.1694 | 0.1466 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p00525_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0130 | 0.1325 | 0.1466 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p0105_ph0p3927_ld0p3_ls0p65` | 84 | 1 | 0.1939 | 1.3385 | 0.0230 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p0105_ph0p3927_ld0p3_ls0p65` | 90 | 1 | 0.1792 | 1.2677 | 0.0338 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p00525_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0113 | 0.1693 | 0.1458 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p00525_ph0p32_ld0p22_ls0p65` | 92 | 1 | 0.1725 | 1.2679 | 0.0379 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p0105_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0113 | 0.1664 | 0.1456 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p0105_ph0p32_ld0p22_ls0p65` | 94 | 1 | 0.1638 | 1.2465 | 0.0450 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p0105_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0111 | 0.1602 | 0.1454 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p0105_ph0p3927_ld0p22_ls0p65` | 93 | 1 | 0.1700 | 1.2753 | 0.0387 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0074 | 0.1408 | 0.1474 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0093 | 0.1032 | 0.1472 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_a0p0075_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0106 | 0.1742 | 0.1450 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_a0p0075_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0123 | 0.1192 | 0.1447 | 5 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0083 | 0.1694 | 0.1462 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0103 | 0.1226 | 0.1462 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0065 | 0.1311 | 0.1480 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0086 | 0.0902 | 0.1480 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p00375_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0100 | 0.1717 | 0.1453 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p00375_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0121 | 0.1560 | 0.1461 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p32_ld0p16_ls1` | 200 | 0 | 0.0102 | 0.1644 | 0.1448 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p32_ld0p16_ls1` | 200 | 0 | 0.0123 | 0.1537 | 0.1461 | 5 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p32_ld0p3_ls0p65` | 61 | 1 | 0.2570 | 1.2845 | 0.0332 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p32_ld0p3_ls0p65` | 96 | 1 | 0.1709 | 1.2899 | 0.0289 | 5 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p3927_ld0p16_ls0p65` | 200 | 0 | 0.0106 | 0.1802 | 0.1452 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p3927_ld0p16_ls0p65` | 200 | 0 | 0.0124 | 0.1100 | 0.1450 | 9 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0067 | 0.1332 | 0.1478 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0089 | 0.1002 | 0.1477 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0090 | 0.1548 | 0.1460 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0104 | 0.0912 | 0.1447 | 8 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p22_ls1` | 71 | 1 | 0.2268 | 1.3037 | 0.0268 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0127 | 0.1671 | 0.1454 | 5 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0p0075_ph0p32_ld0p16_ls0p65` | 88 | 1 | 0.1799 | 1.3046 | 0.0296 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0p0075_ph0p32_ld0p16_ls0p65` | 94 | 1 | 0.1768 | 1.3220 | 0.0239 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0078 | 0.1411 | 0.1482 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0094 | 0.0844 | 0.1479 | 6 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p0105_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0108 | 0.1783 | 0.1460 | 4 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p0105_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0125 | 0.1117 | 0.1460 | 6 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p3_ls0p65` | 58 | 1 | 0.2818 | 1.3443 | 0.0214 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p3_ls0p65` | 88 | 1 | 0.1839 | 1.3010 | 0.0281 | 3 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p0105_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.1017 | 0.0864 | 0.3160 | 0.1467 | 0.0000 | 0.5534 | 0.0630 | 54 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls1` | 5-29 | 0.1014 | 0.0953 | 0.3034 | 0.1477 | 0.0000 | 0.3715 | 0.0703 | 52 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0p0075_ph0p32_ld0p16_ls0p65` | 5-29 | 0.0981 | 0.0777 | 0.2983 | 0.1477 | 0.0000 | 0.3065 | 0.0613 | 58 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0962 | 0.0840 | 0.3046 | 0.1465 | 0.0000 | 0.5534 | 0.0626 | 79 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p0105_ph0p3927_ld0p3_ls0p65` | 0-24 | 0.0941 | 0.2146 | 0.2655 | 0.1488 | 0.0000 | 0.4190 | 0.0936 | 59 | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p32_ld0p16_ls1` | 5-29 | 0.0939 | 0.0960 | 0.2810 | 0.1498 | 0.0000 | 0.2287 | 0.0677 | None | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p00375_ph0p47_ld0p16_ls1` | 5-29 | 0.0935 | 0.0976 | 0.2797 | 0.1497 | 0.0000 | 0.2283 | 0.0675 | None | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p00525_ph0p3927_ld0p16_ls1` | 5-29 | 0.0934 | 0.0953 | 0.3100 | 0.1470 | 0.0000 | 0.4125 | 0.0755 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p00525_ph0p32_ld0p22_ls1` | 5-29 | 0.0934 | 0.0972 | 0.3075 | 0.1470 | 0.0000 | 0.4215 | 0.0708 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls1` | 0-24 | 0.0932 | 0.2185 | 0.2540 | 0.1500 | 0.0000 | 0.3580 | 0.0922 | 57 | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p0105_ph0p47_ld0p22_ls0p65` | 5-29 | 0.0932 | 0.0834 | 0.2794 | 0.1486 | 0.0000 | 0.3357 | 0.0640 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 0-24 | 0.0928 | 0.2095 | 0.2663 | 0.1485 | 0.0000 | 0.4190 | 0.0937 | 84 | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p3927_ld0p16_ls0p65` | 5-29 | 0.0927 | 0.0855 | 0.2866 | 0.1478 | 0.0000 | 0.3163 | 0.0619 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_a0p0075_ph0p47_ld0p3_ls0p65` | 5-29 | 0.0922 | 0.0848 | 0.2861 | 0.1477 | 0.0000 | 0.2930 | 0.0601 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p3_ls0p65` | 5-29 | 0.0920 | 0.0833 | 0.2977 | 0.1468 | 0.0000 | 0.6147 | 0.0626 | 72 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p0105_ph0p47_ld0p3_ls0p65` | 5-29 | 0.0920 | 0.0864 | 0.3100 | 0.1456 | 0.0000 | 0.8721 | 0.0589 | 51 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p00525_ph0p47_ld0p16_ls1` | 5-29 | 0.0902 | 0.0940 | 0.2778 | 0.1480 | 0.0000 | 0.3723 | 0.0690 | None | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p16_ls1` | 5-29 | 0.0901 | 0.0979 | 0.2989 | 0.1471 | 0.0000 | 0.2954 | 0.0735 | None | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p16_ls0p65` | 5-29 | 0.0898 | 0.0774 | 0.3029 | 0.1468 | 0.0000 | 0.5111 | 0.0600 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0p0075_ph0p32_ld0p16_ls0p65` | 0-24 | 0.0886 | 0.2071 | 0.2582 | 0.1483 | 0.0000 | 0.4032 | 0.0956 | 63 | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0_ph0p47_ld0p3_ls0p65` | 5-29 | 0.0884 | 0.0876 | 0.2987 | 0.1463 | 0.0000 | 0.8721 | 0.0627 | 52 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p0105_ph0p47_ld0p22_ls0p65` | 0-24 | 0.0882 | 0.2051 | 0.2490 | 0.1498 | 0.0000 | 0.3357 | 0.0822 | None | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p0105_ph0p47_ld0p3_ls0p65` | 0-24 | 0.0881 | 0.1981 | 0.2620 | 0.1481 | 0.0000 | 0.6612 | 0.0909 | 56 | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p3_ls0p65` | 0-24 | 0.0881 | 0.2120 | 0.2629 | 0.1484 | 0.0000 | 0.4606 | 0.0951 | 77 | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 5-29 | 0.0876 | 0.0826 | 0.2945 | 0.1466 | 0.0000 | 0.6601 | 0.0636 | 61 | `{'01': 16.0, '11': 84.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
