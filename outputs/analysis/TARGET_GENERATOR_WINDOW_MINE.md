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
| seed_000.jsonl | `primitive_p0p7_h0p03_k0p04_am0p015_ph0` | 150 | 0 | -0.0002 | 0.0531 | 0.1536 | 0 |
| seed_000.jsonl | `primitive_p0p7_h0p03_k0p04_am0p015_ph1p5708` | 150 | 0 | 0.0005 | 0.0539 | 0.1536 | 0 |
| seed_000.jsonl | `primitive_p0p7_h0p03_k0p04_am0p03_ph0` | 150 | 0 | -0.0004 | 0.0530 | 0.1536 | 0 |
| seed_000.jsonl | `primitive_p0p7_h0p03_k0p04_am0p03_ph1p5708` | 150 | 0 | 0.0007 | 0.0547 | 0.1536 | 0 |
| seed_000.jsonl | `primitive_p0p7_h0p03_k0p08_am0p015_ph0` | 150 | 0 | 0.0003 | 0.0503 | 0.1536 | 0 |
| seed_000.jsonl | `primitive_p0p7_h0p03_k0p08_am0p015_ph1p5708` | 150 | 0 | 0.0016 | 0.0450 | 0.1536 | 0 |
| seed_000.jsonl | `primitive_p0p7_h0p03_k0p08_am0p03_ph0` | 150 | 0 | 0.0002 | 0.0574 | 0.1536 | 0 |
| seed_000.jsonl | `primitive_p0p7_h0p03_k0p08_am0p03_ph1p5708` | 150 | 0 | 0.0018 | 0.0583 | 0.1536 | 0 |
| seed_000.jsonl | `primitive_p0p7_h0p05_k0p04_am0p025_ph0` | 150 | 0 | -0.0006 | 0.0717 | 0.1536 | 0 |
| seed_000.jsonl | `primitive_p0p7_h0p05_k0p04_am0p025_ph1p5708` | 150 | 0 | 0.0015 | 0.0690 | 0.1536 | 0 |
| seed_000.jsonl | `primitive_p0p7_h0p05_k0p04_am0p05_ph0` | 150 | 0 | -0.0009 | 0.0796 | 0.1536 | 0 |
| seed_000.jsonl | `primitive_p0p7_h0p05_k0p04_am0p05_ph1p5708` | 150 | 0 | 0.0014 | 0.0786 | 0.1536 | 0 |

## Top Candidate Windows

| source | mode | ticks | mean_vx | vy_abs_p95 | pitch_p95 | min_height | sat_pct | sent_vel_p95 | track_p95 | done_margin | contacts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| NA | NA | NA | NA | NA | NA | NA | NA | NA | NA | NA | NA |

## Interpretation

- Candidate windows are short pre-fall or non-fall snippets, not deployable policies.
- If only short windows exist before later falls, use them as motion hints, not as a full walking dataset.
- If no windows pass, the next step is to generate realized stable targets deliberately in sim.
