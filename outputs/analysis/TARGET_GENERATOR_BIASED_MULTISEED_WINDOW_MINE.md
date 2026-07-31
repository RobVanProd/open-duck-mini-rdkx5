# Realized Target Window Mine

status: `PASS_REALIZED_WINDOWS_AVAILABLE`

This mines existing simulated rollout traces for short windows that already
show realized forward motion under actual sim/contact dynamics. It produces
a manifest, not a raw BC dataset.

## Criteria

- window_samples: `25`
- stride_samples: `5`
- min_mean_vx: `0.04`
- max_pitch_abs_p95: `0.45`
- min_base_height: `0.1`
- max_action_saturation_pct: `5.0`
- min_done_margin: `10`

## Trace Summary

| source | mode | samples | done_count | mean_vx | max_vx | min_height | candidates |
|---|---|---:|---:|---:|---:|---:|---:|
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0030 | 0.1123 | 0.1538 | 2 |
| seed_001.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 33 | 1 | -0.1288 | -0.0212 | 0.0896 | 0 |
| seed_002.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0056 | 0.0995 | 0.1527 | 1 |
| seed_003.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | -0.0034 | 0.0745 | 0.1539 | 0 |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0052 | 0.0823 | 0.1536 | 0 |
| seed_001.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 32 | 1 | -0.1218 | -0.0323 | 0.0958 | 0 |
| seed_002.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0076 | 0.0741 | 0.1526 | 0 |
| seed_003.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | -0.0091 | 0.0803 | 0.1529 | 0 |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0051 | 0.1569 | 0.1506 | 3 |
| seed_001.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 32 | 1 | -0.1244 | -0.0243 | 0.0982 | 0 |
| seed_002.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0074 | 0.1235 | 0.1507 | 3 |
| seed_003.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | -0.0104 | 0.0825 | 0.1490 | 0 |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0079 | 0.1280 | 0.1506 | 1 |
| seed_001.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 34 | 1 | -0.1234 | -0.0335 | 0.0829 | 0 |
| seed_002.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0098 | 0.0782 | 0.1503 | 0 |
| seed_003.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | -0.0066 | 0.1082 | 0.1506 | 0 |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0054 | 0.1051 | 0.1528 | 2 |
| seed_001.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 32 | 1 | -0.1212 | -0.0212 | 0.1087 | 0 |
| seed_002.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0079 | 0.1031 | 0.1527 | 1 |
| seed_003.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | -0.0013 | 0.0751 | 0.1529 | 0 |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0072 | 0.0838 | 0.1527 | 0 |
| seed_001.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 32 | 1 | -0.1190 | -0.0323 | 0.0986 | 0 |
| seed_002.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0093 | 0.0772 | 0.1526 | 0 |
| seed_003.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | -0.0072 | 0.0776 | 0.1526 | 0 |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0068 | 0.1434 | 0.1497 | 3 |
| seed_001.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 32 | 1 | -0.1281 | -0.0243 | 0.0968 | 0 |
| seed_002.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0092 | 0.1226 | 0.1498 | 3 |
| seed_003.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | -0.0086 | 0.0851 | 0.1489 | 0 |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0096 | 0.1232 | 0.1497 | 2 |
| seed_001.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 33 | 1 | -0.1098 | -0.0335 | 0.1069 | 0 |
| seed_002.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0116 | 0.0826 | 0.1497 | 1 |
| seed_003.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | -0.0049 | 0.0944 | 0.1497 | 0 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0775 | 0.0702 | 0.2394 | 0.1515 | 0.0000 | 0.3454 | 0.0654 | None | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0746 | 0.1798 | 0.2394 | 0.1515 | 0.0000 | 0.3460 | 0.0863 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0735 | 0.1745 | 0.2081 | 0.1526 | 0.0000 | 0.4466 | 0.0903 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0718 | 0.0647 | 0.2081 | 0.1525 | 0.0000 | 0.4196 | 0.0640 | None | `{'01': 12.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0648 | 0.2028 | 0.1614 | 0.1527 | 0.0000 | 0.3460 | 0.0866 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0646 | 0.2010 | 0.1341 | 0.1527 | 0.0000 | 0.4466 | 0.0880 | None | `{'01': 8.0, '10': 4.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0611 | 0.0349 | 0.1679 | 0.1534 | 0.0000 | 0.3454 | 0.0549 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0580 | 0.1055 | 0.1679 | 0.1539 | 0.0000 | 0.3454 | 0.0555 | None | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0565 | 0.0535 | 0.2394 | 0.1515 | 0.0000 | 0.3454 | 0.0654 | None | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 0-24 | 0.0543 | 0.1481 | 0.1621 | 0.1531 | 0.0000 | 0.3443 | 0.0693 | None | `{'01': 16.0, '11': 84.0}` |
| seed_002.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0527 | 0.1047 | 0.1420 | 0.1531 | 0.0000 | 0.4196 | 0.0563 | None | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0510 | 0.0919 | 0.1558 | 0.1553 | 0.0000 | 0.3454 | 0.0604 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0499 | 0.1761 | 0.1558 | 0.1538 | 0.0000 | 0.3460 | 0.0841 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 5-29 | 0.0493 | 0.0515 | 0.1621 | 0.1531 | 0.0000 | 0.3473 | 0.0563 | None | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0480 | 0.1724 | 0.1321 | 0.1538 | 0.0000 | 0.4466 | 0.0860 | None | `{'01': 20.0, '11': 80.0}` |
| seed_002.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0467 | 0.0330 | 0.1420 | 0.1530 | 0.0000 | 0.4410 | 0.0569 | None | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 0-24 | 0.0450 | 0.1500 | 0.1452 | 0.1530 | 0.0000 | 0.4388 | 0.0847 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0449 | 0.0853 | 0.1321 | 0.1557 | 0.0000 | 0.4196 | 0.0566 | None | `{'01': 12.0, '11': 88.0}` |
| seed_002.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0438 | 0.1997 | 0.0908 | 0.1527 | 0.0000 | 0.3460 | 0.0863 | None | `{'01': 8.0, '10': 8.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0434 | 0.0550 | 0.2081 | 0.1525 | 0.0000 | 0.4410 | 0.0646 | None | `{'11': 100.0}` |
| seed_002.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 0-24 | 0.0406 | 0.2035 | 0.0703 | 0.1526 | 0.0000 | 0.3443 | 0.0726 | None | `{'01': 8.0, '10': 8.0, '11': 84.0}` |
| seed_002.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0402 | 0.1979 | 0.0670 | 0.1527 | 0.0000 | 0.4466 | 0.0887 | None | `{'01': 8.0, '10': 8.0, '11': 84.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
