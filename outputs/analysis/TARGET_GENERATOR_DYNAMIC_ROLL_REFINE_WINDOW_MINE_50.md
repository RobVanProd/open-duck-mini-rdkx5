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
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0078 | 0.1555 | 0.1473 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0096 | 0.0868 | 0.1471 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0081 | 0.1454 | 0.1483 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0099 | 0.0850 | 0.1484 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0045_ph0p45_ld0p34_ls0p65` | 200 | 0 | 0.0088 | 0.1487 | 0.1472 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0045_ph0p45_ld0p34_ls0p65` | 200 | 0 | 0.0107 | 0.0866 | 0.1471 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p45_ld0p3_ls0p65` | 200 | 0 | 0.0081 | 0.1338 | 0.1483 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p45_ld0p3_ls0p65` | 200 | 0 | 0.0102 | 0.0904 | 0.1482 | 2 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0080 | 0.1296 | 0.1487 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0100 | 0.0896 | 0.1486 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p45_ld0p3_ls0p65` | 200 | 0 | 0.0089 | 0.1543 | 0.1470 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p45_ld0p3_ls0p65` | 200 | 0 | 0.0108 | 0.0855 | 0.1466 | 2 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p58_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p37_ld0p26_ls0p75` | 200 | 0 | 0.0077 | 0.1520 | 0.1470 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p58_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p37_ld0p26_ls0p75` | 200 | 0 | 0.0097 | 0.0998 | 0.1473 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p58_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p3927_ld0p34_ls0p55` | 200 | 0 | 0.0083 | 0.1491 | 0.1472 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p58_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p3927_ld0p34_ls0p55` | 200 | 0 | 0.0102 | 0.0817 | 0.1470 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00825_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0081 | 0.1585 | 0.1467 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00825_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0100 | 0.0969 | 0.1472 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p45_ld0p34_ls0p55` | 200 | 0 | 0.0081 | 0.1576 | 0.1478 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p45_ld0p34_ls0p55` | 200 | 0 | 0.0099 | 0.0867 | 0.1479 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p26_ls0p55` | 200 | 0 | 0.0082 | 0.1481 | 0.1480 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p26_ls0p55` | 200 | 0 | 0.0100 | 0.0958 | 0.1479 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0083 | 0.1567 | 0.1473 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0103 | 0.0961 | 0.1476 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p45_ld0p3_ls0p75` | 200 | 0 | 0.0083 | 0.1458 | 0.1471 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p45_ld0p3_ls0p75` | 200 | 0 | 0.0102 | 0.1016 | 0.1476 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p3927_ld0p34_ls0p75` | 200 | 0 | 0.0082 | 0.1527 | 0.1473 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p3927_ld0p34_ls0p75` | 200 | 0 | 0.0103 | 0.1015 | 0.1479 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0085 | 0.1551 | 0.1464 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0107 | 0.1035 | 0.1469 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0076 | 0.1490 | 0.1475 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0096 | 0.0962 | 0.1479 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0083 | 0.1489 | 0.1470 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0103 | 0.0951 | 0.1473 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0083 | 0.1473 | 0.1468 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0101 | 0.0862 | 0.1459 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p26_ls0p55` | 200 | 0 | 0.0079 | 0.1386 | 0.1483 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p26_ls0p55` | 200 | 0 | 0.0101 | 0.0955 | 0.1481 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm1_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p45_ld0p34_ls0p75` | 200 | 0 | 0.0090 | 0.1524 | 0.1460 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm1_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p45_ld0p34_ls0p75` | 200 | 0 | 0.0110 | 0.1015 | 0.1464 | 2 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm1_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p34_ls0p65` | 200 | 0 | 0.0087 | 0.1488 | 0.1464 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm1_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p34_ls0p65` | 200 | 0 | 0.0110 | 0.0900 | 0.1462 | 2 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p42_ld0p3_ls0p55` | 200 | 0 | 0.0076 | 0.1385 | 0.1479 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p42_ld0p3_ls0p55` | 200 | 0 | 0.0096 | 0.0944 | 0.1480 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p34_ls0p65` | 200 | 0 | 0.0087 | 0.1660 | 0.1461 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p34_ls0p65` | 200 | 0 | 0.0102 | 0.0961 | 0.1449 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0077 | 0.1302 | 0.1483 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0095 | 0.0869 | 0.1484 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0085 | 0.1397 | 0.1465 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0105 | 0.0882 | 0.1454 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0082 | 0.1417 | 0.1474 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0102 | 0.0955 | 0.1476 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p34_ls0p75` | 200 | 0 | 0.0080 | 0.1581 | 0.1464 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p34_ls0p75` | 200 | 0 | 0.0099 | 0.0966 | 0.1471 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0079 | 0.1400 | 0.1481 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0101 | 0.0866 | 0.1483 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p26_ls0p75` | 200 | 0 | 0.0079 | 0.1424 | 0.1471 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p26_ls0p75` | 200 | 0 | 0.0099 | 0.0898 | 0.1468 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00825_ph0p42_ld0p3_ls0p75` | 200 | 0 | 0.0079 | 0.1429 | 0.1478 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00825_ph0p42_ld0p3_ls0p75` | 200 | 0 | 0.0100 | 0.0922 | 0.1482 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p0066_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0080 | 0.1364 | 0.1485 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p0066_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0100 | 0.0920 | 0.1486 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p0066_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0082 | 0.1432 | 0.1466 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p0066_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0104 | 0.1008 | 0.1472 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p58_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0076 | 0.1717 | 0.1467 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p58_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0095 | 0.0938 | 0.1467 | 2 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p42_ld0p34_ls0p75` | 200 | 0 | 0.0079 | 0.1626 | 0.1465 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p42_ld0p34_ls0p75` | 200 | 0 | 0.0098 | 0.1036 | 0.1467 | 2 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00825_ph0p34_ld0p34_ls0p55` | 200 | 0 | 0.0077 | 0.1387 | 0.1482 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00825_ph0p34_ld0p34_ls0p55` | 200 | 0 | 0.0093 | 0.0817 | 0.1478 | 3 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0075_ph0p42_ld0p26_ls0p75` | 200 | 0 | 0.0070 | 0.1400 | 0.1478 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0075_ph0p42_ld0p26_ls0p75` | 200 | 0 | 0.0090 | 0.0882 | 0.1477 | 2 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0076 | 0.1514 | 0.1469 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0096 | 0.0994 | 0.1470 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p58_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p37_ld0p26_ls0p55` | 200 | 0 | 0.0069 | 0.1429 | 0.1484 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p58_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p37_ld0p26_ls0p55` | 200 | 0 | 0.0087 | 0.0858 | 0.1482 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0074 | 0.1579 | 0.1466 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0094 | 0.1006 | 0.1469 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0073 | 0.1582 | 0.1466 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0093 | 0.1022 | 0.1468 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0071 | 0.1564 | 0.1478 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0089 | 0.0884 | 0.1479 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0071 | 0.1566 | 0.1473 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0088 | 0.0835 | 0.1475 | 2 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p45_ld0p34_ls0p65` | 200 | 0 | 0.0073 | 0.1500 | 0.1475 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p45_ld0p34_ls0p65` | 200 | 0 | 0.0092 | 0.0893 | 0.1480 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0074 | 0.1458 | 0.1479 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0095 | 0.0942 | 0.1481 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p9_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0069 | 0.1458 | 0.1475 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p9_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0092 | 0.1013 | 0.1479 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00495_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0073 | 0.1384 | 0.1485 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00495_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0093 | 0.0897 | 0.1486 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p45_ld0p26_ls0p55` | 200 | 0 | 0.0074 | 0.1451 | 0.1479 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p45_ld0p26_ls0p55` | 200 | 0 | 0.0094 | 0.0950 | 0.1477 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0069 | 0.1473 | 0.1475 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0089 | 0.0892 | 0.1479 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p3927_ld0p26_ls0p55` | 200 | 0 | 0.0068 | 0.1466 | 0.1480 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p3927_ld0p26_ls0p55` | 200 | 0 | 0.0086 | 0.0856 | 0.1481 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p3927_ld0p26_ls0p75` | 200 | 0 | 0.0068 | 0.1402 | 0.1480 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p3927_ld0p26_ls0p75` | 200 | 0 | 0.0090 | 0.0860 | 0.1484 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0068 | 0.1393 | 0.1480 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0088 | 0.0890 | 0.1483 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p34_ld0p34_ls0p55` | 200 | 0 | 0.0070 | 0.1388 | 0.1478 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p34_ld0p34_ls0p55` | 200 | 0 | 0.0090 | 0.0934 | 0.1480 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p34_ld0p26_ls0p55` | 200 | 0 | 0.0068 | 0.1511 | 0.1482 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p34_ld0p26_ls0p55` | 200 | 0 | 0.0089 | 0.0891 | 0.1481 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0075 | 0.1558 | 0.1461 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0096 | 0.0877 | 0.1461 | 3 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p26_ls0p55` | 200 | 0 | 0.0070 | 0.1498 | 0.1479 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p26_ls0p55` | 200 | 0 | 0.0090 | 0.0876 | 0.1478 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p34_ls0p65` | 200 | 0 | 0.0074 | 0.1708 | 0.1462 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p34_ls0p65` | 200 | 0 | 0.0094 | 0.1062 | 0.1468 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0075_ph0p45_ld0p26_ls0p75` | 200 | 0 | 0.0066 | 0.1402 | 0.1472 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0075_ph0p45_ld0p26_ls0p75` | 200 | 0 | 0.0087 | 0.0932 | 0.1479 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p42_ld0p3_ls0p75` | 200 | 0 | 0.0067 | 0.1450 | 0.1471 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p42_ld0p3_ls0p75` | 200 | 0 | 0.0087 | 0.0932 | 0.1481 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p9_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p0066_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0070 | 0.1427 | 0.1477 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p9_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p0066_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0092 | 0.0895 | 0.1482 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p9_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0071 | 0.1339 | 0.1477 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p9_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0093 | 0.0855 | 0.1482 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0071 | 0.1508 | 0.1472 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0091 | 0.0906 | 0.1475 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0070 | 0.1518 | 0.1471 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0090 | 0.0897 | 0.1470 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0073 | 0.1496 | 0.1466 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0094 | 0.1018 | 0.1469 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0071 | 0.1500 | 0.1475 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0089 | 0.0884 | 0.1472 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p34_ls0p65` | 200 | 0 | 0.0077 | 0.1715 | 0.1463 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p34_ls0p65` | 200 | 0 | 0.0096 | 0.0950 | 0.1464 | 2 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p58_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0074 | 0.1443 | 0.1480 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p58_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0090 | 0.0892 | 0.1479 | 2 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p75` | 200 | 0 | 0.0087 | 0.1621 | 0.1464 | 1 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p75` | 200 | 0 | 0.0107 | 0.0989 | 0.1464 | 2 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p37_ld0p26_ls0p65` | 200 | 0 | 0.0080 | 0.1482 | 0.1481 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p37_ld0p26_ls0p65` | 200 | 0 | 0.0099 | 0.0869 | 0.1480 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0076 | 0.1361 | 0.1484 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0098 | 0.0826 | 0.1483 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p42_ld0p3_ls0p55` | 200 | 0 | 0.0081 | 0.1601 | 0.1470 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p42_ld0p3_ls0p55` | 200 | 0 | 0.0100 | 0.0938 | 0.1464 | 2 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p9_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p45_ld0p34_ls0p75` | 200 | 0 | 0.0086 | 0.1487 | 0.1463 | 1 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p9_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p45_ld0p34_ls0p75` | 200 | 0 | 0.0105 | 0.0944 | 0.1458 | 3 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm1_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0075 | 0.1423 | 0.1481 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm1_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0098 | 0.0994 | 0.1483 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm1_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p34_ld0p34_ls0p75` | 200 | 0 | 0.0082 | 0.1513 | 0.1469 | 1 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm1_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p34_ld0p34_ls0p75` | 200 | 0 | 0.0103 | 0.0961 | 0.1472 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0077 | 0.1461 | 0.1474 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0094 | 0.0952 | 0.1466 | 4 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p34_ls0p65` | 200 | 0 | 0.0082 | 0.1619 | 0.1471 | 1 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p34_ls0p65` | 200 | 0 | 0.0101 | 0.0944 | 0.1472 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm1_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0083 | 0.1502 | 0.1467 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm1_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0103 | 0.0923 | 0.1460 | 3 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p3927_ld0p34_ls0p65` | 200 | 0 | 0.0082 | 0.1712 | 0.1461 | 1 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p3927_ld0p34_ls0p65` | 200 | 0 | 0.0103 | 0.0998 | 0.1462 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p042_hrphm0p9_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0072 | 0.1438 | 0.1480 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p042_hrphm0p9_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0093 | 0.0953 | 0.1486 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p58_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0075 | 0.1340 | 0.1468 | 1 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p58_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0096 | 0.0928 | 0.1471 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0073 | 0.1334 | 0.1476 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0093 | 0.0890 | 0.1481 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00525_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0076 | 0.1572 | 0.1460 | 1 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00525_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0096 | 0.1046 | 0.1468 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p34_ld0p34_ls0p55` | 200 | 0 | 0.0074 | 0.1521 | 0.1475 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p34_ld0p34_ls0p55` | 200 | 0 | 0.0094 | 0.0901 | 0.1479 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0072 | 0.1380 | 0.1472 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0092 | 0.0931 | 0.1472 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0074 | 0.1517 | 0.1470 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0094 | 0.0948 | 0.1469 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00495_ph0p34_ld0p34_ls0p65` | 200 | 0 | 0.0076 | 0.1425 | 0.1475 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00495_ph0p34_ld0p34_ls0p65` | 200 | 0 | 0.0096 | 0.0804 | 0.1475 | 2 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p37_ld0p26_ls0p55` | 200 | 0 | 0.0074 | 0.1407 | 0.1471 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p37_ld0p26_ls0p55` | 200 | 0 | 0.0096 | 0.0913 | 0.1463 | 2 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0077 | 0.1459 | 0.1472 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0098 | 0.0923 | 0.1473 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0074 | 0.1505 | 0.1478 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0094 | 0.0928 | 0.1482 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p0066_ph0p45_ld0p26_ls0p65` | 200 | 0 | 0.0073 | 0.1358 | 0.1478 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p0066_ph0p45_ld0p26_ls0p65` | 200 | 0 | 0.0094 | 0.0903 | 0.1479 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p3927_ld0p3_ls0p55` | 200 | 0 | 0.0076 | 0.1471 | 0.1468 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p3927_ld0p3_ls0p55` | 200 | 0 | 0.0095 | 0.0982 | 0.1465 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p42_ld0p34_ls0p75` | 200 | 0 | 0.0074 | 0.1535 | 0.1475 | 1 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p42_ld0p34_ls0p75` | 200 | 0 | 0.0092 | 0.0824 | 0.1477 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00825_ph0p34_ld0p34_ls0p75` | 200 | 0 | 0.0078 | 0.1598 | 0.1467 | 1 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00825_ph0p34_ld0p34_ls0p75` | 200 | 0 | 0.0100 | 0.0945 | 0.1472 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p3927_ld0p26_ls0p55` | 200 | 0 | 0.0075 | 0.1365 | 0.1472 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p3927_ld0p26_ls0p55` | 200 | 0 | 0.0095 | 0.0912 | 0.1466 | 2 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0077 | 0.1422 | 0.1476 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0098 | 0.0919 | 0.1473 | 2 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p45_ld0p34_ls0p55` | 200 | 0 | 0.0082 | 0.1492 | 0.1465 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p45_ld0p34_ls0p55` | 200 | 0 | 0.0102 | 0.0945 | 0.1459 | 3 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0081 | 0.1438 | 0.1476 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0102 | 0.0937 | 0.1475 | 1 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p34_ls0p65` | 0-49 | 0.0542 | 0.1847 | 0.2854 | 0.1467 | 0.0000 | 0.5529 | 0.0890 | None | `{'01': 10.0, '10': 4.0, '11': 86.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p34_ld0p3_ls0p65` | 0-49 | 0.0530 | 0.1670 | 0.2795 | 0.1472 | 0.0000 | 0.5536 | 0.0849 | None | `{'01': 10.0, '10': 4.0, '11': 86.0}` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p9_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p45_ld0p34_ls0p75` | 0-49 | 0.0519 | 0.1762 | 0.2692 | 0.1473 | 0.0000 | 0.4756 | 0.0863 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55` | 0-49 | 0.0515 | 0.1692 | 0.2777 | 0.1473 | 0.0000 | 0.5061 | 0.0861 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p37_ld0p34_ls0p75` | 0-49 | 0.0504 | 0.1783 | 0.2590 | 0.1474 | 0.0000 | 0.4869 | 0.0843 | None | `{'01': 6.0, '10': 4.0, '11': 90.0}` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p34_ld0p26_ls0p65` | 0-49 | 0.0504 | 0.1896 | 0.2708 | 0.1476 | 0.0000 | 0.4759 | 0.0858 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm1_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p55` | 0-49 | 0.0504 | 0.1720 | 0.2784 | 0.1466 | 0.0000 | 0.4757 | 0.0844 | None | `{'01': 6.0, '10': 2.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p45_ld0p34_ls0p55` | 0-49 | 0.0503 | 0.1720 | 0.2765 | 0.1467 | 0.0000 | 0.4998 | 0.0849 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p34_ls0p65` | 0-49 | 0.0501 | 0.1746 | 0.2568 | 0.1476 | 0.0000 | 0.5185 | 0.0846 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p37_ld0p26_ls0p55` | 0-49 | 0.0499 | 0.1664 | 0.2712 | 0.1470 | 0.0000 | 0.5719 | 0.0835 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm1_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p34_ls0p65` | 0-49 | 0.0495 | 0.1776 | 0.2600 | 0.1476 | 0.0000 | 0.5475 | 0.0841 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p42_ld0p34_ls0p55` | 0-49 | 0.0494 | 0.1725 | 0.2576 | 0.1479 | 0.0000 | 0.4625 | 0.0828 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p45_ld0p3_ls0p65` | 0-49 | 0.0494 | 0.1711 | 0.2622 | 0.1479 | 0.0000 | 0.5764 | 0.0827 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55` | 0-49 | 0.0493 | 0.1736 | 0.2603 | 0.1480 | 0.0000 | 0.4605 | 0.0823 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00825_ph0p34_ld0p34_ls0p55` | 0-49 | 0.0490 | 0.1888 | 0.2609 | 0.1484 | 0.0000 | 0.3929 | 0.0818 | None | `{'01': 6.0, '10': 4.0, '11': 90.0}` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p42_ld0p3_ls0p55` | 0-49 | 0.0490 | 0.1677 | 0.2687 | 0.1471 | 0.0000 | 0.4503 | 0.0834 | None | `{'01': 6.0, '10': 2.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p58_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p3927_ld0p34_ls0p55` | 0-49 | 0.0487 | 0.1770 | 0.2610 | 0.1480 | 0.0000 | 0.4570 | 0.0833 | None | `{'01': 6.0, '10': 2.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p75` | 0-49 | 0.0487 | 0.1708 | 0.2520 | 0.1479 | 0.0000 | 0.4743 | 0.0841 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm1_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p45_ld0p34_ls0p75` | 0-49 | 0.0487 | 0.1789 | 0.2488 | 0.1477 | 0.0000 | 0.5055 | 0.0852 | None | `{'01': 8.0, '10': 2.0, '11': 90.0}` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p3927_ld0p34_ls0p65` | 0-49 | 0.0486 | 0.1704 | 0.2574 | 0.1474 | 0.0000 | 0.5562 | 0.0855 | None | `{'01': 6.0, '10': 4.0, '11': 90.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p26_ls0p75` | 0-49 | 0.0486 | 0.1906 | 0.2557 | 0.1478 | 0.0000 | 0.4714 | 0.0839 | None | `{'01': 10.0, '10': 4.0, '11': 86.0}` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p3927_ld0p26_ls0p55` | 0-49 | 0.0484 | 0.1685 | 0.2670 | 0.1472 | 0.0000 | 0.5013 | 0.0833 | None | `{'01': 4.0, '10': 2.0, '11': 94.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 0-49 | 0.0484 | 0.1956 | 0.2511 | 0.1481 | 0.0000 | 0.4118 | 0.0848 | None | `{'01': 6.0, '10': 4.0, '11': 90.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p45_ld0p26_ls0p55` | 0-49 | 0.0482 | 0.1747 | 0.2525 | 0.1483 | 0.0000 | 0.4411 | 0.0807 | None | `{'01': 6.0, '10': 2.0, '11': 92.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p42_ld0p34_ls0p75` | 0-49 | 0.0482 | 0.1793 | 0.2476 | 0.1479 | 0.0000 | 0.3980 | 0.0832 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
