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
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0078 | 0.1555 | 0.1473 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0096 | 0.0868 | 0.1471 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0081 | 0.1454 | 0.1483 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0099 | 0.0850 | 0.1484 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0045_ph0p45_ld0p34_ls0p65` | 200 | 0 | 0.0088 | 0.1487 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0045_ph0p45_ld0p34_ls0p65` | 200 | 0 | 0.0107 | 0.0866 | 0.1471 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p45_ld0p3_ls0p65` | 200 | 0 | 0.0081 | 0.1338 | 0.1483 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p45_ld0p3_ls0p65` | 200 | 0 | 0.0102 | 0.0904 | 0.1482 | 4 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0080 | 0.1296 | 0.1487 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0100 | 0.0896 | 0.1486 | 4 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p45_ld0p3_ls0p65` | 200 | 0 | 0.0089 | 0.1543 | 0.1470 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p45_ld0p3_ls0p65` | 200 | 0 | 0.0108 | 0.0855 | 0.1466 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p58_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p37_ld0p26_ls0p75` | 200 | 0 | 0.0077 | 0.1520 | 0.1470 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p58_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p37_ld0p26_ls0p75` | 200 | 0 | 0.0097 | 0.0998 | 0.1473 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p58_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p3927_ld0p34_ls0p55` | 200 | 0 | 0.0083 | 0.1491 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p58_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p3927_ld0p34_ls0p55` | 200 | 0 | 0.0102 | 0.0817 | 0.1470 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00825_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0081 | 0.1585 | 0.1467 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00825_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0100 | 0.0969 | 0.1472 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p45_ld0p34_ls0p55` | 200 | 0 | 0.0081 | 0.1576 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p45_ld0p34_ls0p55` | 200 | 0 | 0.0099 | 0.0867 | 0.1479 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p26_ls0p55` | 200 | 0 | 0.0082 | 0.1481 | 0.1480 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p26_ls0p55` | 200 | 0 | 0.0100 | 0.0958 | 0.1479 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0083 | 0.1567 | 0.1473 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0103 | 0.0961 | 0.1476 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p45_ld0p3_ls0p75` | 200 | 0 | 0.0083 | 0.1458 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p45_ld0p3_ls0p75` | 200 | 0 | 0.0102 | 0.1016 | 0.1476 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p3927_ld0p34_ls0p75` | 200 | 0 | 0.0082 | 0.1527 | 0.1473 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p3927_ld0p34_ls0p75` | 200 | 0 | 0.0103 | 0.1015 | 0.1479 | 4 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0085 | 0.1551 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0107 | 0.1035 | 0.1469 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0076 | 0.1490 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0096 | 0.0962 | 0.1479 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0083 | 0.1489 | 0.1470 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0103 | 0.0951 | 0.1473 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0083 | 0.1473 | 0.1468 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0101 | 0.0862 | 0.1459 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p26_ls0p55` | 200 | 0 | 0.0079 | 0.1386 | 0.1483 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p26_ls0p55` | 200 | 0 | 0.0101 | 0.0955 | 0.1481 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm1_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p45_ld0p34_ls0p75` | 200 | 0 | 0.0090 | 0.1524 | 0.1460 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm1_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p45_ld0p34_ls0p75` | 200 | 0 | 0.0110 | 0.1015 | 0.1464 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm1_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p34_ls0p65` | 200 | 0 | 0.0087 | 0.1488 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm1_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p34_ls0p65` | 200 | 0 | 0.0110 | 0.0900 | 0.1462 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p42_ld0p3_ls0p55` | 200 | 0 | 0.0076 | 0.1385 | 0.1479 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p42_ld0p3_ls0p55` | 200 | 0 | 0.0096 | 0.0944 | 0.1480 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p34_ls0p65` | 200 | 0 | 0.0087 | 0.1660 | 0.1461 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p34_ls0p65` | 200 | 0 | 0.0102 | 0.0961 | 0.1449 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0077 | 0.1302 | 0.1483 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0095 | 0.0869 | 0.1484 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0085 | 0.1397 | 0.1465 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0105 | 0.0882 | 0.1454 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0082 | 0.1417 | 0.1474 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0102 | 0.0955 | 0.1476 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p34_ls0p75` | 200 | 0 | 0.0080 | 0.1581 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p34_ls0p75` | 200 | 0 | 0.0099 | 0.0966 | 0.1471 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0079 | 0.1400 | 0.1481 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0101 | 0.0866 | 0.1483 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p26_ls0p75` | 200 | 0 | 0.0079 | 0.1424 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p26_ls0p75` | 200 | 0 | 0.0099 | 0.0898 | 0.1468 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00825_ph0p42_ld0p3_ls0p75` | 200 | 0 | 0.0079 | 0.1429 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00825_ph0p42_ld0p3_ls0p75` | 200 | 0 | 0.0100 | 0.0922 | 0.1482 | 4 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p0066_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0080 | 0.1364 | 0.1485 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p0066_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0100 | 0.0920 | 0.1486 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p0066_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0082 | 0.1432 | 0.1466 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p0066_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0104 | 0.1008 | 0.1472 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p58_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0076 | 0.1717 | 0.1467 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p58_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0095 | 0.0938 | 0.1467 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p42_ld0p34_ls0p75` | 200 | 0 | 0.0079 | 0.1626 | 0.1465 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p42_ld0p34_ls0p75` | 200 | 0 | 0.0098 | 0.1036 | 0.1467 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00825_ph0p34_ld0p34_ls0p55` | 200 | 0 | 0.0077 | 0.1387 | 0.1482 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00825_ph0p34_ld0p34_ls0p55` | 200 | 0 | 0.0093 | 0.0817 | 0.1478 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0075_ph0p42_ld0p26_ls0p75` | 200 | 0 | 0.0070 | 0.1400 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0075_ph0p42_ld0p26_ls0p75` | 200 | 0 | 0.0090 | 0.0882 | 0.1477 | 4 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0076 | 0.1514 | 0.1469 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0096 | 0.0994 | 0.1470 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p58_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p37_ld0p26_ls0p55` | 200 | 0 | 0.0069 | 0.1429 | 0.1484 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p58_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p37_ld0p26_ls0p55` | 200 | 0 | 0.0087 | 0.0858 | 0.1482 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0074 | 0.1579 | 0.1466 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0094 | 0.1006 | 0.1469 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0073 | 0.1582 | 0.1466 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0093 | 0.1022 | 0.1468 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0071 | 0.1564 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0089 | 0.0884 | 0.1479 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0071 | 0.1566 | 0.1473 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0088 | 0.0835 | 0.1475 | 4 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p45_ld0p34_ls0p65` | 200 | 0 | 0.0073 | 0.1500 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p45_ld0p34_ls0p65` | 200 | 0 | 0.0092 | 0.0893 | 0.1480 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0074 | 0.1458 | 0.1479 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0095 | 0.0942 | 0.1481 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p9_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0069 | 0.1458 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p9_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0092 | 0.1013 | 0.1479 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00495_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0073 | 0.1384 | 0.1485 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00495_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0093 | 0.0897 | 0.1486 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p45_ld0p26_ls0p55` | 200 | 0 | 0.0074 | 0.1451 | 0.1479 | 3 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm1_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p45_ld0p26_ls0p55` | 200 | 0 | 0.0094 | 0.0950 | 0.1477 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0069 | 0.1473 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p26_ls0p65` | 200 | 0 | 0.0089 | 0.0892 | 0.1479 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p3927_ld0p26_ls0p55` | 200 | 0 | 0.0068 | 0.1466 | 0.1480 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p3927_ld0p26_ls0p55` | 200 | 0 | 0.0086 | 0.0856 | 0.1481 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p3927_ld0p26_ls0p75` | 200 | 0 | 0.0068 | 0.1402 | 0.1480 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p3927_ld0p26_ls0p75` | 200 | 0 | 0.0090 | 0.0860 | 0.1484 | 4 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0068 | 0.1393 | 0.1480 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p58_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0088 | 0.0890 | 0.1483 | 4 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p34_ld0p34_ls0p55` | 200 | 0 | 0.0070 | 0.1388 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p34_ld0p34_ls0p55` | 200 | 0 | 0.0090 | 0.0934 | 0.1480 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p34_ld0p26_ls0p55` | 200 | 0 | 0.0068 | 0.1511 | 0.1482 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p34_ld0p26_ls0p55` | 200 | 0 | 0.0089 | 0.0891 | 0.1481 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0075 | 0.1558 | 0.1461 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p37_ld0p34_ls0p75` | 200 | 0 | 0.0096 | 0.0877 | 0.1461 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p26_ls0p55` | 200 | 0 | 0.0070 | 0.1498 | 0.1479 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p26_ls0p55` | 200 | 0 | 0.0090 | 0.0876 | 0.1478 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p34_ls0p65` | 200 | 0 | 0.0074 | 0.1708 | 0.1462 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p34_ls0p65` | 200 | 0 | 0.0094 | 0.1062 | 0.1468 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0075_ph0p45_ld0p26_ls0p75` | 200 | 0 | 0.0066 | 0.1402 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p0075_ph0p45_ld0p26_ls0p75` | 200 | 0 | 0.0087 | 0.0932 | 0.1479 | 4 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p42_ld0p3_ls0p75` | 200 | 0 | 0.0067 | 0.1450 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p42_ld0p3_ls0p75` | 200 | 0 | 0.0087 | 0.0932 | 0.1481 | 4 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p9_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p0066_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0070 | 0.1427 | 0.1477 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p9_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p0066_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0092 | 0.0895 | 0.1482 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p9_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0071 | 0.1339 | 0.1477 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p9_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0093 | 0.0855 | 0.1482 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0071 | 0.1508 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0091 | 0.0906 | 0.1475 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0070 | 0.1518 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0090 | 0.0897 | 0.1470 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0073 | 0.1496 | 0.1466 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0094 | 0.1018 | 0.1469 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0071 | 0.1500 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0089 | 0.0884 | 0.1472 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p34_ls0p65` | 200 | 0 | 0.0077 | 0.1715 | 0.1463 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p34_ls0p65` | 200 | 0 | 0.0096 | 0.0950 | 0.1464 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p58_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0074 | 0.1443 | 0.1480 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p58_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p3927_ld0p3_ls0p75` | 200 | 0 | 0.0090 | 0.0892 | 0.1479 | 4 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p75` | 200 | 0 | 0.0087 | 0.1621 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p75` | 200 | 0 | 0.0107 | 0.0989 | 0.1464 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p37_ld0p26_ls0p65` | 200 | 0 | 0.0080 | 0.1482 | 0.1481 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p37_ld0p26_ls0p65` | 200 | 0 | 0.0099 | 0.0869 | 0.1480 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0076 | 0.1361 | 0.1484 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p006_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0098 | 0.0826 | 0.1483 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p42_ld0p3_ls0p55` | 200 | 0 | 0.0081 | 0.1601 | 0.1470 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p42_ld0p3_ls0p55` | 200 | 0 | 0.0100 | 0.0938 | 0.1464 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p9_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p45_ld0p34_ls0p75` | 200 | 0 | 0.0086 | 0.1487 | 0.1463 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p9_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p45_ld0p34_ls0p75` | 200 | 0 | 0.0105 | 0.0944 | 0.1458 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm1_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0075 | 0.1423 | 0.1481 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm1_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0098 | 0.0994 | 0.1483 | 4 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm1_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p34_ld0p34_ls0p75` | 200 | 0 | 0.0082 | 0.1513 | 0.1469 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm1_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p34_ld0p34_ls0p75` | 200 | 0 | 0.0103 | 0.0961 | 0.1472 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0077 | 0.1461 | 0.1474 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p34_ld0p26_ls0p65` | 200 | 0 | 0.0094 | 0.0952 | 0.1466 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p34_ls0p65` | 200 | 0 | 0.0082 | 0.1619 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm0p7854_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p34_ls0p65` | 200 | 0 | 0.0101 | 0.0944 | 0.1472 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm1_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0083 | 0.1502 | 0.1467 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p038_hrphm1_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0103 | 0.0923 | 0.1460 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p3927_ld0p34_ls0p65` | 200 | 0 | 0.0082 | 0.1712 | 0.1461 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p3927_ld0p34_ls0p65` | 200 | 0 | 0.0103 | 0.0998 | 0.1462 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p042_hrphm0p9_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0072 | 0.1438 | 0.1480 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p042_hrphm0p9_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0093 | 0.0953 | 0.1486 | 4 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p58_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0075 | 0.1340 | 0.1468 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p58_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p34_ld0p26_ls0p75` | 200 | 0 | 0.0096 | 0.0928 | 0.1471 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0073 | 0.1334 | 0.1476 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0093 | 0.0890 | 0.1481 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00525_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0076 | 0.1572 | 0.1460 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00525_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0096 | 0.1046 | 0.1468 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p34_ld0p34_ls0p55` | 200 | 0 | 0.0074 | 0.1521 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0045_ph0p34_ld0p34_ls0p55` | 200 | 0 | 0.0094 | 0.0901 | 0.1479 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0072 | 0.1380 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p45_ld0p3_ls0p55` | 200 | 0 | 0.0092 | 0.0931 | 0.1472 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0074 | 0.1517 | 0.1470 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p42_ld0p34_ls0p55` | 200 | 0 | 0.0094 | 0.0948 | 0.1469 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00495_ph0p34_ld0p34_ls0p65` | 200 | 0 | 0.0076 | 0.1425 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p12_ab0p04_a0p00495_ph0p34_ld0p34_ls0p65` | 200 | 0 | 0.0096 | 0.0804 | 0.1475 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p37_ld0p26_ls0p55` | 200 | 0 | 0.0074 | 0.1407 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p37_ld0p26_ls0p55` | 200 | 0 | 0.0096 | 0.0913 | 0.1463 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0077 | 0.1459 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm1_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0098 | 0.0923 | 0.1473 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0074 | 0.1505 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p58_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0094 | 0.0928 | 0.1482 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p0066_ph0p45_ld0p26_ls0p65` | 200 | 0 | 0.0073 | 0.1358 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p0066_ph0p45_ld0p26_ls0p65` | 200 | 0 | 0.0094 | 0.0903 | 0.1479 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p3927_ld0p3_ls0p55` | 200 | 0 | 0.0076 | 0.1471 | 0.1468 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p3927_ld0p3_ls0p55` | 200 | 0 | 0.0095 | 0.0982 | 0.1465 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p42_ld0p34_ls0p75` | 200 | 0 | 0.0074 | 0.1535 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p42_ld0p34_ls0p75` | 200 | 0 | 0.0092 | 0.0824 | 0.1477 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00825_ph0p34_ld0p34_ls0p75` | 200 | 0 | 0.0078 | 0.1598 | 0.1467 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00825_ph0p34_ld0p34_ls0p75` | 200 | 0 | 0.0100 | 0.0945 | 0.1472 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p3927_ld0p26_ls0p55` | 200 | 0 | 0.0075 | 0.1365 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p3927_ld0p26_ls0p55` | 200 | 0 | 0.0095 | 0.0912 | 0.1466 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0077 | 0.1422 | 0.1476 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00495_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0098 | 0.0919 | 0.1473 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p45_ld0p34_ls0p55` | 200 | 0 | 0.0082 | 0.1492 | 0.1465 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00495_ph0p45_ld0p34_ls0p55` | 200 | 0 | 0.0102 | 0.0945 | 0.1459 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0081 | 0.1438 | 0.1476 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0102 | 0.0937 | 0.1475 | 5 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p58_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p37_ld0p3_ls0p75` | 5-29 | 0.0808 | 0.0898 | 0.2735 | 0.1470 | 0.0000 | 0.4514 | 0.0610 | None | `{'01': 12.0, '10': 4.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p34_ls0p75` | 5-29 | 0.0798 | 0.0937 | 0.2774 | 0.1465 | 0.0000 | 0.4805 | 0.0625 | None | `{'01': 8.0, '10': 8.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p42_ld0p34_ls0p75` | 5-29 | 0.0790 | 0.0938 | 0.2697 | 0.1472 | 0.0000 | 0.4464 | 0.0629 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p37_ld0p34_ls0p75` | 5-29 | 0.0790 | 0.0896 | 0.2641 | 0.1476 | 0.0000 | 0.4522 | 0.0624 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p37_ld0p34_ls0p75` | 5-29 | 0.0788 | 0.0938 | 0.2713 | 0.1466 | 0.0000 | 0.5273 | 0.0620 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p75` | 5-29 | 0.0784 | 0.0909 | 0.2809 | 0.1468 | 0.0000 | 0.4994 | 0.0636 | None | `{'01': 8.0, '10': 8.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p58_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p0066_ph0p37_ld0p3_ls0p75` | 0-24 | 0.0773 | 0.1946 | 0.2242 | 0.1505 | 0.0000 | 0.3946 | 0.0954 | None | `{'01': 20.0, '10': 4.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p034_hrphm0p58_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p3_ls0p75` | 5-29 | 0.0771 | 0.0931 | 0.2674 | 0.1474 | 0.0000 | 0.4218 | 0.0598 | None | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p34_ls0p65` | 5-29 | 0.0769 | 0.0929 | 0.2646 | 0.1465 | 0.0000 | 0.5484 | 0.0615 | None | `{'01': 12.0, '10': 4.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p34_ls0p65` | 5-29 | 0.0769 | 0.0927 | 0.2629 | 0.1469 | 0.0000 | 0.5484 | 0.0612 | None | `{'01': 12.0, '10': 12.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p038_hrphm0p68_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00825_ph0p37_ld0p34_ls0p75` | 5-29 | 0.0768 | 0.0929 | 0.2672 | 0.1469 | 0.0000 | 0.4574 | 0.0625 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p9_hb0p08_h0p033_kb0p06_k0p14_ab0p04_a0p00825_ph0p34_ld0p34_ls0p75` | 5-29 | 0.0767 | 0.0940 | 0.2772 | 0.1467 | 0.0000 | 0.5005 | 0.0639 | None | `{'01': 8.0, '10': 8.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p033_kb0p06_k0p16_ab0p04_a0p00825_ph0p3927_ld0p3_ls0p75` | 5-29 | 0.0767 | 0.0924 | 0.2623 | 0.1470 | 0.0000 | 0.4497 | 0.0604 | None | `{'01': 12.0, '10': 4.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p046_hrphm0p68_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00525_ph0p37_ld0p3_ls0p75` | 5-29 | 0.0767 | 0.0997 | 0.2778 | 0.1463 | 0.0000 | 0.5752 | 0.0633 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p34_ld0p34_ls0p75` | 0-24 | 0.0762 | 0.1912 | 0.2221 | 0.1502 | 0.0000 | 0.4805 | 0.0892 | None | `{'01': 16.0, '10': 8.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p42_ld0p34_ls0p75` | 5-29 | 0.0761 | 0.0950 | 0.2699 | 0.1477 | 0.0000 | 0.4989 | 0.0632 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0075_ph0p42_ld0p34_ls0p75` | 0-24 | 0.0761 | 0.1886 | 0.2301 | 0.1488 | 0.0000 | 0.4358 | 0.0950 | None | `{'01': 16.0, '10': 8.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p034_hrphm0p68_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p0045_ph0p42_ld0p34_ls0p75` | 0-24 | 0.0760 | 0.1947 | 0.2214 | 0.1503 | 0.0000 | 0.3946 | 0.0945 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p046_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p34_ls0p65` | 0-24 | 0.0758 | 0.1900 | 0.2213 | 0.1493 | 0.0000 | 0.5340 | 0.0923 | None | `{'01': 20.0, '10': 4.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p034_hrphm1_hb0p08_h0p03_kb0p06_k0p14_ab0p04_a0p006_ph0p34_ld0p34_ls0p75` | 5-29 | 0.0756 | 0.0857 | 0.2692 | 0.1472 | 0.0000 | 0.4441 | 0.0633 | None | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p75` | 5-29 | 0.0756 | 0.0930 | 0.2591 | 0.1471 | 0.0000 | 0.4497 | 0.0600 | None | `{'01': 12.0, '10': 8.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p34_ls0p65` | 0-24 | 0.0755 | 0.1946 | 0.2219 | 0.1496 | 0.0000 | 0.5073 | 0.0920 | None | `{'01': 20.0, '10': 12.0, '11': 68.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p038_hrphm0p68_hb0p08_h0p03_kb0p06_k0p12_ab0p04_a0p0075_ph0p37_ld0p34_ls0p75` | 0-24 | 0.0750 | 0.1951 | 0.2183 | 0.1509 | 0.0000 | 0.4401 | 0.0859 | None | `{'01': 16.0, '10': 4.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p042_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p37_ld0p34_ls0p75` | 0-24 | 0.0748 | 0.1935 | 0.2187 | 0.1505 | 0.0000 | 0.4866 | 0.0940 | None | `{'01': 16.0, '10': 4.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p042_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p34_ld0p26_ls0p75` | 5-29 | 0.0748 | 0.0925 | 0.2580 | 0.1477 | 0.0000 | 0.4941 | 0.0593 | None | `{'01': 8.0, '11': 92.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
