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
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0` | 200 | 0 | 0.0052 | 0.1798 | 0.1483 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0` | 200 | 0 | 0.0067 | 0.1458 | 0.1483 | 2 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 200 | 0 | 0.0073 | 0.2137 | 0.1432 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 200 | 0 | 0.0093 | 0.1848 | 0.1456 | 4 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0p3927` | 200 | 0 | 0.0032 | 0.1551 | 0.1500 | 1 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0p3927` | 200 | 0 | 0.0053 | 0.1218 | 0.1498 | 3 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p04_a0_ph0p3927` | 200 | 0 | 0.0036 | 0.1201 | 0.1516 | 1 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p04_a0_ph0p3927` | 200 | 0 | 0.0054 | 0.0858 | 0.1514 | 3 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p08_a0p009_ph0` | 200 | 0 | 0.0059 | 0.1626 | 0.1488 | 3 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p08_a0p009_ph0` | 200 | 0 | 0.0079 | 0.1306 | 0.1485 | 5 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p06_k0p08_ab0p08_a0p009_ph0p7854` | 79 | 1 | 0.2008 | 1.3056 | 0.0298 | 1 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p06_k0p08_ab0p08_a0p009_ph0p7854` | 87 | 1 | 0.1817 | 1.2608 | 0.0395 | 3 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p3927` | 200 | 0 | 0.0066 | 0.1898 | 0.1486 | 3 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p3927` | 200 | 0 | 0.0085 | 0.1441 | 0.1484 | 3 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0_ph0` | 78 | 1 | 0.2064 | 1.3109 | 0.0269 | 1 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0_ph0` | 120 | 1 | 0.1274 | 1.2183 | 0.0484 | 4 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0p015_ph0p7854` | 75 | 1 | 0.2076 | 1.2905 | 0.0326 | 1 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0p015_ph0p7854` | 79 | 1 | 0.2048 | 1.2995 | 0.0317 | 1 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p7854` | 105 | 1 | 0.1617 | 1.3770 | 0.0143 | 4 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p7854` | 90 | 1 | 0.1818 | 1.2943 | 0.0343 | 4 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p12_ab0p04_a0_ph0p3927` | 200 | 0 | 0.0034 | 0.1413 | 0.1506 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p12_ab0p04_a0_ph0p3927` | 200 | 0 | 0.0050 | 0.1642 | 0.1481 | 5 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p06_k0p12_ab0p08_a0p015_ph0p3927` | 65 | 1 | 0.2248 | 1.1815 | 0.0488 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p06_k0p12_ab0p08_a0p015_ph0p3927` | 65 | 1 | 0.2437 | 1.2470 | 0.0369 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p03_kb0p03_k0p12_ab0p04_a0p009_ph0p3927` | 200 | 0 | 0.0038 | 0.1319 | 0.1512 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p03_kb0p03_k0p12_ab0p04_a0p009_ph0p3927` | 200 | 0 | 0.0056 | 0.1185 | 0.1494 | 5 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0p3927` | 200 | 0 | 0.0045 | 0.1760 | 0.1489 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0p3927` | 200 | 0 | 0.0062 | 0.1407 | 0.1480 | 5 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p08_a0p015_ph0` | 58 | 1 | 0.2830 | 1.3348 | 0.0258 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p08_a0p015_ph0` | 73 | 1 | 0.2132 | 1.2565 | 0.0392 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p04_a0_ph0p7854` | 200 | 0 | 0.0035 | 0.0901 | 0.1526 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p04_a0_ph0p7854` | 200 | 0 | 0.0051 | 0.0965 | 0.1523 | 4 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p7854` | 200 | 0 | 0.0096 | 0.1781 | 0.1448 | 4 |
| seed_002.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p7854` | 200 | 0 | 0.0111 | 0.1540 | 0.1462 | 7 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p08_a0_ph0` | 52 | 1 | 0.2998 | 1.2860 | 0.0354 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p08_a0_ph0` | 69 | 1 | 0.2200 | 1.1832 | 0.0461 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p04_h0p03_kb0p03_k0p12_ab0p04_a0p009_ph0` | 200 | 0 | 0.0038 | 0.1499 | 0.1488 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p04_h0p03_kb0p03_k0p12_ab0p04_a0p009_ph0` | 200 | 0 | 0.0058 | 0.1123 | 0.1478 | 4 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p04_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0` | 200 | 0 | 0.0033 | 0.1592 | 0.1487 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p04_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0` | 200 | 0 | 0.0054 | 0.1237 | 0.1487 | 3 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p04_h0p05_kb0p06_k0p08_ab0p04_a0p015_ph0` | 200 | 0 | 0.0041 | 0.1818 | 0.1471 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p04_h0p05_kb0p06_k0p08_ab0p04_a0p015_ph0` | 200 | 0 | 0.0065 | 0.1424 | 0.1472 | 3 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p06_h0p03_kb0p06_k0p12_ab0p08_a0_ph0p3927` | 75 | 1 | 0.2161 | 1.3513 | 0.0202 | 1 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p06_h0p03_kb0p06_k0p12_ab0p08_a0_ph0p3927` | 77 | 1 | 0.2064 | 1.2872 | 0.0337 | 1 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p04_a0p009_ph0` | 200 | 0 | 0.0077 | 0.1149 | 0.1465 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p04_a0p009_ph0` | 200 | 0 | 0.0098 | 0.1183 | 0.1457 | 7 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p08_a0_ph0` | 58 | 1 | 0.2710 | 1.2736 | 0.0324 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p08_a0_ph0` | 77 | 1 | 0.2175 | 1.3213 | 0.0197 | 1 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p3927` | 200 | 0 | 0.0088 | 0.1375 | 0.1450 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p3927` | 75 | 1 | 0.2155 | 1.3260 | 0.0301 | 1 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p08_ab0p04_a0_ph0` | 200 | 0 | 0.0030 | 0.0864 | 0.1508 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p08_ab0p04_a0_ph0` | 200 | 0 | 0.0054 | 0.1151 | 0.1505 | 3 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p08_ab0p08_a0_ph0p3927` | 84 | 1 | 0.2006 | 1.3450 | 0.0190 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p08_ab0p08_a0_ph0p3927` | 81 | 1 | 0.2145 | 1.3789 | 0.0154 | 2 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p12_ab0p04_am0p015_ph0` | 200 | 0 | 0.0037 | 0.1457 | 0.1493 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p12_ab0p04_am0p015_ph0` | 200 | 0 | 0.0060 | 0.1530 | 0.1470 | 5 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p7854` | 200 | 0 | 0.0070 | 0.2113 | 0.1465 | 3 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p7854` | 200 | 0 | 0.0090 | 0.1346 | 0.1466 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p03_kb0p03_k0p12_ab0p04_am0p009_ph0p7854` | 200 | 0 | 0.0052 | 0.1449 | 0.1498 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p03_kb0p03_k0p12_ab0p04_am0p009_ph0p7854` | 200 | 0 | 0.0070 | 0.0830 | 0.1499 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p03_kb0p06_k0p12_ab0p08_a0_ph0` | 63 | 1 | 0.2592 | 1.3379 | 0.0243 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p03_kb0p06_k0p12_ab0p08_a0_ph0` | 89 | 1 | 0.1798 | 1.2331 | 0.0323 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0p7854` | 200 | 0 | 0.0055 | 0.1721 | 0.1466 | 4 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0p7854` | 200 | 0 | 0.0120 | 0.1392 | 0.1464 | 7 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p06_k0p12_ab0p08_a0_ph0p7854` | 59 | 1 | 0.2675 | 1.3072 | 0.0307 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p06_k0p12_ab0p08_a0_ph0p7854` | 79 | 1 | 0.2011 | 1.2436 | 0.0361 | 1 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0p08_am0p009_ph0p3927` | 200 | 0 | 0.0126 | 0.1708 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0p08_am0p009_ph0p3927` | 131 | 1 | 0.1309 | 1.3682 | 0.0181 | 7 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p12_ab0p08_am0p009_ph0` | 77 | 1 | 0.2069 | 1.2958 | 0.0348 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p12_ab0p08_am0p009_ph0` | 96 | 1 | 0.1706 | 1.3204 | 0.0283 | 4 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p12_ab0p08_am0p009_ph0p3927` | 80 | 1 | 0.1967 | 1.2640 | 0.0377 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p12_ab0p08_am0p009_ph0p3927` | 82 | 1 | 0.1875 | 1.1951 | 0.0473 | 2 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927` | 200 | 0 | 0.0103 | 0.1456 | 0.1476 | 3 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927` | 200 | 0 | 0.0120 | 0.0930 | 0.1476 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p08_am0p009_ph0p7854` | 72 | 1 | 0.2132 | 1.2493 | 0.0409 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p08_am0p009_ph0p7854` | 82 | 1 | 0.1834 | 1.1645 | 0.0486 | 2 |
| seed_000.jsonl | `primitive_p0p7_hrb0p02_hb0p04_h0p05_kb0p06_k0p12_ab0p08_am0p015_ph0p7854` | 54 | 1 | 0.3066 | 1.3785 | 0.0190 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p02_hb0p04_h0p05_kb0p06_k0p12_ab0p08_am0p015_ph0p7854` | 200 | 0 | 0.0126 | 0.2049 | 0.1435 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrb0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p04_a0p009_ph0p7854` | 200 | 0 | 0.0042 | 0.0825 | 0.1532 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p04_a0p009_ph0p7854` | 200 | 0 | 0.0058 | 0.0937 | 0.1512 | 5 |
| seed_000.jsonl | `primitive_p0p7_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p08_a0p015_ph0` | 63 | 1 | 0.2533 | 1.2960 | 0.0295 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p08_a0p015_ph0` | 79 | 1 | 0.2083 | 1.2958 | 0.0309 | 1 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p3927` | 200 | 0 | 0.0076 | 0.1911 | 0.1456 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p3927` | 200 | 0 | 0.0096 | 0.1164 | 0.1458 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p04_h0p03_kb0p06_k0p12_ab0p08_am0p009_ph0p3927` | 51 | 1 | 0.2932 | 1.2036 | 0.0435 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p04_h0p03_kb0p06_k0p12_ab0p08_am0p009_ph0p3927` | 200 | 0 | 0.0140 | 0.1985 | 0.1432 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p04_h0p05_kb0p03_k0p12_ab0p08_a0p015_ph0` | 67 | 1 | 0.2439 | 1.3487 | 0.0265 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p04_h0p05_kb0p03_k0p12_ab0p08_a0p015_ph0` | 200 | 0 | 0.0126 | 0.1718 | 0.1456 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0p015_ph0p7854` | 57 | 1 | 0.2855 | 1.3532 | 0.0203 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0p015_ph0p7854` | 87 | 1 | 0.1774 | 1.2302 | 0.0396 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0` | 200 | 0 | 0.0059 | 0.1639 | 0.1454 | 5 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0` | 200 | 0 | 0.0128 | 0.1338 | 0.1454 | 6 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p08_a0_ph0p7854` | 109 | 1 | 0.1528 | 1.3483 | 0.0228 | 4 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p08_a0_ph0p7854` | 90 | 1 | 0.1779 | 1.2834 | 0.0337 | 4 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p08_h0p05_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 66 | 1 | 0.2394 | 1.3032 | 0.0300 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p08_h0p05_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 80 | 1 | 0.1942 | 1.2054 | 0.0437 | 2 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 5-29 | 0.1036 | 0.0754 | 0.3310 | 0.1465 | 0.0000 | 0.4681 | 0.0710 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0_ph0` | 0-24 | 0.1032 | 0.1986 | 0.2931 | 0.1469 | 0.0000 | 0.5616 | 0.0936 | 53 | `{'01': 24.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 0-24 | 0.0986 | 0.1718 | 0.3083 | 0.1465 | 0.0000 | 0.3400 | 0.0856 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p12_ab0p08_am0p009_ph0p3927` | 5-29 | 0.0985 | 0.0822 | 0.2898 | 0.1486 | 0.0000 | 0.3440 | 0.0597 | 50 | `{'01': 12.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0p02_hb0p04_h0p05_kb0p06_k0p12_ab0p08_am0p015_ph0p7854` | 0-24 | 0.0973 | 0.1885 | 0.2506 | 0.1482 | 0.0000 | 0.4454 | 0.0912 | None | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p06_h0p03_kb0p06_k0p12_ab0p08_a0_ph0p3927` | 0-24 | 0.0938 | 0.1861 | 0.3029 | 0.1459 | 0.0000 | 0.4917 | 0.0924 | 50 | `{'01': 24.0, '11': 76.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p03_kb0p06_k0p12_ab0p08_a0_ph0` | 0-24 | 0.0933 | 0.2212 | 0.2337 | 0.1478 | 0.0000 | 0.5378 | 0.0963 | 64 | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p04_h0p03_kb0p06_k0p12_ab0p08_am0p009_ph0p3927` | 0-24 | 0.0923 | 0.1856 | 0.2527 | 0.1459 | 0.0000 | 0.4113 | 0.0964 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p12_ab0p08_am0p009_ph0` | 0-24 | 0.0919 | 0.2020 | 0.2506 | 0.1507 | 0.0000 | 0.5378 | 0.1108 | 52 | `{'01': 20.0, '11': 80.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0_ph0` | 0-24 | 0.0919 | 0.2261 | 0.2201 | 0.1484 | 0.0000 | 0.5616 | 0.0945 | 95 | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0p08_am0p009_ph0p3927` | 5-29 | 0.0915 | 0.0733 | 0.2728 | 0.1489 | 0.0000 | 0.2688 | 0.0633 | None | `{'01': 8.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 0-24 | 0.0908 | 0.2062 | 0.2427 | 0.1472 | 0.0000 | 0.3400 | 0.0903 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p06_k0p08_ab0p08_a0p009_ph0p7854` | 0-24 | 0.0894 | 0.1943 | 0.2857 | 0.1470 | 0.0000 | 0.3549 | 0.0803 | 54 | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0p015_ph0p7854` | 0-24 | 0.0881 | 0.1913 | 0.2732 | 0.1477 | 0.0000 | 0.5614 | 0.0767 | 50 | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p12_ab0p08_am0p009_ph0p3927` | 0-24 | 0.0876 | 0.1902 | 0.2500 | 0.1491 | 0.0000 | 0.4113 | 0.1041 | 55 | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p7854` | 0-24 | 0.0874 | 0.1342 | 0.2786 | 0.1478 | 0.0000 | 0.3208 | 0.0898 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p7854` | 5-29 | 0.0872 | 0.0700 | 0.2796 | 0.1478 | 0.0000 | 0.4557 | 0.0686 | None | `{'01': 12.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p04_a0p009_ph0` | 20-44 | 0.0867 | 0.0531 | 0.2917 | 0.1466 | 0.0000 | 0.4332 | 0.0806 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p03_kb0p06_k0p12_ab0p08_a0_ph0` | 5-29 | 0.0863 | 0.1067 | 0.2639 | 0.1471 | 0.0000 | 0.3550 | 0.0568 | 59 | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0p02_hb0p04_h0p05_kb0p06_k0p12_ab0p08_am0p015_ph0p7854` | 5-29 | 0.0861 | 0.1100 | 0.2556 | 0.1482 | 0.0000 | 0.4575 | 0.0561 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p06_k0p08_ab0p08_a0p009_ph0p7854` | 10-34 | 0.0854 | 0.0626 | 0.2975 | 0.1457 | 0.0000 | 0.3420 | 0.0568 | 52 | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0p08_am0p009_ph0p3927` | 0-24 | 0.0849 | 0.1916 | 0.2442 | 0.1503 | 0.0000 | 0.2812 | 0.0883 | None | `{'01': 16.0, '11': 84.0}` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p08_h0p05_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 0-24 | 0.0849 | 0.2323 | 0.1916 | 0.1486 | 0.0000 | 0.4394 | 0.0905 | 55 | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p06_k0p12_ab0p08_a0_ph0p7854` | 0-24 | 0.0848 | 0.2087 | 0.2108 | 0.1486 | 0.0000 | 0.4454 | 0.0960 | 54 | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p06_k0p08_ab0p08_a0p009_ph0p7854` | 0-24 | 0.0838 | 0.2307 | 0.2224 | 0.1476 | 0.0000 | 0.3549 | 0.0933 | 62 | `{'01': 8.0, '10': 4.0, '11': 88.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
