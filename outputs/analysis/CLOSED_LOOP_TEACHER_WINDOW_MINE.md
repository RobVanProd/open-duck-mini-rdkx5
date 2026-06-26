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
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0714 | 0.1917 | 0.1521 | 46 |
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0619 | 0.1307 | 0.1513 | 43 |
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0731 | 0.2495 | 0.1510 | 46 |
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0572 | 0.0961 | 0.1568 | 42 |
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0392 | 0.2051 | 0.1506 | 19 |
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0682 | 0.2399 | 0.1451 | 44 |
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0679 | 0.1160 | 0.1556 | 45 |
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0729 | 0.1301 | 0.1558 | 46 |
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0662 | 0.1704 | 0.1520 | 46 |
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0504 | 0.1241 | 0.1511 | 32 |
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0618 | 0.2638 | 0.1510 | 41 |
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0540 | 0.1047 | 0.1570 | 42 |
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0102 | 0.2058 | 0.1506 | 2 |
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0644 | 0.2401 | 0.1452 | 44 |
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0609 | 0.1024 | 0.1556 | 44 |
| trace_full_obs_footpos.jsonl | `vanilla` | 250 | 0 | 0.0640 | 0.1325 | 0.1558 | 46 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| trace_full_obs_footpos.jsonl | `vanilla` | 0-24 | 0.1104 | 0.1487 | 0.0306 | 0.1510 | 0.0000 | 3.2526 | 0.1430 | None | `{'01': 24.0, '10': 24.0, '11': 52.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 0-24 | 0.1008 | 0.1331 | 0.0415 | 0.1510 | 0.0000 | 2.7390 | 0.1181 | None | `{'01': 24.0, '10': 24.0, '11': 52.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 5-29 | 0.0944 | 0.1618 | 0.0329 | 0.1598 | 0.0000 | 2.6524 | 0.1192 | None | `{'01': 16.0, '10': 32.0, '11': 52.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 0-24 | 0.0929 | 0.1398 | 0.0566 | 0.1521 | 0.0000 | 3.3088 | 0.1392 | None | `{'01': 32.0, '10': 8.0, '11': 60.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 0-24 | 0.0855 | 0.1628 | 0.0797 | 0.1506 | 0.0000 | 3.1965 | 0.1295 | None | `{'01': 16.0, '10': 12.0, '11': 72.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 25-49 | 0.0847 | 0.1650 | 0.0578 | 0.1601 | 0.0000 | 2.5501 | 0.1228 | None | `{'01': 28.000000000000004, '10': 16.0, '11': 56.00000000000001}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 5-29 | 0.0833 | 0.1742 | 0.0569 | 0.1591 | 0.0000 | 2.5879 | 0.1269 | None | `{'01': 24.0, '10': 28.000000000000004, '11': 48.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 0-24 | 0.0831 | 0.1516 | 0.0802 | 0.1506 | 0.0000 | 3.3980 | 0.1271 | None | `{'01': 16.0, '10': 8.0, '11': 76.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 190-214 | 0.0818 | 0.1931 | 0.0439 | 0.1622 | 0.0000 | 2.4517 | 0.1250 | None | `{'01': 28.000000000000004, '10': 20.0, '11': 52.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 110-134 | 0.0817 | 0.1984 | 0.0510 | 0.1626 | 0.0000 | 2.4810 | 0.1143 | None | `{'01': 32.0, '10': 20.0, '11': 48.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 5-29 | 0.0809 | 0.1434 | 0.0532 | 0.1562 | 0.0000 | 2.5848 | 0.1088 | None | `{'01': 16.0, '10': 24.0, '11': 60.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 10-34 | 0.0809 | 0.1618 | 0.0369 | 0.1598 | 0.0000 | 2.5406 | 0.1220 | None | `{'01': 16.0, '10': 24.0, '11': 60.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 115-139 | 0.0801 | 0.1985 | 0.0510 | 0.1628 | 0.0000 | 2.5109 | 0.1193 | None | `{'01': 32.0, '10': 32.0, '11': 36.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 110-134 | 0.0798 | 0.1882 | 0.0503 | 0.1624 | 0.0000 | 2.4582 | 0.1134 | None | `{'01': 32.0, '10': 20.0, '11': 48.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 30-54 | 0.0796 | 0.1626 | 0.0585 | 0.1607 | 0.0000 | 2.5775 | 0.1178 | None | `{'01': 28.000000000000004, '10': 20.0, '11': 52.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 205-229 | 0.0795 | 0.1970 | 0.0503 | 0.1622 | 0.0000 | 2.4834 | 0.1224 | None | `{'01': 20.0, '10': 28.000000000000004, '11': 52.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 200-224 | 0.0794 | 0.1970 | 0.0439 | 0.1622 | 0.0000 | 2.5658 | 0.1233 | None | `{'01': 24.0, '10': 28.000000000000004, '11': 48.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 195-219 | 0.0794 | 0.1970 | 0.0439 | 0.1622 | 0.0000 | 2.5907 | 0.1268 | None | `{'01': 28.000000000000004, '10': 28.000000000000004, '11': 44.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 105-129 | 0.0793 | 0.1984 | 0.0503 | 0.1625 | 0.0000 | 2.4453 | 0.1156 | None | `{'01': 32.0, '10': 24.0, '11': 44.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 220-244 | 0.0792 | 0.1728 | 0.0489 | 0.1625 | 0.0000 | 2.5462 | 0.1201 | None | `{'01': 28.000000000000004, '10': 24.0, '11': 48.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 105-129 | 0.0791 | 0.1882 | 0.0503 | 0.1624 | 0.0000 | 2.3456 | 0.1156 | None | `{'01': 32.0, '10': 24.0, '11': 44.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 100-124 | 0.0790 | 0.1674 | 0.0489 | 0.1625 | 0.0000 | 2.5898 | 0.1156 | None | `{'01': 28.000000000000004, '10': 28.000000000000004, '11': 44.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 80-104 | 0.0789 | 0.1816 | 0.0515 | 0.1621 | 0.0000 | 2.5732 | 0.1173 | None | `{'01': 32.0, '10': 20.0, '11': 48.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 80-104 | 0.0788 | 0.1839 | 0.0509 | 0.1624 | 0.0000 | 2.4327 | 0.1208 | None | `{'01': 28.000000000000004, '10': 20.0, '11': 52.0}` |
| trace_full_obs_footpos.jsonl | `vanilla` | 15-39 | 0.0787 | 0.1608 | 0.0524 | 0.1598 | 0.0000 | 2.5406 | 0.1304 | None | `{'01': 12.0, '10': 24.0, '11': 64.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
