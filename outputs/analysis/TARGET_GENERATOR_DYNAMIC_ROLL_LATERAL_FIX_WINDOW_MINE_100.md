# Realized Target Window Mine

status: `PASS_REALIZED_WINDOWS_AVAILABLE`

This mines existing simulated rollout traces for short windows that already
show realized forward motion under actual sim/contact dynamics. It produces
a manifest, not a raw BC dataset.

## Criteria

- window_samples: `100`
- stride_samples: `5`
- min_mean_vx: `0.02`
- max_pitch_abs_p95: `0.5`
- min_base_height: `0.1`
- max_action_saturation_pct: `1.0`
- min_done_margin: `25`

## Trace Summary

| source | mode | samples | done_count | mean_vx | max_vx | min_height | candidates |
|---|---|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0095 | 0.1774 | 0.1463 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0109 | 0.0974 | 0.1458 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0080 | 0.1456 | 0.1482 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0097 | 0.0910 | 0.1480 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0086 | 0.1603 | 0.1469 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0104 | 0.0979 | 0.1468 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0082 | 0.1638 | 0.1463 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p52_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0102 | 0.1308 | 0.1467 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0082 | 0.1793 | 0.1456 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0100 | 0.1302 | 0.1467 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p3_ls0p55` | 200 | 0 | 0.0089 | 0.1659 | 0.1476 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p3927_ld0p3_ls0p55` | 200 | 0 | 0.0104 | 0.0882 | 0.1471 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0095 | 0.1686 | 0.1465 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0118 | 0.1085 | 0.1441 | 3 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0085 | 0.1820 | 0.1466 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0102 | 0.0996 | 0.1470 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0080 | 0.1508 | 0.1472 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0100 | 0.1082 | 0.1472 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0p7854_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0097 | 0.1649 | 0.1464 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0p7854_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0117 | 0.1059 | 0.1457 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p24_ls0p75` | 200 | 0 | 0.0093 | 0.1866 | 0.1463 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p24_ls0p75` | 200 | 0 | 0.0111 | 0.0979 | 0.1467 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0063 | 0.1466 | 0.1476 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0085 | 0.0910 | 0.1475 | 0 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p36_ls1` | 200 | 0 | 0.0077 | 0.1729 | 0.1453 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p36_ls1` | 200 | 0 | 0.0097 | 0.1403 | 0.1467 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0064 | 0.1588 | 0.1464 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0086 | 0.0898 | 0.1465 | 0 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0083 | 0.1463 | 0.1475 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0100 | 0.0910 | 0.1459 | 0 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p36_ls1` | 200 | 0 | 0.0089 | 0.1656 | 0.1450 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p68_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p36_ls1` | 200 | 0 | 0.0107 | 0.1400 | 0.1463 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p47_ld0p36_ls1` | 200 | 0 | 0.0090 | 0.1666 | 0.1451 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p47_ld0p36_ls1` | 200 | 0 | 0.0110 | 0.1271 | 0.1461 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0086 | 0.1473 | 0.1478 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0106 | 0.0952 | 0.1476 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm1p05_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p3_ls0p55` | 200 | 0 | 0.0091 | 0.1515 | 0.1472 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm1p05_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p3_ls0p55` | 200 | 0 | 0.0111 | 0.0931 | 0.1463 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm1p05_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0088 | 0.1557 | 0.1474 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrphm1p05_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0108 | 0.1003 | 0.1476 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0085 | 0.1755 | 0.1467 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0101 | 0.1015 | 0.1475 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0090 | 0.1663 | 0.1464 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0111 | 0.0960 | 0.1466 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p36_ls0p55` | 200 | 0 | 0.0102 | 0.1794 | 0.1462 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p36_ls0p55` | 200 | 0 | 0.0114 | 0.0849 | 0.1459 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0097 | 0.1736 | 0.1461 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p42_ld0p3_ls0p65` | 200 | 0 | 0.0117 | 0.0976 | 0.1454 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0104 | 0.1787 | 0.1461 | 1 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0116 | 0.0921 | 0.1454 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p52_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0079 | 0.1600 | 0.1465 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p52_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0100 | 0.0903 | 0.1473 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls1` | 200 | 0 | 0.0066 | 0.1496 | 0.1468 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls1` | 200 | 0 | 0.0089 | 0.1005 | 0.1469 | 0 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0090 | 0.1865 | 0.1455 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0111 | 0.0931 | 0.1455 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p24_ls0p65` | 200 | 0 | 0.0078 | 0.1527 | 0.1472 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0076_ph0p3927_ld0p24_ls0p65` | 200 | 0 | 0.0099 | 0.0966 | 0.1474 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p36_ls0p65` | 200 | 0 | 0.0090 | 0.1611 | 0.1461 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p36_ls0p65` | 200 | 0 | 0.0110 | 0.1036 | 0.1464 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0077 | 0.1436 | 0.1482 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0098 | 0.0959 | 0.1481 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p34_ld0p3_ls1` | 200 | 0 | 0.0062 | 0.1502 | 0.1466 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p34_ld0p3_ls1` | 200 | 0 | 0.0093 | 0.1145 | 0.1468 | 0 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0076 | 0.1548 | 0.1462 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0094 | 0.1161 | 0.1467 | 0 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p42_ld0p36_ls0p65` | 200 | 0 | 0.0093 | 0.1943 | 0.1449 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p42_ld0p36_ls0p65` | 200 | 0 | 0.0106 | 0.1043 | 0.1458 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p34_ld0p36_ls1` | 80 | 1 | 0.2066 | 1.3167 | 0.0232 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0101 | 0.1294 | 0.1462 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0082 | 0.1724 | 0.1469 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0101 | 0.0997 | 0.1469 | 0 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0063_ph0p42_ld0p36_ls1` | 200 | 0 | 0.0093 | 0.1838 | 0.1452 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0063_ph0p42_ld0p36_ls1` | 200 | 0 | 0.0111 | 0.1240 | 0.1463 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p52_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0073 | 0.1517 | 0.1475 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p52_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0089 | 0.0877 | 0.1478 | 0 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0079 | 0.1672 | 0.1458 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0064_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0098 | 0.0959 | 0.1469 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0075 | 0.1483 | 0.1465 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0096 | 0.1044 | 0.1467 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55` | 200 | 0 | 0.0090 | 0.1708 | 0.1440 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p048_hrphm0p68_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p37_ld0p36_ls0p55` | 200 | 0 | 0.0106 | 0.1040 | 0.1445 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p34_ld0p3_ls1` | 200 | 0 | 0.0069 | 0.1689 | 0.1457 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p34_ld0p3_ls1` | 200 | 0 | 0.0093 | 0.1196 | 0.1468 | 0 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0081 | 0.1488 | 0.1480 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0098 | 0.0853 | 0.1481 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0074 | 0.1402 | 0.1478 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0094 | 0.0866 | 0.1479 | 1 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0048_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0064 | 0.1527 | 0.1467 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0048_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0086 | 0.1079 | 0.1470 | 0 |
| seed_000.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0093 | 0.1681 | 0.1460 | 0 |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p04_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0111 | 0.1011 | 0.1462 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0080 | 0.1702 | 0.1462 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0096 | 0.0946 | 0.1456 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0084 | 0.1875 | 0.1468 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0097 | 0.0888 | 0.1461 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0077 | 0.1514 | 0.1482 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0097 | 0.0878 | 0.1479 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0080 | 0.1700 | 0.1465 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0095 | 0.0895 | 0.1464 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0048_ph0p3927_ld0p36_ls0p65` | 200 | 0 | 0.0086 | 0.1767 | 0.1461 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0048_ph0p3927_ld0p36_ls0p65` | 200 | 0 | 0.0103 | 0.1045 | 0.1461 | 2 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0048_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0063 | 0.1526 | 0.1469 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p0048_ph0p3927_ld0p3_ls1` | 200 | 0 | 0.0083 | 0.0871 | 0.1468 | 0 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p36_ls0p75` | 200 | 0 | 0.0082 | 0.1731 | 0.1462 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p36_ls0p75` | 200 | 0 | 0.0100 | 0.0926 | 0.1454 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0057_ph0p34_ld0p36_ls0p65` | 200 | 0 | 0.0086 | 0.1709 | 0.1458 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0057_ph0p34_ld0p36_ls0p65` | 200 | 0 | 0.0105 | 0.1086 | 0.1460 | 2 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p9_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0073 | 0.1607 | 0.1481 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p9_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0090 | 0.0993 | 0.1482 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0081 | 0.1549 | 0.1466 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0101 | 0.1012 | 0.1466 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p36_ls0p75` | 200 | 0 | 0.0082 | 0.1627 | 0.1462 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p36_ls0p75` | 200 | 0 | 0.0101 | 0.1038 | 0.1462 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrph0_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p3927_ld0p36_ls0p65` | 200 | 0 | 0.0079 | 0.1835 | 0.1469 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p036_hrph0_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p3927_ld0p36_ls0p65` | 200 | 0 | 0.0095 | 0.0926 | 0.1476 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p36_ls1` | 80 | 1 | 0.2121 | 1.3209 | 0.0149 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0099 | 0.1505 | 0.1459 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm0p68_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0069 | 0.1645 | 0.1478 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm0p68_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0089 | 0.0883 | 0.1477 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm1p05_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0073 | 0.1386 | 0.1486 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm1p05_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0093 | 0.0880 | 0.1487 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm1p05_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p34_ld0p24_ls1` | 200 | 0 | 0.0056 | 0.1430 | 0.1480 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p036_hrphm1p05_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p34_ld0p24_ls1` | 200 | 0 | 0.0078 | 0.1119 | 0.1485 | 0 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p36_ls0p75` | 200 | 0 | 0.0070 | 0.1678 | 0.1460 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p36_ls0p75` | 200 | 0 | 0.0090 | 0.1037 | 0.1467 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65` | 200 | 0 | 0.0078 | 0.1815 | 0.1452 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65` | 200 | 0 | 0.0097 | 0.1005 | 0.1457 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p34_ld0p24_ls1` | 200 | 0 | 0.0064 | 0.1548 | 0.1461 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p34_ld0p24_ls1` | 200 | 0 | 0.0081 | 0.0880 | 0.1467 | 0 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0082 | 0.1882 | 0.1452 | 1 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0097 | 0.1077 | 0.1459 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0069 | 0.1512 | 0.1473 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0091 | 0.0871 | 0.1475 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 78 | 1 | 0.1981 | 1.2623 | 0.0373 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0095 | 0.0987 | 0.1459 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0091 | 0.1921 | 0.1455 | 2 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0105 | 0.1028 | 0.1448 | 2 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0072 | 0.1699 | 0.1459 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p3_ls0p65` | 200 | 0 | 0.0090 | 0.0995 | 0.1464 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0068 | 0.1529 | 0.1463 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p47_ld0p3_ls0p65` | 200 | 0 | 0.0090 | 0.0980 | 0.1464 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0074 | 0.1805 | 0.1454 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0097 | 0.1087 | 0.1460 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0_ph0p42_ld0p36_ls0p75` | 200 | 0 | 0.0076 | 0.1867 | 0.1459 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0_ph0p42_ld0p36_ls0p75` | 200 | 0 | 0.0094 | 0.0898 | 0.1464 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p75` | 200 | 0 | 0.0083 | 0.2095 | 0.1455 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p75` | 200 | 0 | 0.0097 | 0.1151 | 0.1461 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0084_ph0p3927_ld0p36_ls1` | 77 | 1 | 0.2121 | 1.3421 | 0.0231 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0084_ph0p3927_ld0p36_ls1` | 200 | 0 | 0.0098 | 0.1034 | 0.1455 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p42_ld0p36_ls1` | 113 | 1 | 0.1427 | 1.2865 | 0.0296 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p42_ld0p36_ls1` | 200 | 0 | 0.0112 | 0.1219 | 0.1456 | 3 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0074 | 0.1714 | 0.1460 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0091 | 0.1005 | 0.1471 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p36_ls1` | 200 | 0 | 0.0072 | 0.1793 | 0.1445 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p52_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p36_ls1` | 200 | 0 | 0.0091 | 0.1354 | 0.1464 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p65` | 200 | 0 | 0.0076 | 0.1626 | 0.1464 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p65` | 200 | 0 | 0.0094 | 0.0964 | 0.1471 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0064 | 0.1424 | 0.1482 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0087 | 0.0999 | 0.1486 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p24_ls1` | 200 | 0 | 0.0058 | 0.1598 | 0.1468 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p24_ls1` | 200 | 0 | 0.0082 | 0.1219 | 0.1471 | 0 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0075 | 0.1532 | 0.1470 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0094 | 0.0989 | 0.1457 | 1 |
| seed_000.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0078 | 0.1417 | 0.1478 | 0 |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00875_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0099 | 0.0928 | 0.1477 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0079 | 0.1636 | 0.1483 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0095 | 0.0863 | 0.1483 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0084_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0085 | 0.1766 | 0.1472 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p032_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0084_ph0p34_ld0p3_ls0p55` | 200 | 0 | 0.0101 | 0.0963 | 0.1476 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0079 | 0.1591 | 0.1460 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0099 | 0.1170 | 0.1469 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0087 | 0.1552 | 0.1470 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm0p68_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0104 | 0.0818 | 0.1463 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0087 | 0.1327 | 0.1484 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p0048_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0107 | 0.0871 | 0.1484 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p3_ls0p55` | 200 | 0 | 0.0091 | 0.1524 | 0.1471 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p47_ld0p3_ls0p55` | 200 | 0 | 0.0111 | 0.0921 | 0.1469 | 2 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0068 | 0.1547 | 0.1474 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0089 | 0.1177 | 0.1476 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0091 | 0.1848 | 0.1471 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0109 | 0.0909 | 0.1475 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0094 | 0.1768 | 0.1467 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p036_hrph0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0112 | 0.1035 | 0.1469 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm0p52_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0071 | 0.1461 | 0.1483 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm0p52_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0087 | 0.0883 | 0.1483 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p42_ld0p3_ls0p55` | 200 | 0 | 0.0084 | 0.1515 | 0.1471 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0105_ph0p42_ld0p3_ls0p55` | 200 | 0 | 0.0100 | 0.0922 | 0.1446 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm1p05_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p3927_ld0p36_ls0p65` | 200 | 0 | 0.0094 | 0.1678 | 0.1464 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p036_hrphm1p05_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p3927_ld0p36_ls0p65` | 200 | 0 | 0.0116 | 0.1042 | 0.1464 | 2 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p3927_ld0p3_ls0p55` | 200 | 0 | 0.0076 | 0.1542 | 0.1476 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p3927_ld0p3_ls0p55` | 200 | 0 | 0.0095 | 0.0895 | 0.1479 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0079 | 0.1543 | 0.1472 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0099 | 0.1128 | 0.1476 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0077 | 0.1735 | 0.1473 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p044_hrph0_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p47_ld0p24_ls0p55` | 200 | 0 | 0.0094 | 0.0942 | 0.1476 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0074 | 0.1482 | 0.1476 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p52_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0095 | 0.0955 | 0.1480 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0_ph0p34_ld0p24_ls0p75` | 200 | 0 | 0.0072 | 0.1466 | 0.1480 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0_ph0p34_ld0p24_ls0p75` | 200 | 0 | 0.0094 | 0.0939 | 0.1485 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p47_ld0p36_ls0p75` | 200 | 0 | 0.0092 | 0.1735 | 0.1456 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p47_ld0p36_ls0p75` | 200 | 0 | 0.0113 | 0.1086 | 0.1459 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p36_ls1` | 200 | 0 | 0.0070 | 0.1665 | 0.1455 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p044_hrphm0p9_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0p0084_ph0p42_ld0p36_ls1` | 200 | 0 | 0.0090 | 0.1270 | 0.1465 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0079 | 0.1853 | 0.1462 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0076_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0095 | 0.0911 | 0.1477 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0078 | 0.1656 | 0.1459 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0097 | 0.1437 | 0.1468 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0116 | 0.1933 | 0.1451 | 1 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0129 | 0.1142 | 0.1450 | 3 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0090 | 0.1793 | 0.1469 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0076_ph0p37_ld0p24_ls0p65` | 200 | 0 | 0.0105 | 0.0903 | 0.1477 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p007_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0073 | 0.1463 | 0.1467 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p007_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0092 | 0.1008 | 0.1472 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0091 | 0.1681 | 0.1448 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0109 | 0.1185 | 0.1460 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0077 | 0.1495 | 0.1466 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0097 | 0.0861 | 0.1459 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0082 | 0.1584 | 0.1466 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55` | 200 | 0 | 0.0101 | 0.0877 | 0.1465 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p3927_ld0p36_ls0p55` | 200 | 0 | 0.0097 | 0.1760 | 0.1447 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0084_ph0p3927_ld0p36_ls0p55` | 100 | 1 | 0.1579 | 1.2658 | 0.0369 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p36_ls0p75` | 200 | 0 | 0.0089 | 0.1857 | 0.1460 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p36_ls0p75` | 200 | 0 | 0.0107 | 0.0978 | 0.1463 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p34_ld0p36_ls1` | 95 | 1 | 0.1713 | 1.3145 | 0.0271 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrph0p7854_hb0p08_h0p032_kb0p06_k0p14_ab0p04_a0p008_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0125 | 0.1396 | 0.1457 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p52_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0072 | 0.1596 | 0.1473 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p52_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0093 | 0.0965 | 0.1479 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p68_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p55` | 200 | 0 | 0.0087 | 0.1609 | 0.1466 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p68_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p36_ls0p55` | 200 | 0 | 0.0105 | 0.0956 | 0.1467 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0096 | 0.1799 | 0.1455 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0116 | 0.1193 | 0.1459 | 1 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0083 | 0.1550 | 0.1469 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0101 | 0.0810 | 0.1460 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0074 | 0.1487 | 0.1475 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm0p9_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0095_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0096 | 0.0995 | 0.1480 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p3_ls0p55` | 200 | 0 | 0.0084 | 0.1410 | 0.1482 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p3_ls0p55` | 200 | 0 | 0.0102 | 0.0819 | 0.1480 | 0 |
| seed_000.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0088 | 0.1549 | 0.1465 | 0 |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0110 | 0.1067 | 0.1467 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0078 | 0.1429 | 0.1480 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0094 | 0.0946 | 0.1478 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0063_ph0p42_ld0p36_ls0p55` | 200 | 0 | 0.0087 | 0.1788 | 0.1461 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0063_ph0p42_ld0p36_ls0p55` | 200 | 0 | 0.0101 | 0.1006 | 0.1456 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0081 | 0.1421 | 0.1483 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0100 | 0.0942 | 0.1478 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0099 | 0.1926 | 0.1464 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p37_ld0p3_ls0p65` | 200 | 0 | 0.0112 | 0.0975 | 0.1457 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p47_ld0p36_ls0p75` | 200 | 0 | 0.0103 | 0.1702 | 0.1457 | 1 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p47_ld0p36_ls0p75` | 200 | 0 | 0.0117 | 0.1021 | 0.1451 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0064_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0072 | 0.1434 | 0.1473 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0064_ph0p37_ld0p24_ls1` | 200 | 0 | 0.0087 | 0.1103 | 0.1468 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p36_ls0p55` | 200 | 0 | 0.0077 | 0.1575 | 0.1478 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p68_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p37_ld0p36_ls0p55` | 200 | 0 | 0.0095 | 0.0937 | 0.1477 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0081 | 0.1408 | 0.1472 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p24_ls0p75` | 200 | 0 | 0.0100 | 0.0901 | 0.1466 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0085 | 0.1642 | 0.1471 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0_ph0p34_ld0p24_ls0p55` | 200 | 0 | 0.0103 | 0.0981 | 0.1462 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0079 | 0.1416 | 0.1478 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm1p05_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0101 | 0.0976 | 0.1478 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm1p05_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0057_ph0p37_ld0p36_ls1` | 200 | 0 | 0.0091 | 0.1824 | 0.1455 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm1p05_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0057_ph0p37_ld0p36_ls1` | 200 | 0 | 0.0111 | 0.1290 | 0.1464 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm1p05_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0063_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0084 | 0.1588 | 0.1466 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrphm1p05_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0063_ph0p37_ld0p3_ls0p75` | 200 | 0 | 0.0104 | 0.1085 | 0.1469 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p36_ls1` | 200 | 0 | 0.0080 | 0.1790 | 0.1462 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p038_kb0p06_k0p12_ab0p04_a0p0057_ph0p47_ld0p36_ls1` | 200 | 0 | 0.0096 | 0.1042 | 0.1467 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls1` | 200 | 0 | 0.0068 | 0.1583 | 0.1470 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls1` | 200 | 0 | 0.0091 | 0.1194 | 0.1473 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0063_ph0p34_ld0p36_ls1` | 74 | 1 | 0.2298 | 1.3471 | 0.0142 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0_hb0p08_h0p042_kb0p06_k0p16_ab0p04_a0p0063_ph0p34_ld0p36_ls1` | 200 | 0 | 0.0111 | 0.1276 | 0.1460 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p34_ld0p24_ls1` | 200 | 0 | 0.0083 | 0.1493 | 0.1475 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p34_ld0p24_ls1` | 200 | 0 | 0.0107 | 0.1060 | 0.1476 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p34_ld0p24_ls0p65` | 200 | 0 | 0.0077 | 0.1612 | 0.1477 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrph0p7854_hb0p08_h0p042_kb0p06_k0p12_ab0p04_a0_ph0p34_ld0p24_ls0p65` | 200 | 0 | 0.0097 | 0.0951 | 0.1477 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p65` | 200 | 0 | 0.0079 | 0.1608 | 0.1470 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p52_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p24_ls0p65` | 200 | 0 | 0.0099 | 0.0955 | 0.1467 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p52_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p65` | 200 | 0 | 0.0077 | 0.1673 | 0.1472 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p52_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p65` | 200 | 0 | 0.0095 | 0.0919 | 0.1474 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0075 | 0.1459 | 0.1477 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p3927_ld0p24_ls0p75` | 200 | 0 | 0.0097 | 0.0930 | 0.1477 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0087 | 0.1481 | 0.1464 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00525_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0107 | 0.0969 | 0.1461 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0078 | 0.1401 | 0.1480 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0_ph0p37_ld0p24_ls0p55` | 200 | 0 | 0.0097 | 0.0946 | 0.1479 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0081 | 0.1409 | 0.1475 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00875_ph0p3927_ld0p3_ls0p65` | 200 | 0 | 0.0102 | 0.0902 | 0.1476 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p24_ls0p65` | 200 | 0 | 0.0074 | 0.1367 | 0.1482 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p24_ls0p65` | 200 | 0 | 0.0094 | 0.0982 | 0.1481 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0094 | 0.1642 | 0.1459 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p37_ld0p36_ls0p75` | 200 | 0 | 0.0112 | 0.1064 | 0.1458 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0084_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0070 | 0.1394 | 0.1479 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0084_ph0p47_ld0p24_ls0p75` | 200 | 0 | 0.0091 | 0.1034 | 0.1483 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm1p05_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0077 | 0.1356 | 0.1481 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p036_hrphm1p05_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p42_ld0p24_ls0p55` | 200 | 0 | 0.0098 | 0.0950 | 0.1478 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p42_ld0p3_ls0p75` | 200 | 0 | 0.0078 | 0.1497 | 0.1463 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p42_ld0p3_ls0p75` | 200 | 0 | 0.0096 | 0.0932 | 0.1461 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls1` | 200 | 0 | 0.0070 | 0.1505 | 0.1464 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p044_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0095_ph0p34_ld0p3_ls1` | 200 | 0 | 0.0088 | 0.1139 | 0.1468 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0076 | 0.1608 | 0.1460 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p52_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0063_ph0p37_ld0p36_ls0p65` | 200 | 0 | 0.0095 | 0.1008 | 0.1468 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0105_ph0p3927_ld0p24_ls0p55` | 200 | 0 | 0.0069 | 0.1384 | 0.1477 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm0p9_hb0p08_h0p042_kb0p06_k0p14_ab0p04_a0p0105_ph0p3927_ld0p24_ls0p55` | 200 | 0 | 0.0089 | 0.1038 | 0.1472 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0075 | 0.1506 | 0.1468 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p34_ld0p3_ls0p75` | 200 | 0 | 0.0094 | 0.0871 | 0.1467 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrph0_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p008_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0073 | 0.1311 | 0.1483 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrph0_hb0p08_h0p032_kb0p06_k0p12_ab0p04_a0p008_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0095 | 0.0988 | 0.1486 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0092 | 0.1976 | 0.1457 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0_ph0p42_ld0p24_ls0p75` | 200 | 0 | 0.0110 | 0.1066 | 0.1461 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0073 | 0.1526 | 0.1471 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p00525_ph0p47_ld0p3_ls0p75` | 200 | 0 | 0.0093 | 0.0944 | 0.1475 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p34_ld0p36_ls0p65` | 200 | 0 | 0.0089 | 0.1700 | 0.1454 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p34_ld0p36_ls0p65` | 200 | 0 | 0.0108 | 0.1027 | 0.1445 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p47_ld0p36_ls0p65` | 200 | 0 | 0.0078 | 0.1678 | 0.1466 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p68_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0p0057_ph0p47_ld0p36_ls0p65` | 200 | 0 | 0.0097 | 0.0912 | 0.1468 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0082 | 0.1609 | 0.1461 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p42_ld0p3_ls1` | 200 | 0 | 0.0102 | 0.1248 | 0.1465 | 1 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p3927_ld0p24_ls1` | 200 | 0 | 0.0058 | 0.1422 | 0.1481 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p00525_ph0p3927_ld0p24_ls1` | 200 | 0 | 0.0081 | 0.1015 | 0.1486 | 0 |
| seed_000.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p36_ls1` | 200 | 0 | 0.0090 | 0.1739 | 0.1455 | 0 |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p04_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p36_ls1` | 200 | 0 | 0.0107 | 0.1256 | 0.1465 | 1 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p42_ld0p3_ls0p65` | 0-99 | 0.0307 | 0.1371 | 0.3777 | 0.1441 | 0.0000 | 0.5588 | 0.0848 | None | `{'01': 3.0, '10': 2.0, '11': 95.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p42_ld0p3_ls0p65` | 5-104 | 0.0253 | 0.0727 | 0.3777 | 0.1441 | 0.0000 | 0.5588 | 0.0794 | None | `{'01': 1.0, '11': 99.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrph0p7854_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0063_ph0p37_ld0p3_ls0p65` | 0-99 | 0.0244 | 0.1039 | 0.3304 | 0.1448 | 0.0000 | 0.5919 | 0.0807 | None | `{'01': 2.0, '10': 1.0, '11': 97.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p9_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0057_ph0p34_ld0p36_ls0p65` | 0-99 | 0.0241 | 0.1125 | 0.2794 | 0.1460 | 0.0000 | 0.5963 | 0.0795 | None | `{'01': 2.0, '10': 2.0, '11': 96.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p18_ab0p04_a0p0076_ph0p34_ld0p24_ls0p55` | 0-99 | 0.0238 | 0.1042 | 0.3200 | 0.1454 | 0.0000 | 0.5364 | 0.0804 | None | `{'01': 2.0, '10': 2.0, '11': 96.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p0048_ph0p3927_ld0p36_ls0p65` | 0-99 | 0.0235 | 0.1110 | 0.2765 | 0.1461 | 0.0000 | 0.5886 | 0.0790 | None | `{'01': 3.0, '11': 97.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p032_hrphm0p9_hb0p08_h0p042_kb0p06_k0p18_ab0p04_a0p0105_ph0p42_ld0p3_ls0p65` | 10-109 | 0.0235 | 0.0626 | 0.3777 | 0.1441 | 0.0000 | 0.6279 | 0.0803 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0p7854_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p42_ld0p24_ls0p75` | 0-99 | 0.0231 | 0.1052 | 0.3058 | 0.1457 | 0.0000 | 0.4309 | 0.0783 | None | `{'01': 2.0, '11': 98.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p04_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0048_ph0p42_ld0p36_ls1` | 0-99 | 0.0231 | 0.1047 | 0.3145 | 0.1456 | 0.0000 | 0.6426 | 0.0801 | None | `{'01': 3.0, '10': 1.0, '11': 96.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p3927_ld0p3_ls0p65` | 0-99 | 0.0230 | 0.1133 | 0.2674 | 0.1466 | 0.0000 | 0.5930 | 0.0764 | None | `{'01': 2.0, '10': 1.0, '11': 97.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p044_hrphm0p68_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p47_ld0p36_ls0p65` | 0-99 | 0.0230 | 0.1128 | 0.2787 | 0.1457 | 0.0000 | 0.5581 | 0.0795 | None | `{'01': 4.0, '10': 1.0, '11': 95.0}` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 10-109 | 0.0230 | 0.0526 | 0.3145 | 0.1450 | 0.0000 | 0.5604 | 0.0760 | None | `{'10': 1.0, '11': 99.0}` |
| seed_002.jsonl | `primitive_p0p5_hrb0_hra0p032_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p47_ld0p36_ls0p75` | 0-99 | 0.0229 | 0.1064 | 0.3190 | 0.1451 | 0.0000 | 0.4860 | 0.0828 | None | `{'01': 2.0, '11': 98.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0095_ph0p42_ld0p3_ls0p65` | 0-99 | 0.0228 | 0.1043 | 0.3098 | 0.1454 | 0.0000 | 0.5267 | 0.0804 | None | `{'01': 2.0, '11': 98.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm1p05_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p36_ls0p75` | 0-99 | 0.0228 | 0.1131 | 0.2769 | 0.1463 | 0.0000 | 0.5078 | 0.0778 | None | `{'01': 2.0, '10': 1.0, '11': 97.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p37_ld0p36_ls0p55` | 0-99 | 0.0227 | 0.1041 | 0.3045 | 0.1459 | 0.0000 | 0.5224 | 0.0802 | None | `{'01': 2.0, '11': 98.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p036_hrph0p7854_hb0p08_h0p038_kb0p06_k0p16_ab0p04_a0p0057_ph0p34_ld0p24_ls0p75` | 0-99 | 0.0226 | 0.1054 | 0.2926 | 0.1467 | 0.0000 | 0.4471 | 0.0775 | None | `{'01': 2.0, '11': 98.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p00875_ph0p34_ld0p3_ls0p55` | 0-99 | 0.0225 | 0.1088 | 0.2925 | 0.1456 | 0.0000 | 0.4775 | 0.0804 | None | `{'01': 2.0, '10': 1.0, '11': 97.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrph0p7854_hb0p08_h0p035_kb0p06_k0p12_ab0p04_a0p007_ph0p37_ld0p24_ls0p75` | 0-99 | 0.0225 | 0.1058 | 0.2764 | 0.1479 | 0.0000 | 0.3972 | 0.0744 | None | `{'01': 2.0, '10': 2.0, '11': 96.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrph0p7854_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0_ph0p42_ld0p24_ls0p75` | 0-99 | 0.0224 | 0.1040 | 0.2867 | 0.1466 | 0.0000 | 0.5263 | 0.0763 | None | `{'01': 2.0, '11': 98.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p048_hrphm0p9_hb0p08_h0p032_kb0p06_k0p18_ab0p04_a0p008_ph0p37_ld0p36_ls0p75` | 0-99 | 0.0224 | 0.1142 | 0.2640 | 0.1460 | 0.0000 | 0.5565 | 0.0792 | None | `{'01': 2.0, '10': 2.0, '11': 96.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0p007_ph0p3927_ld0p36_ls0p75` | 0-99 | 0.0223 | 0.1224 | 0.3007 | 0.1454 | 0.0000 | 0.5157 | 0.0785 | None | `{'01': 2.0, '10': 2.0, '11': 96.0}` |
| seed_002.jsonl | `primitive_p0p58_hrb0_hra0p048_hrph0p7854_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p37_ld0p36_ls0p65` | 0-99 | 0.0223 | 0.1033 | 0.3145 | 0.1450 | 0.0000 | 0.5511 | 0.0783 | None | `{'01': 2.0, '10': 1.0, '11': 97.0}` |
| seed_002.jsonl | `primitive_p0p54_hrb0_hra0p032_hrphm0p52_hb0p08_h0p032_kb0p06_k0p16_ab0p04_a0p0064_ph0p47_ld0p36_ls0p55` | 0-99 | 0.0222 | 0.1109 | 0.2719 | 0.1464 | 0.0000 | 0.4343 | 0.0801 | None | `{'01': 3.0, '10': 1.0, '11': 96.0}` |
| seed_002.jsonl | `primitive_p0p52_hrb0_hra0p044_hrphm0p9_hb0p08_h0p035_kb0p06_k0p16_ab0p04_a0p00875_ph0p34_ld0p36_ls0p65` | 0-99 | 0.0222 | 0.1139 | 0.2632 | 0.1464 | 0.0000 | 0.5298 | 0.0801 | None | `{'01': 4.0, '10': 1.0, '11': 95.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
