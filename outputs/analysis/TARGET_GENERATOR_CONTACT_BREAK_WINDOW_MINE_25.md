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
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p32` | 85 | 1 | 0.1887 | 1.3183 | 0.0266 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p32` | 76 | 1 | 0.2105 | 1.2550 | 0.0321 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p16_ab0p06_am0p0075_ph0p52` | 78 | 1 | 0.1963 | 1.2732 | 0.0373 | 1 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p025_kb0p06_k0p16_ab0p06_am0p0075_ph0p52` | 74 | 1 | 0.2110 | 1.2464 | 0.0374 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 200 | 0 | 0.0108 | 0.1762 | 0.1458 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p43` | 200 | 0 | 0.0123 | 0.1239 | 0.1458 | 8 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_am0p0035_ph0p32` | 78 | 1 | 0.2058 | 1.3075 | 0.0267 | 1 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p06_am0p0035_ph0p32` | 75 | 1 | 0.2150 | 1.2520 | 0.0294 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927` | 200 | 0 | 0.0110 | 0.1599 | 0.1446 | 7 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927` | 200 | 0 | 0.0126 | 0.1469 | 0.1448 | 8 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p47` | 200 | 0 | 0.0109 | 0.1686 | 0.1445 | 6 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p47` | 200 | 0 | 0.0123 | 0.1348 | 0.1446 | 8 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p003_ph0p3927` | 109 | 1 | 0.1523 | 1.3799 | 0.0182 | 6 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p003_ph0p3927` | 82 | 1 | 0.1922 | 1.2730 | 0.0373 | 2 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p06_a0_ph0p47` | 75 | 1 | 0.2025 | 1.2419 | 0.0393 | 1 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p06_a0_ph0p47` | 72 | 1 | 0.2196 | 1.2414 | 0.0345 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p0025_ph0p52` | 200 | 0 | 0.0113 | 0.1528 | 0.1447 | 6 |
| seed_002.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p0025_ph0p52` | 82 | 1 | 0.1994 | 1.3133 | 0.0275 | 2 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p025_kb0p06_k0p16_ab0p06_am0p0025_ph0p47` | 70 | 1 | 0.2230 | 1.2318 | 0.0343 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p025_kb0p06_k0p16_ab0p06_am0p0025_ph0p47` | 74 | 1 | 0.2226 | 1.3029 | 0.0241 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p007_ph0p32` | 96 | 1 | 0.1614 | 1.2549 | 0.0394 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p007_ph0p32` | 86 | 1 | 0.1955 | 1.3583 | 0.0207 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p47` | 200 | 0 | 0.0109 | 0.1674 | 0.1459 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p47` | 200 | 0 | 0.0123 | 0.1302 | 0.1453 | 8 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p52` | 79 | 1 | 0.1990 | 1.3026 | 0.0322 | 1 |
| seed_002.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p52` | 74 | 1 | 0.2131 | 1.2590 | 0.0358 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p009_ph0p32` | 83 | 1 | 0.1917 | 1.2937 | 0.0304 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p009_ph0p32` | 76 | 1 | 0.2103 | 1.2854 | 0.0324 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0_ph0p3927` | 139 | 1 | 0.1150 | 1.3310 | 0.0276 | 6 |
| seed_002.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0_ph0p3927` | 82 | 1 | 0.2044 | 1.3406 | 0.0205 | 2 |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p006_ph0p3927` | 86 | 1 | 0.1870 | 1.3093 | 0.0285 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p006_ph0p3927` | 84 | 1 | 0.1993 | 1.3389 | 0.0220 | 2 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p005_ph0p36` | 200 | 0 | 0.0107 | 0.1475 | 0.1447 | 7 |
| seed_002.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_am0p005_ph0p36` | 200 | 0 | 0.0124 | 0.1342 | 0.1445 | 8 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p005_ph0p52` | 82 | 1 | 0.1874 | 1.2669 | 0.0368 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p005_ph0p52` | 76 | 1 | 0.2186 | 1.3188 | 0.0222 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0075_ph0p47` | 84 | 1 | 0.1949 | 1.3314 | 0.0214 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0075_ph0p47` | 77 | 1 | 0.2176 | 1.3286 | 0.0204 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p47` | 95 | 1 | 0.1694 | 1.3129 | 0.0302 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p47` | 200 | 0 | 0.0124 | 0.1597 | 0.1449 | 8 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p47` | 200 | 0 | 0.0111 | 0.1777 | 0.1444 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p47` | 200 | 0 | 0.0124 | 0.1329 | 0.1445 | 8 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0105_ph0p36` | 88 | 1 | 0.1853 | 1.3036 | 0.0238 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0105_ph0p36` | 85 | 1 | 0.1891 | 1.2838 | 0.0335 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p014_ph0p36` | 76 | 1 | 0.2107 | 1.3028 | 0.0262 | 1 |
| seed_002.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p014_ph0p36` | 85 | 1 | 0.1914 | 1.2887 | 0.0302 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p43` | 200 | 0 | 0.0107 | 0.1681 | 0.1458 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p012_ph0p43` | 200 | 0 | 0.0122 | 0.1385 | 0.1450 | 8 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p009_ph0p43` | 81 | 1 | 0.1993 | 1.3276 | 0.0240 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p009_ph0p43` | 76 | 1 | 0.2110 | 1.2854 | 0.0307 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p009_ph0p47` | 80 | 1 | 0.1938 | 1.2744 | 0.0342 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p009_ph0p47` | 75 | 1 | 0.2055 | 1.2399 | 0.0409 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p06_am0p003_ph0p3927` | 77 | 1 | 0.2030 | 1.2843 | 0.0311 | 1 |
| seed_002.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p06_am0p003_ph0p3927` | 75 | 1 | 0.2155 | 1.2646 | 0.0285 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p06_am0p012_ph0p52` | 80 | 1 | 0.1906 | 1.2424 | 0.0391 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p06_am0p012_ph0p52` | 76 | 1 | 0.2126 | 1.3037 | 0.0287 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p32` | 200 | 0 | 0.0101 | 0.1545 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p32` | 200 | 0 | 0.0118 | 0.1249 | 0.1457 | 8 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p025_kb0p06_k0p16_ab0p04_am0p01_ph0p36` | 116 | 1 | 0.1379 | 1.3000 | 0.0287 | 6 |
| seed_002.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p025_kb0p06_k0p16_ab0p04_am0p01_ph0p36` | 100 | 1 | 0.1672 | 1.3164 | 0.0259 | 6 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p52` | 96 | 1 | 0.1643 | 1.2901 | 0.0367 | 3 |
| seed_002.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p52` | 111 | 1 | 0.1450 | 1.2712 | 0.0310 | 8 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p36` | 86 | 1 | 0.1822 | 1.2727 | 0.0327 | 3 |
| seed_002.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p36` | 82 | 1 | 0.1987 | 1.3107 | 0.0269 | 2 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927` | 113 | 1 | 0.1454 | 1.3250 | 0.0205 | 5 |
| seed_002.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p003_ph0p3927` | 200 | 0 | 0.0127 | 0.1515 | 0.1457 | 8 |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p006_ph0p36` | 200 | 0 | 0.0103 | 0.1467 | 0.1467 | 3 |
| seed_002.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p006_ph0p36` | 200 | 0 | 0.0119 | 0.1275 | 0.1468 | 7 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p007_ph0p43` | 100 | 1 | 0.1631 | 1.3118 | 0.0272 | 4 |
| seed_002.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p007_ph0p43` | 200 | 0 | 0.0123 | 0.1479 | 0.1446 | 9 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p36` | 200 | 0 | 0.0112 | 0.1955 | 0.1461 | 4 |
| seed_002.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p36` | 200 | 0 | 0.0123 | 0.1278 | 0.1461 | 4 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p43` | 200 | 0 | 0.0122 | 0.1493 | 0.1446 | 5 |
| seed_002.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p43` | 83 | 1 | 0.1975 | 1.3154 | 0.0255 | 2 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p007_ph0p32` | 92 | 1 | 0.1722 | 1.2975 | 0.0332 | 3 |
| seed_002.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p007_ph0p32` | 88 | 1 | 0.1866 | 1.3276 | 0.0257 | 3 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p06_am0p0105_ph0p47` | 80 | 1 | 0.1910 | 1.2510 | 0.0393 | 2 |
| seed_002.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p06_am0p0105_ph0p47` | 77 | 1 | 0.2024 | 1.2235 | 0.0386 | 1 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p52` | 84 | 1 | 0.1919 | 1.3098 | 0.0267 | 2 |
| seed_002.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p52` | 76 | 1 | 0.2119 | 1.2560 | 0.0309 | 1 |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p009_ph0p36` | 88 | 1 | 0.1769 | 1.2645 | 0.0360 | 3 |
| seed_002.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p009_ph0p36` | 85 | 1 | 0.1918 | 1.3007 | 0.0285 | 3 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0075_ph0p52` | 85 | 1 | 0.1891 | 1.3141 | 0.0253 | 3 |
| seed_002.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0075_ph0p52` | 78 | 1 | 0.1964 | 1.2041 | 0.0434 | 1 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p32` | 84 | 1 | 0.1949 | 1.3358 | 0.0210 | 2 |
| seed_002.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p32` | 80 | 1 | 0.2041 | 1.3002 | 0.0269 | 2 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p005_ph0p3927` | 200 | 0 | 0.0101 | 0.1415 | 0.1463 | 3 |
| seed_002.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p005_ph0p3927` | 200 | 0 | 0.0118 | 0.1138 | 0.1462 | 8 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p06_a0_ph0p3927` | 87 | 1 | 0.1893 | 1.3553 | 0.0194 | 3 |
| seed_002.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p06_a0_ph0p3927` | 80 | 1 | 0.1920 | 1.2204 | 0.0417 | 2 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p52` | 200 | 0 | 0.0115 | 0.1847 | 0.1448 | 4 |
| seed_002.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p014_ph0p52` | 200 | 0 | 0.0127 | 0.1389 | 0.1452 | 8 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p06_am0p003_ph0p43` | 78 | 1 | 0.1952 | 1.2417 | 0.0384 | 1 |
| seed_002.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p06_am0p003_ph0p43` | 77 | 1 | 0.2064 | 1.2411 | 0.0334 | 1 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p009_ph0p3927` | 200 | 0 | 0.0100 | 0.1565 | 0.1466 | 3 |
| seed_002.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p009_ph0p3927` | 200 | 0 | 0.0118 | 0.1237 | 0.1466 | 8 |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p009_ph0p52` | 94 | 1 | 0.1736 | 1.3271 | 0.0240 | 4 |
| seed_002.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p009_ph0p52` | 85 | 1 | 0.1960 | 1.3121 | 0.0225 | 3 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p52` | 200 | 0 | 0.0095 | 0.1456 | 0.1456 | 4 |
| seed_002.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p52` | 98 | 1 | 0.1699 | 1.3332 | 0.0251 | 5 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p32` | 78 | 1 | 0.1947 | 1.2026 | 0.0426 | 1 |
| seed_002.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p32` | 83 | 1 | 0.1922 | 1.2437 | 0.0325 | 2 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p005_ph0p3927` | 94 | 1 | 0.1696 | 1.3088 | 0.0295 | 4 |
| seed_002.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p005_ph0p3927` | 84 | 1 | 0.1865 | 1.2478 | 0.0375 | 2 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p01_ph0p32` | 93 | 1 | 0.1678 | 1.2813 | 0.0349 | 4 |
| seed_002.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p01_ph0p32` | 88 | 1 | 0.1892 | 1.3268 | 0.0227 | 3 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p32` | 85 | 1 | 0.1786 | 1.2438 | 0.0392 | 3 |
| seed_002.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p32` | 80 | 1 | 0.2009 | 1.2298 | 0.0323 | 2 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0_ph0p47` | 120 | 1 | 0.1285 | 1.2786 | 0.0373 | 6 |
| seed_002.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0_ph0p47` | 200 | 0 | 0.0109 | 0.1482 | 0.1457 | 9 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p012_ph0p43` | 132 | 1 | 0.1185 | 1.2714 | 0.0375 | 5 |
| seed_002.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p012_ph0p43` | 200 | 0 | 0.0110 | 0.1416 | 0.1445 | 9 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p009_ph0p43` | 92 | 1 | 0.1735 | 1.3096 | 0.0290 | 4 |
| seed_002.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p009_ph0p43` | 85 | 1 | 0.1933 | 1.2977 | 0.0254 | 3 |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p012_ph0p43` | 67 | 1 | 0.2341 | 1.2774 | 0.0370 | 0 |
| seed_002.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p012_ph0p43` | 86 | 1 | 0.1825 | 1.2502 | 0.0364 | 3 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p0075_ph0p47` | 99 | 1 | 0.1612 | 1.2965 | 0.0318 | 3 |
| seed_002.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p0075_ph0p47` | 91 | 1 | 0.1732 | 1.2704 | 0.0373 | 4 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p01_ph0p36` | 89 | 1 | 0.1795 | 1.2809 | 0.0294 | 3 |
| seed_002.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p01_ph0p36` | 89 | 1 | 0.1761 | 1.2542 | 0.0379 | 3 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0105_ph0p3927` | 74 | 1 | 0.2079 | 1.2397 | 0.0430 | 0 |
| seed_002.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0105_ph0p3927` | 81 | 1 | 0.1971 | 1.2249 | 0.0337 | 2 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p0035_ph0p36` | 94 | 1 | 0.1734 | 1.3293 | 0.0252 | 3 |
| seed_002.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p0035_ph0p36` | 88 | 1 | 0.1865 | 1.3021 | 0.0258 | 3 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p06_am0p0035_ph0p43` | 80 | 1 | 0.1932 | 1.2156 | 0.0365 | 2 |
| seed_002.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p06_am0p0035_ph0p43` | 78 | 1 | 0.2020 | 1.2224 | 0.0377 | 1 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927` | 200 | 0 | 0.0092 | 0.1896 | 0.1469 | 4 |
| seed_002.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927` | 200 | 0 | 0.0102 | 0.1246 | 0.1468 | 8 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p007_ph0p3927` | 90 | 1 | 0.1798 | 1.3198 | 0.0251 | 4 |
| seed_002.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p007_ph0p3927` | 87 | 1 | 0.1918 | 1.3294 | 0.0210 | 3 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p003_ph0p32` | 98 | 1 | 0.1629 | 1.2962 | 0.0317 | 3 |
| seed_002.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p04_am0p003_ph0p32` | 90 | 1 | 0.1859 | 1.3160 | 0.0208 | 4 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p04_am0p003_ph0p47` | 92 | 1 | 0.1674 | 1.2714 | 0.0382 | 3 |
| seed_002.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p04_am0p003_ph0p47` | 116 | 1 | 0.1338 | 1.2384 | 0.0409 | 9 |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p006_ph0p43` | 92 | 1 | 0.1804 | 1.3426 | 0.0193 | 4 |
| seed_002.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p006_ph0p43` | 86 | 1 | 0.1858 | 1.2900 | 0.0322 | 3 |
| seed_000.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p3927` | 109 | 1 | 0.1362 | 1.2088 | 0.0478 | 3 |
| seed_002.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p04_a0_ph0p3927` | 153 | 1 | 0.1019 | 1.2572 | 0.0397 | 9 |
| seed_000.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p01_ph0p43` | 87 | 1 | 0.1759 | 1.2606 | 0.0373 | 3 |
| seed_002.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p01_ph0p43` | 80 | 1 | 0.1884 | 1.1815 | 0.0473 | 2 |
| seed_000.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p16_ab0p04_am0p01_ph0p36` | 105 | 1 | 0.1479 | 1.2543 | 0.0401 | 4 |
| seed_002.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p16_ab0p04_am0p01_ph0p36` | 104 | 1 | 0.1588 | 1.3197 | 0.0289 | 6 |
| seed_000.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p0025_ph0p47` | 90 | 1 | 0.1771 | 1.3059 | 0.0280 | 4 |
| seed_002.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p0025_ph0p47` | 83 | 1 | 0.1910 | 1.2465 | 0.0345 | 2 |
| seed_000.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p006_ph0p3927` | 94 | 1 | 0.1663 | 1.2821 | 0.0336 | 4 |
| seed_002.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p006_ph0p3927` | 84 | 1 | 0.1917 | 1.2564 | 0.0309 | 2 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p3927` | 82 | 1 | 0.1895 | 1.2689 | 0.0339 | 2 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p3927` | 77 | 1 | 0.2076 | 1.2594 | 0.0322 | 1 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p01_ph0p36` | 83 | 1 | 0.1871 | 1.2646 | 0.0356 | 2 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p01_ph0p36` | 77 | 1 | 0.2097 | 1.2774 | 0.0298 | 1 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p16_ab0p04_am0p0075_ph0p36` | 101 | 1 | 0.1551 | 1.2481 | 0.0346 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p16_ab0p04_am0p0075_ph0p36` | 94 | 1 | 0.1711 | 1.3016 | 0.0355 | 4 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p04_a0_ph0p47` | 200 | 0 | 0.0111 | 0.1375 | 0.1464 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p04_a0_ph0p47` | 200 | 0 | 0.0127 | 0.1183 | 0.1458 | 8 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p01_ph0p3927` | 200 | 0 | 0.0108 | 0.1433 | 0.1469 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p04_am0p01_ph0p3927` | 200 | 0 | 0.0124 | 0.1053 | 0.1469 | 7 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p007_ph0p36` | 83 | 1 | 0.1944 | 1.3259 | 0.0245 | 2 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p007_ph0p36` | 77 | 1 | 0.2137 | 1.2963 | 0.0235 | 1 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0105_ph0p32` | 87 | 1 | 0.1805 | 1.2866 | 0.0328 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0105_ph0p32` | 78 | 1 | 0.2004 | 1.2709 | 0.0374 | 1 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p0035_ph0p32` | 104 | 1 | 0.1454 | 1.2088 | 0.0424 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p0035_ph0p32` | 106 | 1 | 0.1447 | 1.2323 | 0.0434 | 7 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p006_ph0p47` | 80 | 1 | 0.1921 | 1.2774 | 0.0372 | 2 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p006_ph0p47` | 75 | 1 | 0.2095 | 1.2433 | 0.0365 | 1 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p47` | 200 | 0 | 0.0119 | 0.1816 | 0.1461 | 4 |
| seed_002.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p47` | 200 | 0 | 0.0132 | 0.1349 | 0.1461 | 7 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p06_am0p0035_ph0p43` | 79 | 1 | 0.2019 | 1.3096 | 0.0282 | 1 |
| seed_002.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p035_kb0p06_k0p14_ab0p06_am0p0035_ph0p43` | 76 | 1 | 0.2124 | 1.2817 | 0.0296 | 1 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p006_ph0p36` | 103 | 1 | 0.1446 | 1.1848 | 0.0475 | 4 |
| seed_002.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p006_ph0p36` | 87 | 1 | 0.1800 | 1.2659 | 0.0393 | 3 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p52` | 200 | 0 | 0.0119 | 0.1808 | 0.1450 | 4 |
| seed_002.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p52` | 200 | 0 | 0.0134 | 0.1283 | 0.1457 | 8 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p06_a0_ph0p52` | 74 | 1 | 0.2000 | 1.1969 | 0.0465 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p06_a0_ph0p52` | 73 | 1 | 0.2088 | 1.1826 | 0.0444 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p012_ph0p52` | 200 | 0 | 0.0110 | 0.1654 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p6_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p04_am0p012_ph0p52` | 200 | 0 | 0.0125 | 0.1106 | 0.1471 | 7 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p36` | 83 | 1 | 0.1918 | 1.3139 | 0.0274 | 2 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p0025_ph0p36` | 77 | 1 | 0.2057 | 1.2656 | 0.0336 | 1 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p0025_ph0p3927` | 200 | 0 | 0.0123 | 0.1546 | 0.1445 | 5 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p04_am0p0025_ph0p3927` | 94 | 1 | 0.1729 | 1.2931 | 0.0326 | 4 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47` | 79 | 1 | 0.1961 | 1.3037 | 0.0331 | 1 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p06_am0p0035_ph0p47` | 78 | 1 | 0.2044 | 1.2675 | 0.0325 | 1 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p014_ph0p36` | 200 | 0 | 0.0122 | 0.1820 | 0.1438 | 5 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p04_am0p014_ph0p36` | 200 | 0 | 0.0135 | 0.1316 | 0.1441 | 8 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p06_am0p007_ph0p36` | 80 | 1 | 0.2022 | 1.3422 | 0.0228 | 2 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p06_am0p007_ph0p36` | 77 | 1 | 0.2074 | 1.2731 | 0.0317 | 1 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0_ph0p36` | 200 | 0 | 0.0116 | 0.1478 | 0.1443 | 5 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0_ph0p36` | 119 | 1 | 0.1355 | 1.2974 | 0.0328 | 8 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p04_am0p012_ph0p32` | 200 | 0 | 0.0121 | 0.1796 | 0.1442 | 4 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p04_am0p012_ph0p32` | 113 | 1 | 0.1410 | 1.2843 | 0.0342 | 8 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p06_am0p012_ph0p36` | 83 | 1 | 0.1976 | 1.3520 | 0.0197 | 2 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p06_am0p012_ph0p36` | 78 | 1 | 0.2114 | 1.3051 | 0.0236 | 1 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p01_ph0p36` | 5-29 | 0.1030 | 0.0686 | 0.3025 | 0.1484 | 0.0000 | 0.3729 | 0.0573 | 59 | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p06_am0p012_ph0p52` | 5-29 | 0.1020 | 0.0839 | 0.3072 | 0.1475 | 0.0000 | 0.8177 | 0.0584 | 50 | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p32` | 5-29 | 0.1009 | 0.0772 | 0.3029 | 0.1477 | 0.0000 | 0.4591 | 0.0574 | 54 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p01_ph0p32` | 5-29 | 0.0999 | 0.0711 | 0.3020 | 0.1478 | 0.0000 | 0.2953 | 0.0594 | 63 | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p009_ph0p43` | 5-29 | 0.0998 | 0.0676 | 0.3001 | 0.1478 | 0.0000 | 0.3526 | 0.0651 | 62 | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p06_am0p0105_ph0p47` | 5-29 | 0.0995 | 0.0768 | 0.2891 | 0.1487 | 0.0000 | 0.6857 | 0.0537 | 50 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p66_hrbm0p005_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p01_ph0p43` | 5-29 | 0.0994 | 0.0784 | 0.2987 | 0.1474 | 0.0000 | 0.4936 | 0.0540 | 57 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927` | 5-29 | 0.0990 | 0.0665 | 0.2851 | 0.1493 | 0.0000 | 0.3897 | 0.0609 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p014_ph0p36` | 0-24 | 0.0958 | 0.1893 | 0.2787 | 0.1484 | 0.0000 | 0.3918 | 0.0965 | 51 | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p62_hrb0_hb0p08_h0p035_kb0p06_k0p1_ab0p06_am0p0035_ph0p36` | 5-29 | 0.0948 | 0.0705 | 0.2867 | 0.1481 | 0.0000 | 0.3965 | 0.0651 | 56 | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p32` | 0-24 | 0.0943 | 0.1902 | 0.2815 | 0.1479 | 0.0000 | 0.4169 | 0.1059 | 53 | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p58_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p06_am0p012_ph0p52` | 0-24 | 0.0942 | 0.1774 | 0.2799 | 0.1476 | 0.0000 | 0.6228 | 0.1075 | 55 | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p6_hrbm0p005_hb0p08_h0p03_kb0p06_k0p16_ab0p06_am0p012_ph0p36` | 5-29 | 0.0941 | 0.0826 | 0.2861 | 0.1480 | 0.0000 | 0.6341 | 0.0541 | 53 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p52` | 5-29 | 0.0938 | 0.0662 | 0.2835 | 0.1482 | 0.0000 | 0.5330 | 0.0640 | 54 | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p009_ph0p36` | 5-29 | 0.0929 | 0.0688 | 0.2804 | 0.1486 | 0.0000 | 0.3965 | 0.0575 | 58 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p025_kb0p06_k0p1_ab0p06_am0p01_ph0p36` | 0-24 | 0.0928 | 0.1929 | 0.2704 | 0.1486 | 0.0000 | 0.3729 | 0.0991 | 64 | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p16_ab0p06_am0p0105_ph0p47` | 0-24 | 0.0928 | 0.1836 | 0.2606 | 0.1495 | 0.0000 | 0.5340 | 0.1063 | 55 | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p006_ph0p43` | 5-29 | 0.0927 | 0.0705 | 0.2799 | 0.1483 | 0.0000 | 0.3526 | 0.0614 | 62 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p66_hrb0_hb0p08_h0p03_kb0p06_k0p1_ab0p06_am0p009_ph0p43` | 0-24 | 0.0917 | 0.1897 | 0.2767 | 0.1480 | 0.0000 | 0.3016 | 0.0969 | 67 | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p025_kb0p06_k0p14_ab0p06_am0p01_ph0p36` | 5-29 | 0.0914 | 0.0669 | 0.2770 | 0.1482 | 0.0000 | 0.5549 | 0.0523 | 53 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927` | 0-24 | 0.0914 | 0.1806 | 0.2608 | 0.1493 | 0.0000 | 0.3897 | 0.0979 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p03_kb0p06_k0p12_ab0p06_am0p003_ph0p52` | 0-24 | 0.0907 | 0.1897 | 0.2672 | 0.1484 | 0.0000 | 0.4140 | 0.1003 | 59 | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0p005_hb0p08_h0p03_kb0p06_k0p14_ab0p06_am0p009_ph0p32` | 5-29 | 0.0907 | 0.0745 | 0.2743 | 0.1484 | 0.0000 | 0.7073 | 0.0559 | 53 | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p62_hrb0p005_hb0p08_h0p035_kb0p06_k0p12_ab0p04_am0p014_ph0p36` | 5-29 | 0.0906 | 0.0634 | 0.2650 | 0.1494 | 0.0000 | 0.4758 | 0.0563 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p62_hrbm0p005_hb0p08_h0p025_kb0p06_k0p12_ab0p06_am0p01_ph0p32` | 0-24 | 0.0905 | 0.1920 | 0.2694 | 0.1483 | 0.0000 | 0.4125 | 0.1046 | 59 | `{'01': 24.0, '11': 76.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
