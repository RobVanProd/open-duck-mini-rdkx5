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
- max_action_saturation_pct: `1.0`
- min_done_margin: `50`

## Trace Summary

| source | mode | samples | done_count | mean_vx | max_vx | min_height | candidates |
|---|---|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0095 | 0.1774 | 0.1463 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0109 | 0.0974 | 0.1458 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0080 | 0.1456 | 0.1482 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0097 | 0.0910 | 0.1480 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0086 | 0.1603 | 0.1469 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0104 | 0.0979 | 0.1468 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0082 | 0.1638 | 0.1463 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0102 | 0.1308 | 0.1467 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0082 | 0.1793 | 0.1456 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0100 | 0.1302 | 0.1467 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p3_ls0p55` | 200 | 0 | 0.0089 | 0.1659 | 0.1476 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p3_ls0p55` | 200 | 0 | 0.0104 | 0.0882 | 0.1471 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0095 | 0.1686 | 0.1465 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0118 | 0.1085 | 0.1441 | 7 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0085 | 0.1820 | 0.1466 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0102 | 0.0996 | 0.1470 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0080 | 0.1508 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0100 | 0.1082 | 0.1472 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0p7854_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0097 | 0.1649 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0p7854_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0117 | 0.1059 | 0.1457 | 7 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p24_ls0p75` | 200 | 0 | 0.0093 | 0.1866 | 0.1463 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p24_ls0p75` | 200 | 0 | 0.0111 | 0.0979 | 0.1467 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0063 | 0.1466 | 0.1476 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0085 | 0.0910 | 0.1475 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p36_ls1` | 200 | 0 | 0.0077 | 0.1729 | 0.1453 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p36_ls1` | 200 | 0 | 0.0097 | 0.1403 | 0.1467 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0064 | 0.1588 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0086 | 0.0898 | 0.1465 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0083 | 0.1463 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0100 | 0.0910 | 0.1459 | 7 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p36_ls1` | 200 | 0 | 0.0089 | 0.1656 | 0.1450 | 5 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p36_ls1` | 200 | 0 | 0.0107 | 0.1400 | 0.1463 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p47_ld0p36_ls1` | 200 | 0 | 0.0090 | 0.1666 | 0.1451 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p47_ld0p36_ls1` | 200 | 0 | 0.0110 | 0.1271 | 0.1461 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0086 | 0.1473 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0106 | 0.0952 | 0.1476 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm1p05_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p3_ls0p55` | 200 | 0 | 0.0091 | 0.1515 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm1p05_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p3_ls0p55` | 200 | 0 | 0.0111 | 0.0931 | 0.1463 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm1p05_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0088 | 0.1557 | 0.1474 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm1p05_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0108 | 0.1003 | 0.1476 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0085 | 0.1755 | 0.1467 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0101 | 0.1015 | 0.1475 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0090 | 0.1663 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0111 | 0.0960 | 0.1466 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p36_ls0p55` | 200 | 0 | 0.0102 | 0.1794 | 0.1462 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p36_ls0p55` | 200 | 0 | 0.0114 | 0.0849 | 0.1459 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0097 | 0.1736 | 0.1461 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0117 | 0.0976 | 0.1454 | 7 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0104 | 0.1787 | 0.1461 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0116 | 0.0921 | 0.1454 | 7 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p52_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0079 | 0.1600 | 0.1465 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p52_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0100 | 0.0903 | 0.1473 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls1` | 200 | 0 | 0.0066 | 0.1496 | 0.1468 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls1` | 200 | 0 | 0.0089 | 0.1005 | 0.1469 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0090 | 0.1865 | 0.1455 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0111 | 0.0931 | 0.1455 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p24_ls0p65` | 200 | 0 | 0.0078 | 0.1527 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p24_ls0p65` | 200 | 0 | 0.0099 | 0.0966 | 0.1474 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p36_ls0p65` | 200 | 0 | 0.0090 | 0.1611 | 0.1461 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p36_ls0p65` | 200 | 0 | 0.0110 | 0.1036 | 0.1464 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0077 | 0.1436 | 0.1482 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0098 | 0.0959 | 0.1481 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p34_ld0p3_ls1` | 200 | 0 | 0.0062 | 0.1502 | 0.1466 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p34_ld0p3_ls1` | 200 | 0 | 0.0093 | 0.1145 | 0.1468 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0076 | 0.1548 | 0.1462 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0094 | 0.1161 | 0.1467 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p42_ld0p36_ls0p65` | 200 | 0 | 0.0093 | 0.1943 | 0.1449 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p42_ld0p36_ls0p65` | 200 | 0 | 0.0106 | 0.1043 | 0.1458 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p34_ld0p36_ls1` | 80 | 1 | 0.2066 | 1.3167 | 0.0232 | 2 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0101 | 0.1294 | 0.1462 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0082 | 0.1724 | 0.1469 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0101 | 0.0997 | 0.1469 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0063_ph0p42_ld0p36_ls1` | 200 | 0 | 0.0093 | 0.1838 | 0.1452 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0063_ph0p42_ld0p36_ls1` | 200 | 0 | 0.0111 | 0.1240 | 0.1463 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p52_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0073 | 0.1517 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p52_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0089 | 0.0877 | 0.1478 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0079 | 0.1672 | 0.1458 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0098 | 0.0959 | 0.1469 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0075 | 0.1483 | 0.1465 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0096 | 0.1044 | 0.1467 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55` | 200 | 0 | 0.0090 | 0.1708 | 0.1440 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55` | 200 | 0 | 0.0106 | 0.1040 | 0.1445 | 6 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p34_ld0p3_ls1` | 200 | 0 | 0.0069 | 0.1689 | 0.1457 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p34_ld0p3_ls1` | 200 | 0 | 0.0093 | 0.1196 | 0.1468 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0081 | 0.1488 | 0.1480 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0098 | 0.0853 | 0.1481 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0074 | 0.1402 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0094 | 0.0866 | 0.1479 | 4 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0048_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0064 | 0.1527 | 0.1467 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0048_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0086 | 0.1079 | 0.1470 | 5 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0093 | 0.1681 | 0.1460 | 4 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0111 | 0.1011 | 0.1462 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0080 | 0.1702 | 0.1462 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0096 | 0.0946 | 0.1456 | 7 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0084 | 0.1875 | 0.1468 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0097 | 0.0888 | 0.1461 | 7 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0077 | 0.1514 | 0.1482 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0097 | 0.0878 | 0.1479 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0080 | 0.1700 | 0.1465 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0095 | 0.0895 | 0.1464 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0048_ph0p3927_ld0p36_ls0p65` | 200 | 0 | 0.0086 | 0.1767 | 0.1461 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0048_ph0p3927_ld0p36_ls0p65` | 200 | 0 | 0.0103 | 0.1045 | 0.1461 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0048_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0063 | 0.1526 | 0.1469 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0048_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0083 | 0.0871 | 0.1468 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p36_ls0p75` | 200 | 0 | 0.0082 | 0.1731 | 0.1462 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p36_ls0p75` | 200 | 0 | 0.0100 | 0.0926 | 0.1454 | 7 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0057_ph0p34_ld0p36_ls0p65` | 200 | 0 | 0.0086 | 0.1709 | 0.1458 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0057_ph0p34_ld0p36_ls0p65` | 200 | 0 | 0.0105 | 0.1086 | 0.1460 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p9_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0073 | 0.1607 | 0.1481 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p9_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0090 | 0.0993 | 0.1482 | 4 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0081 | 0.1549 | 0.1466 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0101 | 0.1012 | 0.1466 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p36_ls0p75` | 200 | 0 | 0.0082 | 0.1627 | 0.1462 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p36_ls0p75` | 200 | 0 | 0.0101 | 0.1038 | 0.1462 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrph0_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p3927_ld0p36_ls0p65` | 200 | 0 | 0.0079 | 0.1835 | 0.1469 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p036_hrph0_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p3927_ld0p36_ls0p65` | 200 | 0 | 0.0095 | 0.0926 | 0.1476 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p36_ls1` | 80 | 1 | 0.2121 | 1.3209 | 0.0149 | 2 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0099 | 0.1505 | 0.1459 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm0p68_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0069 | 0.1645 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm0p68_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0089 | 0.0883 | 0.1477 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm1p05_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0073 | 0.1386 | 0.1486 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm1p05_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0093 | 0.0880 | 0.1487 | 4 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm1p05_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p34_ld0p24_ls1` | 200 | 0 | 0.0056 | 0.1430 | 0.1480 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm1p05_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p34_ld0p24_ls1` | 200 | 0 | 0.0078 | 0.1119 | 0.1485 | 4 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p36_ls0p75` | 200 | 0 | 0.0070 | 0.1678 | 0.1460 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p36_ls0p75` | 200 | 0 | 0.0090 | 0.1037 | 0.1467 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65` | 200 | 0 | 0.0078 | 0.1815 | 0.1452 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65` | 200 | 0 | 0.0097 | 0.1005 | 0.1457 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p34_ld0p24_ls1` | 200 | 0 | 0.0064 | 0.1548 | 0.1461 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p34_ld0p24_ls1` | 200 | 0 | 0.0081 | 0.0880 | 0.1467 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0082 | 0.1882 | 0.1452 | 5 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0097 | 0.1077 | 0.1459 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0069 | 0.1512 | 0.1473 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0091 | 0.0871 | 0.1475 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 78 | 1 | 0.1981 | 1.2623 | 0.0373 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0095 | 0.0987 | 0.1459 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0091 | 0.1921 | 0.1455 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0105 | 0.1028 | 0.1448 | 7 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0072 | 0.1699 | 0.1459 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0090 | 0.0995 | 0.1464 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0068 | 0.1529 | 0.1463 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0090 | 0.0980 | 0.1464 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0074 | 0.1805 | 0.1454 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0097 | 0.1087 | 0.1460 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0_ph0p42_ld0p36_ls0p75` | 200 | 0 | 0.0076 | 0.1867 | 0.1459 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0_ph0p42_ld0p36_ls0p75` | 200 | 0 | 0.0094 | 0.0898 | 0.1464 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p75` | 200 | 0 | 0.0083 | 0.2095 | 0.1455 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p75` | 200 | 0 | 0.0097 | 0.1151 | 0.1461 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0084_ph0p3927_ld0p36_ls1` | 77 | 1 | 0.2121 | 1.3421 | 0.0231 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0084_ph0p3927_ld0p36_ls1` | 200 | 0 | 0.0098 | 0.1034 | 0.1455 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p42_ld0p36_ls1` | 113 | 1 | 0.1427 | 1.2865 | 0.0296 | 2 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p42_ld0p36_ls1` | 200 | 0 | 0.0112 | 0.1219 | 0.1456 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0074 | 0.1714 | 0.1460 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0091 | 0.1005 | 0.1471 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p36_ls1` | 200 | 0 | 0.0072 | 0.1793 | 0.1445 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p36_ls1` | 200 | 0 | 0.0091 | 0.1354 | 0.1464 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p65` | 200 | 0 | 0.0076 | 0.1626 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p65` | 200 | 0 | 0.0094 | 0.0964 | 0.1471 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0064 | 0.1424 | 0.1482 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0087 | 0.0999 | 0.1486 | 4 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p24_ls1` | 200 | 0 | 0.0058 | 0.1598 | 0.1468 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p24_ls1` | 200 | 0 | 0.0082 | 0.1219 | 0.1471 | 5 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0075 | 0.1532 | 0.1470 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0094 | 0.0989 | 0.1457 | 6 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0078 | 0.1417 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0099 | 0.0928 | 0.1477 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0079 | 0.1636 | 0.1483 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0095 | 0.0863 | 0.1483 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0084_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0085 | 0.1766 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p032_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0084_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0101 | 0.0963 | 0.1476 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0079 | 0.1591 | 0.1460 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0099 | 0.1170 | 0.1469 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0087 | 0.1552 | 0.1470 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0104 | 0.0818 | 0.1463 | 7 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0087 | 0.1327 | 0.1484 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0107 | 0.0871 | 0.1484 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p3_ls0p55` | 200 | 0 | 0.0091 | 0.1524 | 0.1471 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p3_ls0p55` | 200 | 0 | 0.0111 | 0.0921 | 0.1469 | 6 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0068 | 0.1547 | 0.1474 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0089 | 0.1177 | 0.1476 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0091 | 0.1848 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0109 | 0.0909 | 0.1475 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0094 | 0.1768 | 0.1467 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0112 | 0.1035 | 0.1469 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm0p52_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0071 | 0.1461 | 0.1483 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm0p52_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0087 | 0.0883 | 0.1483 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p42_ld0p3_ls0p55` | 200 | 0 | 0.0084 | 0.1515 | 0.1471 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p42_ld0p3_ls0p55` | 200 | 0 | 0.0100 | 0.0922 | 0.1446 | 8 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm1p05_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p3927_ld0p36_ls0p65` | 200 | 0 | 0.0094 | 0.1678 | 0.1464 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm1p05_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p3927_ld0p36_ls0p65` | 200 | 0 | 0.0116 | 0.1042 | 0.1464 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p3927_ld0p3_ls0p55` | 200 | 0 | 0.0076 | 0.1542 | 0.1476 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p3927_ld0p3_ls0p55` | 200 | 0 | 0.0095 | 0.0895 | 0.1479 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0079 | 0.1543 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0099 | 0.1128 | 0.1476 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0077 | 0.1735 | 0.1473 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0094 | 0.0942 | 0.1476 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0074 | 0.1482 | 0.1476 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0095 | 0.0955 | 0.1480 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0_ph0p34_ld0p24_ls0p75` | 200 | 0 | 0.0072 | 0.1466 | 0.1480 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0_ph0p34_ld0p24_ls0p75` | 200 | 0 | 0.0094 | 0.0939 | 0.1485 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p47_ld0p36_ls0p75` | 200 | 0 | 0.0092 | 0.1735 | 0.1456 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p47_ld0p36_ls0p75` | 200 | 0 | 0.0113 | 0.1086 | 0.1459 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p36_ls1` | 200 | 0 | 0.0070 | 0.1665 | 0.1455 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p36_ls1` | 200 | 0 | 0.0090 | 0.1270 | 0.1465 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0079 | 0.1853 | 0.1462 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0095 | 0.0911 | 0.1477 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0078 | 0.1656 | 0.1459 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0097 | 0.1437 | 0.1468 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0116 | 0.1933 | 0.1451 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0129 | 0.1142 | 0.1450 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0090 | 0.1793 | 0.1469 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0105 | 0.0903 | 0.1477 | 6 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p007_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0073 | 0.1463 | 0.1467 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p007_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0092 | 0.1008 | 0.1472 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0091 | 0.1681 | 0.1448 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0109 | 0.1185 | 0.1460 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0077 | 0.1495 | 0.1466 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0097 | 0.0861 | 0.1459 | 7 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0082 | 0.1584 | 0.1466 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0101 | 0.0877 | 0.1465 | 6 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p3927_ld0p36_ls0p55` | 200 | 0 | 0.0097 | 0.1760 | 0.1447 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p3927_ld0p36_ls0p55` | 100 | 1 | 0.1579 | 1.2658 | 0.0369 | 6 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p36_ls0p75` | 200 | 0 | 0.0089 | 0.1857 | 0.1460 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p36_ls0p75` | 200 | 0 | 0.0107 | 0.0978 | 0.1463 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p34_ld0p36_ls1` | 95 | 1 | 0.1713 | 1.3145 | 0.0271 | 2 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0125 | 0.1396 | 0.1457 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p52_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0072 | 0.1596 | 0.1473 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p52_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0093 | 0.0965 | 0.1479 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p68_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p55` | 200 | 0 | 0.0087 | 0.1609 | 0.1466 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p68_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p55` | 200 | 0 | 0.0105 | 0.0956 | 0.1467 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0096 | 0.1799 | 0.1455 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0116 | 0.1193 | 0.1459 | 5 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0083 | 0.1550 | 0.1469 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0101 | 0.0810 | 0.1460 | 7 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0074 | 0.1487 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0096 | 0.0995 | 0.1480 | 4 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p3_ls0p55` | 200 | 0 | 0.0084 | 0.1410 | 0.1482 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p3_ls0p55` | 200 | 0 | 0.0102 | 0.0819 | 0.1480 | 7 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0088 | 0.1549 | 0.1465 | 3 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0110 | 0.1067 | 0.1467 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0078 | 0.1429 | 0.1480 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0094 | 0.0946 | 0.1478 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0063_ph0p42_ld0p36_ls0p55` | 200 | 0 | 0.0087 | 0.1788 | 0.1461 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0063_ph0p42_ld0p36_ls0p55` | 200 | 0 | 0.0101 | 0.1006 | 0.1456 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0081 | 0.1421 | 0.1483 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0100 | 0.0942 | 0.1478 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0099 | 0.1926 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0112 | 0.0975 | 0.1457 | 7 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p47_ld0p36_ls0p75` | 200 | 0 | 0.0103 | 0.1702 | 0.1457 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p47_ld0p36_ls0p75` | 200 | 0 | 0.0117 | 0.1021 | 0.1451 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0064_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0072 | 0.1434 | 0.1473 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0064_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0087 | 0.1103 | 0.1468 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p36_ls0p55` | 200 | 0 | 0.0077 | 0.1575 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p36_ls0p55` | 200 | 0 | 0.0095 | 0.0937 | 0.1477 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0081 | 0.1408 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0100 | 0.0901 | 0.1466 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0085 | 0.1642 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0103 | 0.0981 | 0.1462 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0079 | 0.1416 | 0.1478 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0101 | 0.0976 | 0.1478 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm1p05_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0057_ph0p37_ld0p36_ls1` | 200 | 0 | 0.0091 | 0.1824 | 0.1455 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm1p05_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0057_ph0p37_ld0p36_ls1` | 200 | 0 | 0.0111 | 0.1290 | 0.1464 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm1p05_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0063_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0084 | 0.1588 | 0.1466 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm1p05_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0063_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0104 | 0.1085 | 0.1469 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p36_ls1` | 200 | 0 | 0.0080 | 0.1790 | 0.1462 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p36_ls1` | 200 | 0 | 0.0096 | 0.1042 | 0.1467 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls1` | 200 | 0 | 0.0068 | 0.1583 | 0.1470 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls1` | 200 | 0 | 0.0091 | 0.1194 | 0.1473 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0063_ph0p34_ld0p36_ls1` | 74 | 1 | 0.2298 | 1.3471 | 0.0142 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0063_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0111 | 0.1276 | 0.1460 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p34_ld0p24_ls1` | 200 | 0 | 0.0083 | 0.1493 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p34_ld0p24_ls1` | 200 | 0 | 0.0107 | 0.1060 | 0.1476 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p34_ld0p24_ls0p65` | 200 | 0 | 0.0077 | 0.1612 | 0.1477 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p34_ld0p24_ls0p65` | 200 | 0 | 0.0097 | 0.0951 | 0.1477 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p65` | 200 | 0 | 0.0079 | 0.1608 | 0.1470 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p65` | 200 | 0 | 0.0099 | 0.0955 | 0.1467 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p52_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p65` | 200 | 0 | 0.0077 | 0.1673 | 0.1472 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p52_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p65` | 200 | 0 | 0.0095 | 0.0919 | 0.1474 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0075 | 0.1459 | 0.1477 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0097 | 0.0930 | 0.1477 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0087 | 0.1481 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0107 | 0.0969 | 0.1461 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0078 | 0.1401 | 0.1480 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0097 | 0.0946 | 0.1479 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0081 | 0.1409 | 0.1475 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0102 | 0.0902 | 0.1476 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p24_ls0p65` | 200 | 0 | 0.0074 | 0.1367 | 0.1482 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p24_ls0p65` | 200 | 0 | 0.0094 | 0.0982 | 0.1481 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0094 | 0.1642 | 0.1459 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0112 | 0.1064 | 0.1458 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0084_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0070 | 0.1394 | 0.1479 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0084_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0091 | 0.1034 | 0.1483 | 4 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm1p05_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0077 | 0.1356 | 0.1481 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm1p05_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0098 | 0.0950 | 0.1478 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p42_ld0p3_ls0p75` | 200 | 0 | 0.0078 | 0.1497 | 0.1463 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p42_ld0p3_ls0p75` | 200 | 0 | 0.0096 | 0.0932 | 0.1461 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls1` | 200 | 0 | 0.0070 | 0.1505 | 0.1464 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls1` | 200 | 0 | 0.0088 | 0.1139 | 0.1468 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0076 | 0.1608 | 0.1460 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0095 | 0.1008 | 0.1468 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0105_ph0p3927_ld0p24_ls0p55` | 200 | 0 | 0.0069 | 0.1384 | 0.1477 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0105_ph0p3927_ld0p24_ls0p55` | 200 | 0 | 0.0089 | 0.1038 | 0.1472 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0075 | 0.1506 | 0.1468 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0094 | 0.0871 | 0.1467 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrph0_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p008_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0073 | 0.1311 | 0.1483 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrph0_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p008_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0095 | 0.0988 | 0.1486 | 4 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0092 | 0.1976 | 0.1457 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0110 | 0.1066 | 0.1461 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0073 | 0.1526 | 0.1471 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0093 | 0.0944 | 0.1475 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p34_ld0p36_ls0p65` | 200 | 0 | 0.0089 | 0.1700 | 0.1454 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p34_ld0p36_ls0p65` | 200 | 0 | 0.0108 | 0.1027 | 0.1445 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p47_ld0p36_ls0p65` | 200 | 0 | 0.0078 | 0.1678 | 0.1466 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p47_ld0p36_ls0p65` | 200 | 0 | 0.0097 | 0.0912 | 0.1468 | 6 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0082 | 0.1609 | 0.1461 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0102 | 0.1248 | 0.1465 | 5 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p3927_ld0p24_ls1` | 200 | 0 | 0.0058 | 0.1422 | 0.1481 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p3927_ld0p24_ls1` | 200 | 0 | 0.0081 | 0.1015 | 0.1486 | 4 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p36_ls1` | 200 | 0 | 0.0090 | 0.1739 | 0.1455 | 4 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p36_ls1` | 200 | 0 | 0.0107 | 0.1256 | 0.1465 | 5 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p36_ls1` | 5-29 | 0.1006 | 0.1085 | 0.3290 | 0.1454 | 0.0000 | 0.8260 | 0.0802 | 50 | `{'01': 12.0, '10': 4.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p42_ld0p36_ls1` | 5-29 | 0.0987 | 0.1213 | 0.3163 | 0.1456 | 0.0000 | 0.9363 | 0.0784 | 83 | `{'01': 28.000000000000004, '11': 72.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p34_ld0p36_ls1` | 5-29 | 0.0981 | 0.1136 | 0.3278 | 0.1453 | 0.0000 | 0.5784 | 0.0788 | 50 | `{'01': 12.0, '10': 12.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p34_ld0p36_ls1` | 5-29 | 0.0979 | 0.1174 | 0.2989 | 0.1461 | 0.0000 | 0.4321 | 0.0749 | 65 | `{'01': 28.000000000000004, '11': 72.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p75` | 5-29 | 0.0974 | 0.0959 | 0.3172 | 0.1456 | 0.0000 | 0.5174 | 0.0696 | None | `{'01': 12.0, '10': 8.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 5-29 | 0.0954 | 0.1059 | 0.2972 | 0.1464 | 0.0000 | 0.5194 | 0.0666 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p36_ls1` | 0-24 | 0.0946 | 0.1876 | 0.2518 | 0.1509 | 0.0000 | 0.6306 | 0.0996 | 55 | `{'01': 20.0, '10': 4.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p75` | 0-24 | 0.0941 | 0.1810 | 0.2525 | 0.1496 | 0.0000 | 0.4814 | 0.0946 | None | `{'01': 20.0, '10': 8.0, '11': 72.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0063_ph0p42_ld0p36_ls1` | 5-29 | 0.0938 | 0.1336 | 0.3109 | 0.1456 | 0.0000 | 0.6102 | 0.0748 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75` | 5-29 | 0.0935 | 0.1020 | 0.3088 | 0.1453 | 0.0000 | 0.5540 | 0.0623 | None | `{'01': 12.0, '10': 8.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65` | 5-29 | 0.0930 | 0.1030 | 0.2872 | 0.1474 | 0.0000 | 0.5105 | 0.0685 | None | `{'01': 12.0, '10': 12.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0084_ph0p3927_ld0p36_ls1` | 0-24 | 0.0930 | 0.1854 | 0.2497 | 0.1508 | 0.0000 | 0.5900 | 0.0989 | 52 | `{'01': 20.0, '10': 12.0, '11': 68.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p36_ls1` | 5-29 | 0.0922 | 0.1063 | 0.3087 | 0.1462 | 0.0000 | 0.5865 | 0.0742 | None | `{'01': 12.0, '10': 4.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p36_ls1` | 5-29 | 0.0922 | 0.1042 | 0.3113 | 0.1461 | 0.0000 | 0.5062 | 0.0770 | None | `{'01': 12.0, '10': 4.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p24_ls0p75` | 5-29 | 0.0920 | 0.1075 | 0.3200 | 0.1458 | 0.0000 | 0.5249 | 0.0651 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 0-24 | 0.0920 | 0.1747 | 0.2538 | 0.1486 | 0.0000 | 0.5572 | 0.0991 | 53 | `{'01': 20.0, '10': 8.0, '11': 72.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p36_ls1` | 5-29 | 0.0919 | 0.1051 | 0.3063 | 0.1457 | 0.0000 | 0.8165 | 0.0776 | None | `{'01': 12.0, '10': 4.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p34_ld0p36_ls1` | 5-29 | 0.0915 | 0.0992 | 0.3092 | 0.1462 | 0.0000 | 0.3913 | 0.0764 | None | `{'01': 8.0, '10': 8.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p36_ls1` | 5-29 | 0.0911 | 0.0995 | 0.3133 | 0.1464 | 0.0000 | 0.5801 | 0.0723 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 5-29 | 0.0910 | 0.0832 | 0.3070 | 0.1464 | 0.0000 | 0.5824 | 0.0612 | None | `{'01': 12.0, '10': 12.0, '11': 76.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p42_ld0p36_ls1` | 0-24 | 0.0908 | 0.2005 | 0.2405 | 0.1505 | 0.0000 | 0.5086 | 0.1022 | 88 | `{'01': 36.0, '11': 64.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p34_ld0p36_ls1` | 5-29 | 0.0906 | 0.0976 | 0.2798 | 0.1478 | 0.0000 | 0.3459 | 0.0721 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p34_ld0p36_ls1` | 0-24 | 0.0906 | 0.1928 | 0.2458 | 0.1501 | 0.0000 | 0.5682 | 0.0979 | 55 | `{'01': 20.0, '10': 12.0, '11': 68.0}` |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 0-24 | 0.0902 | 0.1923 | 0.2458 | 0.1486 | 0.0000 | 0.5342 | 0.0955 | None | `{'01': 28.000000000000004, '11': 72.0}` |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 5-29 | 0.0902 | 0.1006 | 0.2924 | 0.1460 | 0.0000 | 0.6135 | 0.0641 | None | `{'01': 20.0, '10': 8.0, '11': 72.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
