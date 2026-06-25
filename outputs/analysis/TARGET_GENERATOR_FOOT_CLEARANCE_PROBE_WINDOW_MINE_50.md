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
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0092 | 0.1301 | 0.1484 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0109 | 0.0911 | 0.1480 | 4 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0083 | 0.1495 | 0.1472 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0103 | 0.1220 | 0.1466 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0082 | 0.1486 | 0.1473 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p22_ls1` | 200 | 0 | 0.0103 | 0.1073 | 0.1467 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p16_ls1` | 200 | 0 | 0.0109 | 0.1686 | 0.1465 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p16_ls1` | 200 | 0 | 0.0130 | 0.1346 | 0.1465 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p3927_ld0p16_ls1` | 200 | 0 | 0.0071 | 0.1284 | 0.1492 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p3927_ld0p16_ls1` | 200 | 0 | 0.0090 | 0.0871 | 0.1490 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p0105_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0075 | 0.1314 | 0.1491 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p0105_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0094 | 0.0898 | 0.1487 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p0105_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0090 | 0.1543 | 0.1468 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p0105_ph0p47_ld0p3_ls1` | 200 | 0 | 0.0107 | 0.1078 | 0.1466 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0122 | 0.1729 | 0.1462 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0138 | 0.1123 | 0.1461 | 4 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p00525_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0110 | 0.1718 | 0.1462 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p00525_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0130 | 0.1393 | 0.1465 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0106 | 0.1601 | 0.1464 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 98 | 1 | 0.1680 | 1.3147 | 0.0244 | 0 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p47_ld0p16_ls0p65` | 200 | 0 | 0.0095 | 0.1440 | 0.1478 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p47_ld0p16_ls0p65` | 200 | 0 | 0.0115 | 0.0916 | 0.1473 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p0105_ph0p3927_ld0p16_ls0p65` | 200 | 0 | 0.0099 | 0.1413 | 0.1478 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p0105_ph0p3927_ld0p16_ls0p65` | 200 | 0 | 0.0116 | 0.0957 | 0.1471 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 91 | 1 | 0.1709 | 1.2620 | 0.0344 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 89 | 1 | 0.1725 | 1.2350 | 0.0429 | 0 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p16_ls0p65` | 200 | 0 | 0.0123 | 0.1917 | 0.1445 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p16_ls0p65` | 123 | 1 | 0.1318 | 1.2861 | 0.0298 | 2 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0_ph0p3927_ld0p16_ls0p65` | 200 | 0 | 0.0103 | 0.1528 | 0.1467 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0_ph0p3927_ld0p16_ls0p65` | 200 | 0 | 0.0121 | 0.1194 | 0.1443 | 2 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p3_ls0p65` | 71 | 1 | 0.2240 | 1.3022 | 0.0271 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p3_ls0p65` | 79 | 1 | 0.1978 | 1.2399 | 0.0398 | 0 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0_ph0p47_ld0p3_ls0p65` | 82 | 1 | 0.1936 | 1.2792 | 0.0316 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0_ph0p47_ld0p3_ls0p65` | 80 | 1 | 0.2062 | 1.3059 | 0.0269 | 0 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p00525_ph0p3927_ld0p16_ls1` | 200 | 0 | 0.0111 | 0.1757 | 0.1460 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p00525_ph0p3927_ld0p16_ls1` | 200 | 0 | 0.0131 | 0.1336 | 0.1463 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p0105_ph0p47_ld0p3_ls0p65` | 81 | 1 | 0.1999 | 1.3068 | 0.0263 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p0105_ph0p47_ld0p3_ls0p65` | 77 | 1 | 0.2137 | 1.3141 | 0.0251 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p00375_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0107 | 0.1502 | 0.1464 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p00375_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0122 | 0.0923 | 0.1457 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0107 | 0.1439 | 0.1462 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0122 | 0.0947 | 0.1455 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls1` | 70 | 1 | 0.2219 | 1.2829 | 0.0360 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0139 | 0.1631 | 0.1451 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p3_ls0p65` | 102 | 1 | 0.1496 | 1.2362 | 0.0403 | 1 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p3_ls0p65` | 93 | 1 | 0.1661 | 1.2411 | 0.0438 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p16_ls0p65` | 200 | 0 | 0.0100 | 0.1508 | 0.1468 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p16_ls0p65` | 200 | 0 | 0.0119 | 0.0911 | 0.1460 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0089 | 0.1450 | 0.1483 | 1 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0106 | 0.0841 | 0.1478 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls1` | 82 | 1 | 0.1991 | 1.3319 | 0.0238 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0129 | 0.1493 | 0.1462 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p3_ls1` | 65 | 1 | 0.2377 | 1.2612 | 0.0380 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p3_ls1` | 200 | 0 | 0.0134 | 0.1559 | 0.1454 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 109 | 1 | 0.1445 | 1.3037 | 0.0303 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 94 | 1 | 0.1751 | 1.3070 | 0.0282 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p00525_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0108 | 0.1694 | 0.1466 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p00525_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0130 | 0.1325 | 0.1466 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p0105_ph0p3927_ld0p3_ls0p65` | 84 | 1 | 0.1939 | 1.3385 | 0.0230 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p0105_ph0p3927_ld0p3_ls0p65` | 90 | 1 | 0.1792 | 1.2677 | 0.0338 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p00525_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0113 | 0.1693 | 0.1458 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p00525_ph0p32_ld0p22_ls0p65` | 92 | 1 | 0.1725 | 1.2679 | 0.0379 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p0105_ph0p32_ld0p22_ls0p65` | 200 | 0 | 0.0113 | 0.1664 | 0.1456 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p0105_ph0p32_ld0p22_ls0p65` | 94 | 1 | 0.1638 | 1.2465 | 0.0450 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p0105_ph0p3927_ld0p22_ls0p65` | 200 | 0 | 0.0111 | 0.1602 | 0.1454 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0p0105_ph0p3927_ld0p22_ls0p65` | 93 | 1 | 0.1700 | 1.2753 | 0.0387 | 0 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0074 | 0.1408 | 0.1474 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p04_a0p0075_ph0p3927_ld0p22_ls1` | 200 | 0 | 0.0093 | 0.1032 | 0.1472 | 1 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_a0p0075_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0106 | 0.1742 | 0.1450 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_a0p0075_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0123 | 0.1192 | 0.1447 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0083 | 0.1694 | 0.1462 | 2 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0103 | 0.1226 | 0.1462 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0065 | 0.1311 | 0.1480 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0086 | 0.0902 | 0.1480 | 0 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p00375_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0100 | 0.1717 | 0.1453 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p00375_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0121 | 0.1560 | 0.1461 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p32_ld0p16_ls1` | 200 | 0 | 0.0102 | 0.1644 | 0.1448 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p32_ld0p16_ls1` | 200 | 0 | 0.0123 | 0.1537 | 0.1461 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p32_ld0p3_ls0p65` | 61 | 1 | 0.2570 | 1.2845 | 0.0332 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p32_ld0p3_ls0p65` | 96 | 1 | 0.1709 | 1.2899 | 0.0289 | 0 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p3927_ld0p16_ls0p65` | 200 | 0 | 0.0106 | 0.1802 | 0.1452 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p3927_ld0p16_ls0p65` | 200 | 0 | 0.0124 | 0.1100 | 0.1450 | 4 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0067 | 0.1332 | 0.1478 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p16_ls1` | 200 | 0 | 0.0089 | 0.1002 | 0.1477 | 1 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0090 | 0.1548 | 0.1460 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0104 | 0.0912 | 0.1447 | 5 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p22_ls1` | 71 | 1 | 0.2268 | 1.3037 | 0.0268 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p22_ls1` | 200 | 0 | 0.0127 | 0.1671 | 0.1454 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0p0075_ph0p32_ld0p16_ls0p65` | 88 | 1 | 0.1799 | 1.3046 | 0.0296 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0p0075_ph0p32_ld0p16_ls0p65` | 94 | 1 | 0.1768 | 1.3220 | 0.0239 | 0 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0078 | 0.1411 | 0.1482 | 2 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0094 | 0.0844 | 0.1479 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p0105_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0108 | 0.1783 | 0.1460 | 3 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p0105_ph0p47_ld0p22_ls0p65` | 200 | 0 | 0.0125 | 0.1117 | 0.1460 | 3 |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p3_ls0p65` | 58 | 1 | 0.2818 | 1.3443 | 0.0214 | 0 |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p3_ls0p65` | 88 | 1 | 0.1839 | 1.3010 | 0.0281 | 0 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p16_ls0p65` | 0-49 | 0.0623 | 0.1752 | 0.3212 | 0.1469 | 0.0000 | 0.4768 | 0.0870 | 73 | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0_ph0p3927_ld0p16_ls0p65` | 0-49 | 0.0603 | 0.1743 | 0.3149 | 0.1469 | 0.0000 | 0.5720 | 0.0906 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls1` | 0-49 | 0.0589 | 0.1903 | 0.3058 | 0.1460 | 0.0000 | 0.2700 | 0.0808 | None | `{'01': 4.0, '11': 96.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 5-54 | 0.0584 | 0.0794 | 0.3470 | 0.1454 | 0.0000 | 0.5027 | 0.0693 | 54 | `{'01': 8.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p22_ls0p65` | 10-59 | 0.0580 | 0.0646 | 0.3239 | 0.1461 | 0.0000 | 0.4323 | 0.0667 | None | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p3927_ld0p3_ls0p65` | 0-49 | 0.0579 | 0.1312 | 0.3470 | 0.1454 | 0.0000 | 0.5420 | 0.0767 | 59 | `{'01': 12.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p3_ls1` | 0-49 | 0.0574 | 0.1987 | 0.2930 | 0.1463 | 0.0000 | 0.3764 | 0.0785 | None | `{'01': 4.0, '11': 96.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p3_ls0p65` | 0-49 | 0.0571 | 0.1330 | 0.3457 | 0.1454 | 0.0000 | 0.5595 | 0.0738 | 52 | `{'01': 12.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p16_ls0p65` | 5-54 | 0.0568 | 0.0821 | 0.3466 | 0.1454 | 0.0000 | 0.5111 | 0.0724 | 68 | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p04_a0_ph0p47_ld0p16_ls0p65` | 0-49 | 0.0552 | 0.1697 | 0.2900 | 0.1471 | 0.0000 | 0.5153 | 0.0839 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p3927_ld0p16_ls0p65` | 10-59 | 0.0551 | 0.0548 | 0.3232 | 0.1463 | 0.0000 | 0.3917 | 0.0681 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p00525_ph0p32_ld0p22_ls1` | 0-49 | 0.0551 | 0.1923 | 0.2889 | 0.1471 | 0.0000 | 0.4135 | 0.0831 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p04_a0_ph0p3927_ld0p16_ls0p65` | 5-54 | 0.0551 | 0.1021 | 0.3408 | 0.1459 | 0.0000 | 0.6758 | 0.0718 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p04_a0p0075_ph0p47_ld0p3_ls0p65` | 0-49 | 0.0549 | 0.1675 | 0.2865 | 0.1472 | 0.0000 | 0.5595 | 0.0820 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0_ph0p47_ld0p16_ls0p65` | 0-49 | 0.0548 | 0.1221 | 0.3384 | 0.1464 | 0.0000 | 0.4768 | 0.0854 | None | `{'01': 10.0, '11': 90.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls0p65` | 0-49 | 0.0546 | 0.1798 | 0.2818 | 0.1477 | 0.0000 | 0.4195 | 0.0823 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p025_kb0p06_k0p22_ab0p06_a0_ph0p32_ld0p16_ls1` | 0-49 | 0.0546 | 0.1903 | 0.2779 | 0.1473 | 0.0000 | 0.2851 | 0.0877 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_a0p0075_ph0p47_ld0p3_ls0p65` | 0-49 | 0.0546 | 0.1817 | 0.2904 | 0.1467 | 0.0000 | 0.3999 | 0.0735 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p06_a0p00525_ph0p47_ld0p16_ls1` | 0-49 | 0.0546 | 0.1873 | 0.2767 | 0.1476 | 0.0000 | 0.3606 | 0.0830 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0p0105_ph0p47_ld0p22_ls0p65` | 5-54 | 0.0544 | 0.0682 | 0.3359 | 0.1465 | 0.0000 | 0.3430 | 0.0648 | None | `{'01': 8.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p22_ab0p06_a0p00525_ph0p3927_ld0p16_ls1` | 0-49 | 0.0544 | 0.1912 | 0.2764 | 0.1472 | 0.0000 | 0.3996 | 0.0867 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p00375_ph0p47_ld0p16_ls1` | 5-54 | 0.0542 | 0.0815 | 0.3453 | 0.1456 | 0.0000 | 0.2393 | 0.0727 | None | `{'01': 4.0, '11': 96.0}` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_a0_ph0p32_ld0p22_ls1` | 0-49 | 0.0542 | 0.1913 | 0.2849 | 0.1471 | 0.0000 | 0.3692 | 0.0796 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p3927_ld0p16_ls0p65` | 0-49 | 0.0540 | 0.1722 | 0.2843 | 0.1468 | 0.0000 | 0.4559 | 0.0806 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_000.jsonl | `primitive_p0p64_hrb0_hb0p08_h0p025_kb0p06_k0p18_ab0p06_a0p0075_ph0p3927_ld0p16_ls0p65` | 5-54 | 0.0540 | 0.0616 | 0.3326 | 0.1462 | 0.0000 | 0.3917 | 0.0624 | None | `{'01': 8.0, '11': 92.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
