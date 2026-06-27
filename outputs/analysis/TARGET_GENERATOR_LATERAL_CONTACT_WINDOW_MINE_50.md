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
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0` | 200 | 0 | 0.0052 | 0.1798 | 0.1483 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0` | 200 | 0 | 0.0067 | 0.1458 | 0.1483 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 200 | 0 | 0.0073 | 0.2137 | 0.1432 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p03_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 200 | 0 | 0.0093 | 0.1848 | 0.1456 | 1 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0p3927` | 200 | 0 | 0.0032 | 0.1551 | 0.1500 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p04_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0p3927` | 200 | 0 | 0.0053 | 0.1218 | 0.1498 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p04_a0_ph0p3927` | 200 | 0 | 0.0036 | 0.1201 | 0.1516 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p04_a0_ph0p3927` | 200 | 0 | 0.0054 | 0.0858 | 0.1514 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p08_a0p009_ph0` | 200 | 0 | 0.0059 | 0.1626 | 0.1488 | 1 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p08_a0p009_ph0` | 200 | 0 | 0.0079 | 0.1306 | 0.1485 | 2 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p06_k0p08_ab0p08_a0p009_ph0p7854` | 79 | 1 | 0.2008 | 1.3056 | 0.0298 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p06_k0p08_ab0p08_a0p009_ph0p7854` | 87 | 1 | 0.1817 | 1.2608 | 0.0395 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p3927` | 200 | 0 | 0.0066 | 0.1898 | 0.1486 | 1 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p3927` | 200 | 0 | 0.0085 | 0.1441 | 0.1484 | 1 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0_ph0` | 78 | 1 | 0.2064 | 1.3109 | 0.0269 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0_ph0` | 120 | 1 | 0.1274 | 1.2183 | 0.0484 | 3 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0p015_ph0p7854` | 75 | 1 | 0.2076 | 1.2905 | 0.0326 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0p015_ph0p7854` | 79 | 1 | 0.2048 | 1.2995 | 0.0317 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p7854` | 105 | 1 | 0.1617 | 1.3770 | 0.0143 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p7854` | 90 | 1 | 0.1818 | 1.2943 | 0.0343 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p12_ab0p04_a0_ph0p3927` | 200 | 0 | 0.0034 | 0.1413 | 0.1506 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p12_ab0p04_a0_ph0p3927` | 200 | 0 | 0.0050 | 0.1642 | 0.1481 | 5 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p06_k0p12_ab0p08_a0p015_ph0p3927` | 65 | 1 | 0.2248 | 1.1815 | 0.0488 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p06_k0p12_ab0p08_a0p015_ph0p3927` | 65 | 1 | 0.2437 | 1.2470 | 0.0369 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p03_kb0p03_k0p12_ab0p04_a0p009_ph0p3927` | 200 | 0 | 0.0038 | 0.1319 | 0.1512 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p03_kb0p03_k0p12_ab0p04_a0p009_ph0p3927` | 200 | 0 | 0.0056 | 0.1185 | 0.1494 | 1 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0p3927` | 200 | 0 | 0.0045 | 0.1760 | 0.1489 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0p3927` | 200 | 0 | 0.0062 | 0.1407 | 0.1480 | 1 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p08_a0p015_ph0` | 58 | 1 | 0.2830 | 1.3348 | 0.0258 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p08_a0p015_ph0` | 73 | 1 | 0.2132 | 1.2565 | 0.0392 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p04_a0_ph0p7854` | 200 | 0 | 0.0035 | 0.0901 | 0.1526 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p04_a0_ph0p7854` | 200 | 0 | 0.0051 | 0.0965 | 0.1523 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p7854` | 200 | 0 | 0.0096 | 0.1781 | 0.1448 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p7854` | 200 | 0 | 0.0111 | 0.1540 | 0.1462 | 3 |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p08_a0_ph0` | 52 | 1 | 0.2998 | 1.2860 | 0.0354 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p08_a0_ph0` | 69 | 1 | 0.2200 | 1.1832 | 0.0461 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p04_h0p03_kb0p03_k0p12_ab0p04_a0p009_ph0` | 200 | 0 | 0.0038 | 0.1499 | 0.1488 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p04_h0p03_kb0p03_k0p12_ab0p04_a0p009_ph0` | 200 | 0 | 0.0058 | 0.1123 | 0.1478 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p04_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0` | 200 | 0 | 0.0033 | 0.1592 | 0.1487 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p04_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0` | 200 | 0 | 0.0054 | 0.1237 | 0.1487 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p04_h0p05_kb0p06_k0p08_ab0p04_a0p015_ph0` | 200 | 0 | 0.0041 | 0.1818 | 0.1471 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p04_h0p05_kb0p06_k0p08_ab0p04_a0p015_ph0` | 200 | 0 | 0.0065 | 0.1424 | 0.1472 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p06_h0p03_kb0p06_k0p12_ab0p08_a0_ph0p3927` | 75 | 1 | 0.2161 | 1.3513 | 0.0202 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p06_h0p03_kb0p06_k0p12_ab0p08_a0_ph0p3927` | 77 | 1 | 0.2064 | 1.2872 | 0.0337 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p04_a0p009_ph0` | 200 | 0 | 0.0077 | 0.1149 | 0.1465 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p04_a0p009_ph0` | 200 | 0 | 0.0098 | 0.1183 | 0.1457 | 5 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p08_a0_ph0` | 58 | 1 | 0.2710 | 1.2736 | 0.0324 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p08_a0_ph0` | 77 | 1 | 0.2175 | 1.3213 | 0.0197 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p3927` | 200 | 0 | 0.0088 | 0.1375 | 0.1450 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p3927` | 75 | 1 | 0.2155 | 1.3260 | 0.0301 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p08_ab0p04_a0_ph0` | 200 | 0 | 0.0030 | 0.0864 | 0.1508 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p08_ab0p04_a0_ph0` | 200 | 0 | 0.0054 | 0.1151 | 0.1505 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p08_ab0p08_a0_ph0p3927` | 84 | 1 | 0.2006 | 1.3450 | 0.0190 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p08_ab0p08_a0_ph0p3927` | 81 | 1 | 0.2145 | 1.3789 | 0.0154 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p12_ab0p04_am0p015_ph0` | 200 | 0 | 0.0037 | 0.1457 | 0.1493 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p12_ab0p04_am0p015_ph0` | 200 | 0 | 0.0060 | 0.1530 | 0.1470 | 4 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p7854` | 200 | 0 | 0.0070 | 0.2113 | 0.1465 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p7854` | 200 | 0 | 0.0090 | 0.1346 | 0.1466 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p03_kb0p03_k0p12_ab0p04_am0p009_ph0p7854` | 200 | 0 | 0.0052 | 0.1449 | 0.1498 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p03_kb0p03_k0p12_ab0p04_am0p009_ph0p7854` | 200 | 0 | 0.0070 | 0.0830 | 0.1499 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p03_kb0p06_k0p12_ab0p08_a0_ph0` | 63 | 1 | 0.2592 | 1.3379 | 0.0243 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p03_kb0p06_k0p12_ab0p08_a0_ph0` | 89 | 1 | 0.1798 | 1.2331 | 0.0323 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0p7854` | 200 | 0 | 0.0055 | 0.1721 | 0.1466 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0p7854` | 200 | 0 | 0.0120 | 0.1392 | 0.1464 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p06_k0p12_ab0p08_a0_ph0p7854` | 59 | 1 | 0.2675 | 1.3072 | 0.0307 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p06_k0p12_ab0p08_a0_ph0p7854` | 79 | 1 | 0.2011 | 1.2436 | 0.0361 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0p08_am0p009_ph0p3927` | 200 | 0 | 0.0126 | 0.1708 | 0.1475 | 3 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0p08_am0p009_ph0p3927` | 131 | 1 | 0.1309 | 1.3682 | 0.0181 | 4 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p12_ab0p08_am0p009_ph0` | 77 | 1 | 0.2069 | 1.2958 | 0.0348 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p12_ab0p08_am0p009_ph0` | 96 | 1 | 0.1706 | 1.3204 | 0.0283 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p12_ab0p08_am0p009_ph0p3927` | 80 | 1 | 0.1967 | 1.2640 | 0.0377 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p12_ab0p08_am0p009_ph0p3927` | 82 | 1 | 0.1875 | 1.1951 | 0.0473 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927` | 200 | 0 | 0.0103 | 0.1456 | 0.1476 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p3927` | 200 | 0 | 0.0120 | 0.0930 | 0.1476 | 2 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p08_am0p009_ph0p7854` | 72 | 1 | 0.2132 | 1.2493 | 0.0409 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p06_k0p08_ab0p08_am0p009_ph0p7854` | 82 | 1 | 0.1834 | 1.1645 | 0.0486 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0p02_hb0p04_h0p05_kb0p06_k0p12_ab0p08_am0p015_ph0p7854` | 54 | 1 | 0.3066 | 1.3785 | 0.0190 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p02_hb0p04_h0p05_kb0p06_k0p12_ab0p08_am0p015_ph0p7854` | 200 | 0 | 0.0126 | 0.2049 | 0.1435 | 2 |
| seed_000.jsonl | `primitive_p0p7_hrb0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p04_a0p009_ph0p7854` | 200 | 0 | 0.0042 | 0.0825 | 0.1532 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p04_a0p009_ph0p7854` | 200 | 0 | 0.0058 | 0.0937 | 0.1512 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p08_a0p015_ph0` | 63 | 1 | 0.2533 | 1.2960 | 0.0295 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p08_a0p015_ph0` | 79 | 1 | 0.2083 | 1.2958 | 0.0309 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p3927` | 200 | 0 | 0.0076 | 0.1911 | 0.1456 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p3927` | 200 | 0 | 0.0096 | 0.1164 | 0.1458 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p04_h0p03_kb0p06_k0p12_ab0p08_am0p009_ph0p3927` | 51 | 1 | 0.2932 | 1.2036 | 0.0435 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p04_h0p03_kb0p06_k0p12_ab0p08_am0p009_ph0p3927` | 200 | 0 | 0.0140 | 0.1985 | 0.1432 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p04_h0p05_kb0p03_k0p12_ab0p08_a0p015_ph0` | 67 | 1 | 0.2439 | 1.3487 | 0.0265 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p04_h0p05_kb0p03_k0p12_ab0p08_a0p015_ph0` | 200 | 0 | 0.0126 | 0.1718 | 0.1456 | 1 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0p015_ph0p7854` | 57 | 1 | 0.2855 | 1.3532 | 0.0203 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0p015_ph0p7854` | 87 | 1 | 0.1774 | 1.2302 | 0.0396 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0` | 200 | 0 | 0.0059 | 0.1639 | 0.1454 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p06_h0p05_kb0p06_k0p12_ab0p04_a0p015_ph0` | 200 | 0 | 0.0128 | 0.1338 | 0.1454 | 2 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p08_a0_ph0p7854` | 109 | 1 | 0.1528 | 1.3483 | 0.0228 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p08_a0_ph0p7854` | 90 | 1 | 0.1779 | 1.2834 | 0.0337 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p08_h0p05_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 66 | 1 | 0.2394 | 1.3032 | 0.0300 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p02_hb0p08_h0p05_kb0p06_k0p08_ab0p08_a0_ph0p3927` | 80 | 1 | 0.1942 | 1.2054 | 0.0437 | 0 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0_ph0` | 0-49 | 0.0625 | 0.1888 | 0.3301 | 0.1456 | 0.0000 | 0.5616 | 0.0866 | 70 | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p04_a0p009_ph0` | 0-49 | 0.0589 | 0.1651 | 0.3016 | 0.1462 | 0.0000 | 0.4139 | 0.0839 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p7854` | 5-54 | 0.0579 | 0.0626 | 0.3320 | 0.1481 | 0.0000 | 0.5682 | 0.0741 | 50 | `{'01': 6.0, '11': 94.0}` |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p7854` | 0-49 | 0.0568 | 0.1158 | 0.3281 | 0.1481 | 0.0000 | 0.5647 | 0.0824 | 55 | `{'01': 10.0, '11': 90.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0_ph0` | 5-54 | 0.0563 | 0.0620 | 0.3301 | 0.1456 | 0.0000 | 0.5604 | 0.0704 | 65 | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p08_a0_ph0p7854` | 5-54 | 0.0562 | 0.0524 | 0.3310 | 0.1473 | 0.0000 | 0.3746 | 0.0639 | 54 | `{'01': 8.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0p08_am0p009_ph0p3927` | 10-59 | 0.0553 | 0.0478 | 0.3138 | 0.1480 | 0.0000 | 0.3503 | 0.0657 | 71 | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p7854` | 0-49 | 0.0549 | 0.1611 | 0.2831 | 0.1478 | 0.0000 | 0.5818 | 0.0796 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p05_kb0p03_k0p12_ab0p04_am0p015_ph0` | 0-49 | 0.0545 | 0.1591 | 0.2554 | 0.1479 | 0.0000 | 0.6213 | 0.0815 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p7854` | 0-49 | 0.0541 | 0.1057 | 0.3159 | 0.1476 | 0.0000 | 0.5818 | 0.0834 | None | `{'01': 10.0, '11': 90.0}` |
| seed_000.jsonl | `primitive_p0p55_hrb0p02_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p7854` | 5-54 | 0.0539 | 0.0599 | 0.3226 | 0.1476 | 0.0000 | 0.6811 | 0.0728 | None | `{'01': 6.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p04_a0p009_ph0` | 10-59 | 0.0537 | 0.0534 | 0.3106 | 0.1457 | 0.0000 | 0.4560 | 0.0812 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p12_ab0p04_a0_ph0p3927` | 0-49 | 0.0532 | 0.1683 | 0.2634 | 0.1485 | 0.0000 | 0.5753 | 0.0858 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0p08_am0p009_ph0p3927` | 5-54 | 0.0527 | 0.0507 | 0.3183 | 0.1486 | 0.0000 | 0.3147 | 0.0644 | None | `{'01': 4.0, '11': 96.0}` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p04_a0p009_ph0` | 5-54 | 0.0522 | 0.0970 | 0.3105 | 0.1457 | 0.0000 | 0.3788 | 0.0810 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0p08_am0p009_ph0p3927` | 5-54 | 0.0518 | 0.0697 | 0.2997 | 0.1490 | 0.0000 | 0.3147 | 0.0657 | 76 | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0p08_am0p009_ph0p3927` | 0-49 | 0.0515 | 0.1739 | 0.2625 | 0.1490 | 0.0000 | 0.2951 | 0.0754 | 81 | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_000.jsonl | `primitive_p0p7_hrbm0p02_hb0p08_h0p03_kb0p03_k0p08_ab0p08_a0_ph0p7854` | 0-49 | 0.0514 | 0.1316 | 0.3236 | 0.1473 | 0.0000 | 0.2897 | 0.0725 | 59 | `{'01': 12.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p08_ab0p08_a0p009_ph0` | 0-49 | 0.0512 | 0.1725 | 0.2657 | 0.1490 | 0.0000 | 0.4139 | 0.0803 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0p02_hb0p04_h0p05_kb0p06_k0p12_ab0p08_am0p015_ph0p7854` | 0-49 | 0.0507 | 0.1714 | 0.3041 | 0.1454 | 0.0000 | 0.4481 | 0.0757 | None | `{'01': 4.0, '11': 96.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p06_k0p08_ab0p08_a0_ph0` | 10-59 | 0.0505 | 0.0432 | 0.3327 | 0.1456 | 0.0000 | 0.5690 | 0.0749 | 60 | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p02_hb0p08_h0p03_kb0p06_k0p08_ab0p04_a0p009_ph0` | 15-64 | 0.0492 | 0.0546 | 0.3111 | 0.1457 | 0.0000 | 0.3788 | 0.0792 | None | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0p08_am0p009_ph0p3927` | 0-49 | 0.0492 | 0.1303 | 0.3066 | 0.1486 | 0.0000 | 0.2951 | 0.0735 | None | `{'01': 8.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0p02_hb0p04_h0p05_kb0p06_k0p12_ab0p08_am0p015_ph0p7854` | 5-54 | 0.0487 | 0.0469 | 0.3045 | 0.1454 | 0.0000 | 0.5619 | 0.0678 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p08_ab0p08_am0p015_ph0p3927` | 0-49 | 0.0483 | 0.1657 | 0.2438 | 0.1495 | 0.0000 | 0.5605 | 0.0733 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
