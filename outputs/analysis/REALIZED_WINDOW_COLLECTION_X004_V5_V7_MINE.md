# Realized Target Window Mine

status: `HOLD_NO_REALIZED_WINDOWS`

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
| trace.jsonl | `vanilla` | 250 | 0 | 0.0018 | 0.1123 | 0.1537 | 0 |
| trace.jsonl | `vanilla` | 34 | 1 | -0.1549 | 0.0064 | 0.0884 | 0 |
| trace.jsonl | `vanilla` | 250 | 0 | 0.0033 | 0.0959 | 0.1526 | 0 |
| trace.jsonl | `vanilla` | 250 | 0 | -0.0088 | 0.0096 | 0.1549 | 0 |
| trace.jsonl | `vanilla` | 250 | 0 | 0.0013 | 0.0807 | 0.1539 | 0 |
| trace.jsonl | `vanilla` | 35 | 1 | -0.1641 | -0.0110 | 0.1059 | 0 |
| trace.jsonl | `vanilla` | 250 | 0 | 0.0019 | 0.0882 | 0.1526 | 0 |
| trace.jsonl | `vanilla` | 250 | 0 | -0.0090 | 0.0269 | 0.1558 | 0 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| NA | NA | NA | NA | NA | NA | NA | NA | NA | NA | NA | NA |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
