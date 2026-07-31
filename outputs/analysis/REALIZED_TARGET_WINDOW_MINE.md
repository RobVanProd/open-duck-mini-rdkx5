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
| phase1_x008_trace.jsonl | `fitted` | 80 | 1 | 0.1892 | 1.2424 | 0.0434 | 6 |
| v7_x008_trace.jsonl | `vanilla` | 750 | 0 | 0.0018 | 0.1921 | 0.1506 | 2 |
| v7_x008_trace.jsonl | `fitted` | 59 | 1 | 0.2654 | 1.3183 | 0.0388 | 3 |
| v7_x008_trace.jsonl | `stress` | 750 | 0 | 0.0016 | 0.1558 | 0.1499 | 4 |
| trace_seed0.jsonl | `fitted` | 750 | 0 | 0.0015 | 0.1381 | 0.1511 | 2 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| v7_x008_trace.jsonl | `fitted` | 5-29 | 0.1071 | 0.1649 | 0.3954 | 0.1500 | 0.0000 | 1.3416 | 0.0907 | 29 | `{'01': 20.0, '11': 80.0}` |
| v7_x008_trace.jsonl | `fitted` | 10-34 | 0.1057 | 0.1500 | 0.4356 | 0.1500 | 0.0000 | 0.6808 | 0.0818 | 24 | `{'01': 4.0, '11': 96.0}` |
| phase1_x008_trace.jsonl | `fitted` | 5-29 | 0.1023 | 0.1676 | 0.3555 | 0.1489 | 0.0000 | 1.2030 | 0.0812 | 50 | `{'01': 20.0, '10': 4.0, '11': 76.0}` |
| v7_x008_trace.jsonl | `fitted` | 0-24 | 0.0985 | 0.1792 | 0.3629 | 0.1500 | 0.0000 | 2.0062 | 0.1111 | 34 | `{'01': 28.000000000000004, '11': 72.0}` |
| phase1_x008_trace.jsonl | `fitted` | 0-24 | 0.0906 | 0.1676 | 0.3144 | 0.1506 | 0.0000 | 2.3110 | 0.1095 | 55 | `{'01': 28.000000000000004, '10': 4.0, '11': 68.0}` |
| phase1_x008_trace.jsonl | `fitted` | 10-34 | 0.0857 | 0.1609 | 0.3853 | 0.1474 | 0.0000 | 0.7491 | 0.0674 | 45 | `{'10': 4.0, '11': 96.0}` |
| phase1_x008_trace.jsonl | `fitted` | 15-39 | 0.0694 | 0.0289 | 0.4085 | 0.1471 | 0.0000 | 0.2365 | 0.0698 | 40 | `{'11': 100.0}` |
| trace_seed0.jsonl | `fitted` | 0-24 | 0.0666 | 0.1439 | 0.2803 | 0.1511 | 0.0000 | 2.3502 | 0.1248 | None | `{'01': 24.0, '10': 4.0, '11': 72.0}` |
| v7_x008_trace.jsonl | `vanilla` | 0-24 | 0.0656 | 0.0956 | 0.2717 | 0.1513 | 0.0000 | 1.9668 | 0.0971 | None | `{'01': 8.0, '11': 92.0}` |
| v7_x008_trace.jsonl | `stress` | 5-29 | 0.0562 | 0.1701 | 0.2621 | 0.1499 | 0.0000 | 1.4137 | 0.0893 | None | `{'01': 16.0, '10': 4.0, '11': 80.0}` |
| v7_x008_trace.jsonl | `stress` | 10-34 | 0.0558 | 0.1495 | 0.2626 | 0.1499 | 0.0000 | 0.9816 | 0.0771 | None | `{'01': 4.0, '10': 4.0, '11': 92.0}` |
| phase1_x008_trace.jsonl | `fitted` | 20-44 | 0.0552 | 0.0289 | 0.4246 | 0.1471 | 0.0000 | 0.1941 | 0.0733 | 35 | `{'11': 100.0}` |
| trace_seed0.jsonl | `fitted` | 5-29 | 0.0535 | 0.1235 | 0.2805 | 0.1511 | 0.0000 | 1.7842 | 0.1011 | None | `{'01': 16.0, '10': 4.0, '11': 80.0}` |
| v7_x008_trace.jsonl | `stress` | 0-24 | 0.0534 | 0.1844 | 0.2196 | 0.1506 | 0.0000 | 2.0543 | 0.1198 | None | `{'01': 24.0, '10': 4.0, '11': 72.0}` |
| v7_x008_trace.jsonl | `vanilla` | 5-29 | 0.0515 | 0.0374 | 0.2717 | 0.1513 | 0.0000 | 0.8058 | 0.0709 | None | `{'11': 100.0}` |
| v7_x008_trace.jsonl | `stress` | 15-39 | 0.0451 | 0.0405 | 0.2626 | 0.1499 | 0.0000 | 0.3851 | 0.0777 | None | `{'11': 100.0}` |
| phase1_x008_trace.jsonl | `fitted` | 25-49 | 0.0418 | 0.0292 | 0.4411 | 0.1471 | 0.0000 | 0.1926 | 0.0799 | 30 | `{'11': 100.0}` |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
