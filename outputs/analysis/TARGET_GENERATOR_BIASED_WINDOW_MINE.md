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
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0052 | 0.0823 | 0.1536 | 0 |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_abm0p04_am0p025_ph0` | 72 | 1 | -0.2304 | 0.0372 | 0.0654 | 0 |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_abm0p04_am0p025_ph1p5708` | 150 | 0 | -0.0081 | 0.0244 | 0.1536 | 0 |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0051 | 0.1569 | 0.1506 | 3 |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0079 | 0.1280 | 0.1506 | 1 |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_abm0p04_am0p025_ph0` | 150 | 0 | -0.0025 | 0.0373 | 0.1536 | 0 |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_abm0p04_am0p025_ph1p5708` | 150 | 0 | -0.0016 | 0.0328 | 0.1535 | 0 |
| seed_000.jsonl | `primitive_p0p7_hbm0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0025 | 0.0993 | 0.1528 | 0 |
| seed_000.jsonl | `primitive_p0p7_hbm0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0047 | 0.1111 | 0.1527 | 0 |
| seed_000.jsonl | `primitive_p0p7_hbm0p06_h0p05_kb0_k0p08_abm0p04_am0p025_ph0` | 83 | 1 | -0.2264 | 0.0174 | 0.0321 | 0 |
| seed_000.jsonl | `primitive_p0p7_hbm0p06_h0p05_kb0_k0p08_abm0p04_am0p025_ph1p5708` | 84 | 1 | -0.2017 | 0.0096 | 0.0634 | 0 |
| seed_000.jsonl | `primitive_p0p7_hbm0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0044 | 0.1288 | 0.1493 | 1 |
| seed_000.jsonl | `primitive_p0p7_hbm0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0064 | 0.1081 | 0.1491 | 0 |
| seed_000.jsonl | `primitive_p0p7_hbm0p06_h0p05_kb0p03_k0p08_abm0p04_am0p025_ph0` | 150 | 0 | -0.0040 | 0.0922 | 0.1534 | 0 |
| seed_000.jsonl | `primitive_p0p7_hbm0p06_h0p05_kb0p03_k0p08_abm0p04_am0p025_ph1p5708` | 150 | 0 | -0.0011 | 0.0772 | 0.1533 | 0 |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0054 | 0.1051 | 0.1528 | 2 |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0072 | 0.0838 | 0.1527 | 0 |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_abm0p04_am0p025_ph0` | 80 | 1 | -0.2146 | 0.0401 | 0.0576 | 0 |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_abm0p04_am0p025_ph1p5708` | 89 | 1 | -0.1928 | 0.0177 | 0.0557 | 0 |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0068 | 0.1434 | 0.1497 | 3 |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0096 | 0.1232 | 0.1497 | 2 |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_abm0p04_am0p025_ph0` | 150 | 0 | -0.0018 | 0.0388 | 0.1536 | 0 |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_abm0p04_am0p025_ph1p5708` | 150 | 0 | -0.0006 | 0.0350 | 0.1535 | 0 |
| seed_000.jsonl | `primitive_p0p9_hbm0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0045 | 0.1238 | 0.1510 | 0 |
| seed_000.jsonl | `primitive_p0p9_hbm0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0035 | 0.1121 | 0.1517 | 0 |
| seed_000.jsonl | `primitive_p0p9_hbm0p06_h0p05_kb0_k0p08_abm0p04_am0p025_ph0` | 88 | 1 | -0.1887 | 0.0208 | 0.0660 | 0 |
| seed_000.jsonl | `primitive_p0p9_hbm0p06_h0p05_kb0_k0p08_abm0p04_am0p025_ph1p5708` | 139 | 1 | -0.1295 | 0.0406 | 0.0452 | 0 |
| seed_000.jsonl | `primitive_p0p9_hbm0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 150 | 0 | 0.0063 | 0.1329 | 0.1486 | 1 |
| seed_000.jsonl | `primitive_p0p9_hbm0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 150 | 0 | 0.0051 | 0.1106 | 0.1486 | 0 |
| seed_000.jsonl | `primitive_p0p9_hbm0p06_h0p05_kb0p03_k0p08_abm0p04_am0p025_ph0` | 150 | 0 | -0.0034 | 0.1062 | 0.1531 | 1 |
| seed_000.jsonl | `primitive_p0p9_hbm0p06_h0p05_kb0p03_k0p08_abm0p04_am0p025_ph1p5708` | 150 | 0 | -0.0008 | 0.0772 | 0.1533 | 0 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0775 | 0.0702 | 0.2394 | 0.1515 | 0.0000 | 0.3454 | 0.0654 | None | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0746 | 0.1798 | 0.2394 | 0.1515 | 0.0000 | 0.3460 | 0.0863 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0735 | 0.1745 | 0.2081 | 0.1526 | 0.0000 | 0.4466 | 0.0903 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0718 | 0.0647 | 0.2081 | 0.1525 | 0.0000 | 0.4196 | 0.0640 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0565 | 0.0535 | 0.2394 | 0.1515 | 0.0000 | 0.3454 | 0.0654 | None | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 0-24 | 0.0543 | 0.1481 | 0.1621 | 0.1531 | 0.0000 | 0.3443 | 0.0693 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0510 | 0.0919 | 0.1558 | 0.1553 | 0.0000 | 0.3454 | 0.0604 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0499 | 0.1761 | 0.1558 | 0.1538 | 0.0000 | 0.3460 | 0.0841 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p9_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 5-29 | 0.0493 | 0.0515 | 0.1621 | 0.1531 | 0.0000 | 0.3473 | 0.0563 | None | `{'01': 8.0, '11': 92.0}` |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0480 | 0.1724 | 0.1321 | 0.1538 | 0.0000 | 0.4466 | 0.0860 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p9_hbm0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0474 | 0.1245 | 0.2417 | 0.1486 | 0.0000 | 0.3460 | 0.1100 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph1p5708` | 0-24 | 0.0450 | 0.1500 | 0.1452 | 0.1530 | 0.0000 | 0.4388 | 0.0847 | None | `{'01': 16.0, '11': 84.0}` |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0_k0p08_ab0p04_am0p025_ph0` | 5-29 | 0.0449 | 0.0853 | 0.1321 | 0.1557 | 0.0000 | 0.4196 | 0.0566 | None | `{'01': 12.0, '11': 88.0}` |
| seed_000.jsonl | `primitive_p0p7_hbm0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 0-24 | 0.0437 | 0.1237 | 0.2174 | 0.1501 | 0.0000 | 0.4466 | 0.1015 | None | `{'01': 20.0, '11': 80.0}` |
| seed_000.jsonl | `primitive_p0p7_hb0p06_h0p05_kb0p03_k0p08_ab0p04_am0p025_ph0` | 10-34 | 0.0434 | 0.0550 | 0.2081 | 0.1525 | 0.0000 | 0.4410 | 0.0646 | None | `{'11': 100.0}` |
| seed_000.jsonl | `primitive_p0p9_hbm0p06_h0p05_kb0p03_k0p08_abm0p04_am0p025_ph0` | 50-74 | 0.0414 | 0.0425 | 0.0783 | 0.1560 | 0.0000 | 0.3454 | 0.0497 | None | `{'11': 100.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
