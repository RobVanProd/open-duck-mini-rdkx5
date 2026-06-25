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
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p04_am0p009_ph0p3927` | 200 | 0 | 0.0036 | 0.1351 | 0.1502 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p04_am0p009_ph0p3927` | 200 | 0 | 0.0058 | 0.0904 | 0.1500 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p1_ab0p04_am0p015_ph0p589` | 200 | 0 | 0.0038 | 0.1726 | 0.1508 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p06_h0p05_kb0p03_k0p1_ab0p04_am0p015_ph0p589` | 200 | 0 | 0.0053 | 0.0954 | 0.1506 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p04_a0p015_ph0` | 200 | 0 | 0.0033 | 0.0791 | 0.1519 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0_hb0p08_h0p05_kb0p03_k0p08_ab0p04_a0p015_ph0` | 200 | 0 | 0.0046 | 0.1084 | 0.1518 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963` | 200 | 0 | 0.0066 | 0.2154 | 0.1455 | 2 |
| seed_002.jsonl | `primitive_p0p55_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963` | 200 | 0 | 0.0081 | 0.1846 | 0.1477 | 1 |
| seed_000.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p7854` | 200 | 0 | 0.0053 | 0.1894 | 0.1477 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p7854` | 200 | 0 | 0.0071 | 0.1238 | 0.1474 | 1 |
| seed_000.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p05_kb0p03_k0p08_ab0p08_a0p015_ph0p3927` | 200 | 0 | 0.0059 | 0.1818 | 0.1498 | 1 |
| seed_002.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p05_kb0p03_k0p08_ab0p08_a0p015_ph0p3927` | 200 | 0 | 0.0075 | 0.1373 | 0.1488 | 2 |
| seed_000.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p05_kb0p03_k0p1_ab0p04_a0_ph0p1963` | 200 | 0 | 0.0035 | 0.1494 | 0.1514 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p05_kb0p03_k0p1_ab0p04_a0_ph0p1963` | 200 | 0 | 0.0050 | 0.1110 | 0.1510 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p05_kb0p06_k0p12_ab0p08_a0_ph0` | 59 | 1 | 0.2772 | 1.3105 | 0.0265 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p05_kb0p06_k0p12_ab0p08_a0_ph0` | 77 | 1 | 0.2082 | 1.3195 | 0.0307 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p01_hb0p04_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927` | 200 | 0 | 0.0052 | 0.2011 | 0.1467 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p04_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927` | 200 | 0 | 0.0068 | 0.1373 | 0.1468 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p04_a0_ph0p1963` | 200 | 0 | 0.0037 | 0.1642 | 0.1491 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p04_a0_ph0p1963` | 200 | 0 | 0.0056 | 0.1209 | 0.1492 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p01_hb0p04_h0p04_kb0p06_k0p08_ab0p04_am0p012_ph0p3927` | 200 | 0 | 0.0049 | 0.1837 | 0.1477 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p04_h0p04_kb0p06_k0p08_ab0p04_am0p012_ph0p3927` | 200 | 0 | 0.0068 | 0.1428 | 0.1477 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p01_hb0p04_h0p04_kb0p06_k0p1_ab0p04_a0_ph0p1963` | 200 | 0 | 0.0046 | 0.1875 | 0.1473 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p04_h0p04_kb0p06_k0p1_ab0p04_a0_ph0p1963` | 200 | 0 | 0.0065 | 0.1406 | 0.1472 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p01_hb0p06_h0p04_kb0p06_k0p08_ab0p08_am0p012_ph0p3927` | 59 | 1 | 0.2751 | 1.3074 | 0.0275 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p06_h0p04_kb0p06_k0p08_ab0p08_am0p012_ph0p3927` | 200 | 0 | 0.0125 | 0.1646 | 0.1432 | 1 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p01_hb0p06_h0p05_kb0p06_k0p08_ab0p04_a0_ph0p589` | 200 | 0 | 0.0047 | 0.1744 | 0.1480 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p06_h0p05_kb0p06_k0p08_ab0p04_a0_ph0p589` | 200 | 0 | 0.0064 | 0.1167 | 0.1480 | 0 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p01_hb0p08_h0p04_kb0p03_k0p12_ab0p04_am0p012_ph0p1963` | 200 | 0 | 0.0036 | 0.1347 | 0.1498 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p08_h0p04_kb0p03_k0p12_ab0p04_am0p012_ph0p1963` | 200 | 0 | 0.0056 | 0.1496 | 0.1465 | 5 |
| seed_000.jsonl | `primitive_p0p55_hrbm0p01_hb0p08_h0p04_kb0p06_k0p1_ab0p04_a0p012_ph0p3927` | 200 | 0 | 0.0086 | 0.1281 | 0.1463 | 0 |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p08_h0p04_kb0p06_k0p1_ab0p04_a0p012_ph0p3927` | 91 | 1 | 0.1823 | 1.3164 | 0.0282 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hb0p04_h0p04_kb0p03_k0p12_ab0p04_a0_ph0p589` | 200 | 0 | 0.0043 | 0.1616 | 0.1499 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p04_h0p04_kb0p03_k0p12_ab0p04_a0_ph0p589` | 200 | 0 | 0.0059 | 0.1272 | 0.1494 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hb0p04_h0p04_kb0p06_k0p1_ab0p08_am0p012_ph0p3927` | 53 | 1 | 0.3090 | 1.3321 | 0.0236 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p04_h0p04_kb0p06_k0p1_ab0p08_am0p012_ph0p3927` | 200 | 0 | 0.0112 | 0.1930 | 0.1449 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hb0p04_h0p05_kb0p06_k0p1_ab0p04_a0p015_ph0p589` | 200 | 0 | 0.0047 | 0.1870 | 0.1482 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p04_h0p05_kb0p06_k0p1_ab0p04_a0p015_ph0p589` | 200 | 0 | 0.0066 | 0.1570 | 0.1473 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p08_a0_ph0p1963` | 200 | 0 | 0.0075 | 0.1820 | 0.1474 | 1 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p08_a0_ph0p1963` | 200 | 0 | 0.0095 | 0.1381 | 0.1471 | 3 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p04_kb0p03_k0p1_ab0p08_a0_ph0p7854` | 200 | 0 | 0.0065 | 0.1616 | 0.1476 | 1 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p04_kb0p03_k0p1_ab0p08_a0_ph0p7854` | 200 | 0 | 0.0089 | 0.1430 | 0.1465 | 3 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p05_kb0p03_k0p1_ab0p08_a0_ph0p3927` | 200 | 0 | 0.0085 | 0.1968 | 0.1480 | 1 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p05_kb0p03_k0p1_ab0p08_a0_ph0p3927` | 200 | 0 | 0.0092 | 0.1349 | 0.1449 | 2 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hb0p08_h0p04_kb0p03_k0p1_ab0p04_a0_ph0` | 200 | 0 | 0.0050 | 0.1100 | 0.1510 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p08_h0p04_kb0p03_k0p1_ab0p04_a0_ph0` | 200 | 0 | 0.0067 | 0.1314 | 0.1500 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hb0p08_h0p05_kb0p03_k0p1_ab0p08_a0p015_ph0p3927` | 79 | 1 | 0.2086 | 1.3376 | 0.0253 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p08_h0p05_kb0p03_k0p1_ab0p08_a0p015_ph0p3927` | 69 | 1 | 0.2345 | 1.3291 | 0.0297 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p04_h0p03_kb0p06_k0p08_ab0p08_am0p009_ph0` | 56 | 1 | 0.2879 | 1.3066 | 0.0321 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0p01_hb0p04_h0p03_kb0p06_k0p08_ab0p08_am0p009_ph0` | 200 | 0 | 0.0104 | 0.2044 | 0.1465 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963` | 200 | 0 | 0.0077 | 0.2150 | 0.1463 | 1 |
| seed_002.jsonl | `primitive_p0p5_hrb0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p08_am0p012_ph0p1963` | 200 | 0 | 0.0095 | 0.1766 | 0.1477 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p06_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p1963` | 200 | 0 | 0.0065 | 0.1774 | 0.1491 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0p01_hb0p06_h0p03_kb0p06_k0p08_ab0p04_am0p009_ph0p1963` | 200 | 0 | 0.0077 | 0.1062 | 0.1491 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0p012_ph0p589` | 102 | 1 | 0.1578 | 1.3051 | 0.0306 | 1 |
| seed_002.jsonl | `primitive_p0p5_hrb0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0p012_ph0p589` | 76 | 1 | 0.2161 | 1.3192 | 0.0306 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p06_h0p04_kb0p06_k0p1_ab0p08_a0_ph0p3927` | 55 | 1 | 0.2972 | 1.3194 | 0.0268 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0p01_hb0p06_h0p04_kb0p06_k0p1_ab0p08_a0_ph0p3927` | 82 | 1 | 0.1854 | 1.2178 | 0.0480 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p08_h0p04_kb0p06_k0p1_ab0p08_am0p012_ph0` | 54 | 1 | 0.2891 | 1.2566 | 0.0387 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0p01_hb0p08_h0p04_kb0p06_k0p1_ab0p08_am0p012_ph0` | 72 | 1 | 0.2209 | 1.2645 | 0.0343 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p08_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0p3927` | 200 | 0 | 0.0048 | 0.1190 | 0.1510 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0p01_hb0p08_h0p05_kb0p03_k0p12_ab0p04_a0p015_ph0p3927` | 200 | 0 | 0.0064 | 0.1665 | 0.1488 | 3 |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p08_h0p05_kb0p06_k0p08_ab0p04_a0p015_ph0p589` | 200 | 0 | 0.0090 | 0.1356 | 0.1483 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0p01_hb0p08_h0p05_kb0p06_k0p08_ab0p04_a0p015_ph0p589` | 200 | 0 | 0.0103 | 0.1377 | 0.1478 | 4 |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p08_h0p05_kb0p06_k0p12_ab0p08_a0p015_ph0p589` | 60 | 1 | 0.2380 | 1.1532 | 0.0521 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0p01_hb0p08_h0p05_kb0p06_k0p12_ab0p08_a0p015_ph0p589` | 61 | 1 | 0.2442 | 1.1710 | 0.0487 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrbm0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0_ph0p1963` | 129 | 1 | 0.1290 | 1.3480 | 0.0233 | 2 |
| seed_002.jsonl | `primitive_p0p5_hrbm0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0_ph0p1963` | 80 | 1 | 0.2076 | 1.3053 | 0.0298 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrbm0p01_hb0p06_h0p04_kb0p03_k0p1_ab0p08_a0p012_ph0p589` | 200 | 0 | 0.0071 | 0.1762 | 0.1465 | 2 |
| seed_002.jsonl | `primitive_p0p5_hrbm0p01_hb0p06_h0p04_kb0p03_k0p1_ab0p08_a0p012_ph0p589` | 86 | 1 | 0.1883 | 1.2779 | 0.0327 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrbm0p01_hb0p08_h0p03_kb0p03_k0p12_ab0p08_am0p009_ph0p3927` | 72 | 1 | 0.2281 | 1.3480 | 0.0209 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrbm0p01_hb0p08_h0p03_kb0p03_k0p12_ab0p08_am0p009_ph0p3927` | 70 | 1 | 0.2262 | 1.2789 | 0.0356 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p589` | 200 | 0 | 0.0078 | 0.1875 | 0.1471 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p589` | 200 | 0 | 0.0092 | 0.1391 | 0.1471 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p04_h0p04_kb0p03_k0p1_ab0p08_am0p012_ph0` | 61 | 1 | 0.2618 | 1.3128 | 0.0348 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p04_h0p04_kb0p03_k0p1_ab0p08_am0p012_ph0` | 200 | 0 | 0.0109 | 0.1835 | 0.1477 | 1 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p04_h0p05_kb0p06_k0p1_ab0p08_am0p015_ph0p1963` | 50 | 1 | 0.3280 | 1.3792 | 0.0209 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p04_h0p05_kb0p06_k0p1_ab0p08_am0p015_ph0p1963` | 200 | 0 | 0.0124 | 0.2224 | 0.1442 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p06_h0p04_kb0p06_k0p1_ab0p08_am0p012_ph0p589` | 56 | 1 | 0.2845 | 1.3049 | 0.0312 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p06_h0p04_kb0p06_k0p1_ab0p08_am0p012_ph0p589` | 98 | 1 | 0.1586 | 1.2362 | 0.0424 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p03_k0p1_ab0p04_a0p009_ph0p1963` | 200 | 0 | 0.0024 | 0.0992 | 0.1494 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p03_k0p1_ab0p04_a0p009_ph0p1963` | 200 | 0 | 0.0068 | 0.1383 | 0.1485 | 3 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p03_k0p1_ab0p08_am0p009_ph0p7854` | 84 | 1 | 0.1932 | 1.3241 | 0.0261 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p03_k0p1_ab0p08_am0p009_ph0p7854` | 80 | 1 | 0.2018 | 1.3131 | 0.0314 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927` | 200 | 0 | 0.0117 | 0.1646 | 0.1439 | 3 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927` | 200 | 0 | 0.0132 | 0.1359 | 0.1458 | 4 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p04_kb0p03_k0p1_ab0p08_am0p012_ph0p589` | 83 | 1 | 0.1996 | 1.3414 | 0.0192 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p04_kb0p03_k0p1_ab0p08_am0p012_ph0p589` | 81 | 1 | 0.2128 | 1.3740 | 0.0135 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p04_kb0p06_k0p08_ab0p08_am0p012_ph0` | 51 | 1 | 0.3048 | 1.2803 | 0.0349 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p04_kb0p06_k0p08_ab0p08_am0p012_ph0` | 81 | 1 | 0.1923 | 1.2433 | 0.0385 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p04_kb0p06_k0p12_ab0p08_a0p012_ph0p7854` | 67 | 1 | 0.2274 | 1.2428 | 0.0416 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p04_kb0p06_k0p12_ab0p08_a0p012_ph0p7854` | 67 | 1 | 0.2330 | 1.2415 | 0.0408 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrb0p01_hb0p04_h0p03_kb0p03_k0p1_ab0p04_a0_ph0p589` | 200 | 0 | 0.0052 | 0.1480 | 0.1512 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0p01_hb0p04_h0p03_kb0p03_k0p1_ab0p04_a0_ph0p589` | 200 | 0 | 0.0068 | 0.1052 | 0.1513 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrb0p01_hb0p04_h0p04_kb0p03_k0p08_ab0p08_a0_ph0` | 200 | 0 | 0.0084 | 0.1883 | 0.1495 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0p01_hb0p04_h0p04_kb0p03_k0p08_ab0p08_a0_ph0` | 200 | 0 | 0.0105 | 0.1749 | 0.1495 | 1 |
| seed_000.jsonl | `primitive_p0p6_hrb0p01_hb0p04_h0p05_kb0p03_k0p08_ab0p04_a0p015_ph0p589` | 200 | 0 | 0.0054 | 0.1429 | 0.1519 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0p01_hb0p04_h0p05_kb0p03_k0p08_ab0p04_a0p015_ph0p589` | 200 | 0 | 0.0070 | 0.0964 | 0.1518 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrb0p01_hb0p06_h0p04_kb0p06_k0p08_ab0p04_a0p012_ph0p589` | 200 | 0 | 0.0075 | 0.1507 | 0.1491 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0p01_hb0p06_h0p04_kb0p06_k0p08_ab0p04_a0p012_ph0p589` | 200 | 0 | 0.0076 | 0.1032 | 0.1486 | 1 |
| seed_000.jsonl | `primitive_p0p6_hrb0p01_hb0p06_h0p04_kb0p06_k0p12_ab0p08_a0_ph0p3927` | 50 | 1 | 0.3065 | 1.2782 | 0.0392 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0p01_hb0p06_h0p04_kb0p06_k0p12_ab0p08_a0_ph0p3927` | 78 | 1 | 0.2017 | 1.2561 | 0.0358 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrb0p01_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p589` | 165 | 1 | 0.0944 | 1.2356 | 0.0350 | 2 |
| seed_002.jsonl | `primitive_p0p6_hrb0p01_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p589` | 78 | 1 | 0.2057 | 1.3157 | 0.0316 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrb0p01_hb0p08_h0p04_kb0p03_k0p1_ab0p04_a0_ph0p1963` | 200 | 0 | 0.0056 | 0.1283 | 0.1514 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0p01_hb0p08_h0p04_kb0p03_k0p1_ab0p04_a0_ph0p1963` | 200 | 0 | 0.0073 | 0.1215 | 0.1504 | 1 |
| seed_000.jsonl | `primitive_p0p6_hrb0p01_hb0p08_h0p04_kb0p06_k0p12_ab0p08_a0p012_ph0` | 71 | 1 | 0.2128 | 1.2143 | 0.0450 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrb0p01_hb0p08_h0p04_kb0p06_k0p12_ab0p08_a0p012_ph0` | 70 | 1 | 0.2178 | 1.2186 | 0.0483 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p04_a0_ph0p3927` | 200 | 0 | 0.0061 | 0.1573 | 0.1491 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p01_hb0p04_h0p04_kb0p03_k0p12_ab0p04_a0_ph0p3927` | 200 | 0 | 0.0077 | 0.1096 | 0.1493 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p01_hb0p04_h0p04_kb0p06_k0p08_ab0p04_a0p012_ph0p3927` | 200 | 0 | 0.0070 | 0.1783 | 0.1477 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p01_hb0p04_h0p04_kb0p06_k0p08_ab0p04_a0p012_ph0p3927` | 200 | 0 | 0.0087 | 0.1326 | 0.1477 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p01_hb0p06_h0p03_kb0p03_k0p08_ab0p04_a0_ph0p3927` | 200 | 0 | 0.0049 | 0.1149 | 0.1511 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p01_hb0p06_h0p03_kb0p03_k0p08_ab0p04_a0_ph0p3927` | 200 | 0 | 0.0067 | 0.0864 | 0.1510 | 0 |
| seed_000.jsonl | `primitive_p0p6_hrbm0p01_hb0p08_h0p03_kb0p06_k0p1_ab0p08_a0_ph0p3927` | 73 | 1 | 0.2040 | 1.1903 | 0.0438 | 0 |
| seed_002.jsonl | `primitive_p0p6_hrbm0p01_hb0p08_h0p03_kb0p06_k0p1_ab0p08_a0_ph0p3927` | 72 | 1 | 0.2126 | 1.1961 | 0.0452 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0p03_k0p1_ab0p08_a0_ph0` | 60 | 1 | 0.2796 | 1.3729 | 0.0186 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0p03_k0p1_ab0p08_a0_ph0` | 200 | 0 | 0.0109 | 0.1684 | 0.1471 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p589` | 200 | 0 | 0.0072 | 0.1952 | 0.1469 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p04_h0p03_kb0p06_k0p12_ab0p04_a0p009_ph0p589` | 200 | 0 | 0.0090 | 0.1240 | 0.1469 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0_ph0p1963` | 100 | 1 | 0.1576 | 1.3101 | 0.0348 | 1 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0_ph0p1963` | 200 | 0 | 0.0125 | 0.1490 | 0.1465 | 1 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p04_kb0p06_k0p12_ab0p04_a0_ph0` | 200 | 0 | 0.0077 | 0.1732 | 0.1471 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p04_kb0p06_k0p12_ab0p04_a0_ph0` | 200 | 0 | 0.0110 | 0.1166 | 0.1471 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p06_k0p12_ab0p08_am0p015_ph0p3927` | 49 | 1 | 0.3023 | 1.1692 | 0.0477 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p06_h0p05_kb0p06_k0p12_ab0p08_am0p015_ph0p3927` | 88 | 1 | 0.1806 | 1.2600 | 0.0321 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0p04_a0p009_ph0p1963` | 200 | 0 | 0.0039 | 0.0636 | 0.1522 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p03_kb0p03_k0p08_ab0p04_a0p009_ph0p1963` | 200 | 0 | 0.0060 | 0.1048 | 0.1505 | 1 |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p1963` | 200 | 0 | 0.0126 | 0.1786 | 0.1446 | 3 |
| seed_002.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p1963` | 200 | 0 | 0.0142 | 0.1200 | 0.1449 | 1 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p04_h0p05_kb0p06_k0p12_ab0p08_a0_ph0p589` | 54 | 1 | 0.3000 | 1.3286 | 0.0228 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p01_hb0p04_h0p05_kb0p06_k0p12_ab0p08_a0_ph0p589` | 200 | 0 | 0.0141 | 0.2024 | 0.1434 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p04_h0p05_kb0p06_k0p12_ab0p08_am0p015_ph0p7854` | 57 | 1 | 0.2802 | 1.3319 | 0.0282 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p01_hb0p04_h0p05_kb0p06_k0p12_ab0p08_am0p015_ph0p7854` | 200 | 0 | 0.0125 | 0.2042 | 0.1438 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p03_kb0p03_k0p08_ab0p04_a0p009_ph0` | 200 | 0 | 0.0054 | 0.1077 | 0.1522 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p03_kb0p03_k0p08_ab0p04_a0p009_ph0` | 200 | 0 | 0.0071 | 0.0962 | 0.1523 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p03_kb0p06_k0p08_ab0p08_am0p009_ph0p589` | 63 | 1 | 0.2506 | 1.2942 | 0.0345 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p03_kb0p06_k0p08_ab0p08_am0p009_ph0p589` | 200 | 0 | 0.0133 | 0.1680 | 0.1458 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p04_kb0p03_k0p08_ab0p04_a0p012_ph0p3927` | 200 | 0 | 0.0049 | 0.1116 | 0.1523 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p04_kb0p03_k0p08_ab0p04_a0p012_ph0p3927` | 200 | 0 | 0.0069 | 0.0825 | 0.1523 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p04_a0_ph0p7854` | 200 | 0 | 0.0053 | 0.1539 | 0.1503 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p04_a0_ph0p7854` | 200 | 0 | 0.0070 | 0.0893 | 0.1505 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p04_kb0p03_k0p1_ab0p04_a0p012_ph0p3927` | 200 | 0 | 0.0048 | 0.1216 | 0.1512 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p04_kb0p03_k0p1_ab0p04_a0p012_ph0p3927` | 200 | 0 | 0.0073 | 0.0824 | 0.1511 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p04_kb0p06_k0p12_ab0p08_am0p012_ph0p7854` | 61 | 1 | 0.2688 | 1.3515 | 0.0237 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p04_kb0p06_k0p12_ab0p08_am0p012_ph0p7854` | 87 | 1 | 0.1797 | 1.2463 | 0.0370 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p05_kb0p06_k0p1_ab0p04_am0p015_ph0p589` | 200 | 0 | 0.0090 | 0.2082 | 0.1473 | 2 |
| seed_002.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p05_kb0p06_k0p1_ab0p04_am0p015_ph0p589` | 200 | 0 | 0.0101 | 0.1359 | 0.1477 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p1963` | 200 | 0 | 0.0120 | 0.1522 | 0.1466 | 3 |
| seed_002.jsonl | `primitive_p0p7_hrb0p01_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p1963` | 200 | 0 | 0.0134 | 0.1166 | 0.1467 | 3 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p01_hb0p04_h0p04_kb0p06_k0p08_ab0p04_a0_ph0p7854` | 200 | 0 | 0.0063 | 0.1699 | 0.1470 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p01_hb0p04_h0p04_kb0p06_k0p08_ab0p04_a0_ph0p7854` | 200 | 0 | 0.0081 | 0.1310 | 0.1469 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p01_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p015_ph0` | 200 | 0 | 0.0062 | 0.1494 | 0.1502 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p01_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p015_ph0` | 200 | 0 | 0.0083 | 0.0874 | 0.1503 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p01_hb0p08_h0p03_kb0p06_k0p1_ab0p08_a0_ph0p3927` | 71 | 1 | 0.2259 | 1.3109 | 0.0268 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p01_hb0p08_h0p03_kb0p06_k0p1_ab0p08_a0_ph0p3927` | 78 | 1 | 0.1966 | 1.2147 | 0.0470 | 0 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p01_hb0p08_h0p04_kb0p06_k0p08_ab0p04_a0p012_ph0p589` | 200 | 0 | 0.0106 | 0.1167 | 0.1469 | 0 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p01_hb0p08_h0p04_kb0p06_k0p08_ab0p04_a0p012_ph0p589` | 200 | 0 | 0.0118 | 0.1259 | 0.1465 | 4 |
| seed_000.jsonl | `primitive_p0p7_hrbm0p01_hb0p08_h0p05_kb0p06_k0p12_ab0p04_a0_ph0p589` | 117 | 1 | 0.1292 | 1.1907 | 0.0432 | 3 |
| seed_002.jsonl | `primitive_p0p7_hrbm0p01_hb0p08_h0p05_kb0p06_k0p12_ab0p04_a0_ph0p589` | 200 | 0 | 0.0703 | 1.1255 | 0.0623 | 4 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p06_h0p04_kb0p06_k0p08_ab0p08_am0p012_ph0p3927` | 0-49 | 0.0623 | 0.1660 | 0.3277 | 0.1450 | 0.0000 | 0.4546 | 0.0820 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p05_kb0p03_k0p1_ab0p08_a0_ph0p3927` | 0-49 | 0.0592 | 0.1689 | 0.3026 | 0.1479 | 0.0000 | 0.6266 | 0.0874 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p55_hrb0p01_hb0p06_h0p05_kb0p03_k0p08_ab0p08_a0p015_ph0p3927` | 0-49 | 0.0565 | 0.1820 | 0.2856 | 0.1495 | 0.0000 | 0.5605 | 0.0853 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927` | 5-54 | 0.0565 | 0.0636 | 0.3313 | 0.1462 | 0.0000 | 0.4800 | 0.0687 | None | `{'01': 6.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p08_h0p04_kb0p03_k0p12_ab0p04_am0p012_ph0p1963` | 0-49 | 0.0564 | 0.1668 | 0.2783 | 0.1479 | 0.0000 | 0.5365 | 0.0826 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p04_kb0p03_k0p1_ab0p08_a0_ph0p7854` | 0-49 | 0.0545 | 0.1826 | 0.2985 | 0.1474 | 0.0000 | 0.5520 | 0.0900 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_000.jsonl | `primitive_p0p7_hrbm0p01_hb0p08_h0p05_kb0p06_k0p12_ab0p04_a0_ph0p589` | 5-54 | 0.0543 | 0.0588 | 0.3190 | 0.1462 | 0.0000 | 0.5280 | 0.0700 | 62 | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p7_hrb0_hb0p08_h0p05_kb0p06_k0p12_ab0p04_am0p015_ph0p1963` | 5-54 | 0.0537 | 0.0635 | 0.3299 | 0.1462 | 0.0000 | 0.4481 | 0.0616 | None | `{'01': 6.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927` | 0-49 | 0.0537 | 0.1630 | 0.2780 | 0.1475 | 0.0000 | 0.5400 | 0.0817 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p03_kb0p03_k0p1_ab0p08_a0_ph0p1963` | 0-49 | 0.0532 | 0.1664 | 0.2893 | 0.1471 | 0.0000 | 0.5640 | 0.0870 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_000.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927` | 0-49 | 0.0532 | 0.1089 | 0.3173 | 0.1471 | 0.0000 | 0.5400 | 0.0843 | None | `{'01': 10.0, '11': 90.0}` |
| seed_000.jsonl | `primitive_p0p5_hrb0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0p012_ph0p589` | 0-49 | 0.0530 | 0.1104 | 0.3206 | 0.1470 | 0.0000 | 0.6666 | 0.0901 | 52 | `{'01': 10.0, '11': 90.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0p01_hb0p06_h0p03_kb0p06_k0p08_ab0p08_am0p009_ph0p589` | 0-49 | 0.0529 | 0.1803 | 0.3002 | 0.1467 | 0.0000 | 0.2978 | 0.0725 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p01_hb0p08_h0p04_kb0p06_k0p08_ab0p04_a0p012_ph0p589` | 10-59 | 0.0528 | 0.0371 | 0.2923 | 0.1469 | 0.0000 | 0.3583 | 0.0732 | None | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p5_hrbm0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0_ph0p1963` | 0-49 | 0.0526 | 0.1136 | 0.3130 | 0.1461 | 0.0000 | 0.6768 | 0.0902 | 79 | `{'01': 12.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p55_hrbm0p01_hb0p08_h0p04_kb0p03_k0p12_ab0p04_am0p012_ph0p1963` | 10-59 | 0.0525 | 0.0706 | 0.2921 | 0.1477 | 0.0000 | 0.6748 | 0.0772 | None | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p5_hrbm0p01_hb0p06_h0p04_kb0p03_k0p12_ab0p08_a0_ph0p1963` | 5-54 | 0.0522 | 0.0762 | 0.3197 | 0.1461 | 0.0000 | 0.7142 | 0.0798 | 74 | `{'01': 8.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hb0p06_h0p05_kb0p03_k0p1_ab0p08_a0_ph0p3927` | 5-54 | 0.0516 | 0.0747 | 0.3221 | 0.1475 | 0.0000 | 0.6266 | 0.0779 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p03_k0p1_ab0p04_a0p009_ph0p1963` | 0-49 | 0.0516 | 0.1639 | 0.2552 | 0.1507 | 0.0000 | 0.4377 | 0.0825 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927` | 10-59 | 0.0515 | 0.0507 | 0.3071 | 0.1466 | 0.0000 | 0.5400 | 0.0733 | None | `{'10': 2.0, '11': 98.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0p01_hb0p04_h0p05_kb0p06_k0p12_ab0p08_a0_ph0p589` | 5-54 | 0.0510 | 0.0580 | 0.3093 | 0.1453 | 0.0000 | 0.5280 | 0.0688 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p7_hrbm0p01_hb0p08_h0p05_kb0p06_k0p12_ab0p04_a0_ph0p589` | 10-59 | 0.0509 | 0.0380 | 0.2799 | 0.1465 | 0.0000 | 0.4694 | 0.0704 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p7_hrb0p01_hb0p04_h0p05_kb0p06_k0p12_ab0p08_a0_ph0p589` | 0-49 | 0.0506 | 0.1734 | 0.2965 | 0.1453 | 0.0000 | 0.4579 | 0.0726 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927` | 5-54 | 0.0505 | 0.0648 | 0.3017 | 0.1466 | 0.0000 | 0.4800 | 0.0718 | None | `{'10': 2.0, '11': 98.0}` |
| seed_000.jsonl | `primitive_p0p7_hrb0p01_hb0p08_h0p03_kb0p06_k0p1_ab0p04_a0_ph0p1963` | 5-54 | 0.0503 | 0.0570 | 0.3001 | 0.1482 | 0.0000 | 0.3657 | 0.0674 | None | `{'01': 6.0, '11': 94.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
