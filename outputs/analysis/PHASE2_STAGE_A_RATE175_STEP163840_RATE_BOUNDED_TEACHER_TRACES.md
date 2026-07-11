# Phase 2 Rate-Bounded On-Policy Teacher Traces

status: `PASS_RATE_BOUNDED_TEACHER_TRACES_READY`

Offline target-manifold analysis only. No training, deployment, SSH, local GPU, or robot operation was performed.

## Summary

- traces/samples: `8` / `400`
- original teacher target-rate p95/max: `1.6771` / `2.6084` rad/s
- bounded teacher target-rate p95/max: `1.6844` / `2.0000` rad/s
- bounded-vs-teacher action mean/p95/max: `0.0002` / `0.0000` / `0.0951`
- changed pitch-chain values: `33`

## Per Trace

| trace | transitions | changed | original max | bounded max | distortion p95 | transition distortion p95 | ordinary distortion p95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `seed_000` | 11 | 0 | 1.9960 | 1.9960 | 0.0000 | 0.0000 | 0.0000 |
| `seed_001` | 7 | 2 | 2.1104 | 2.0000 | 0.0000 | 0.0000 | 0.0000 |
| `seed_002` | 12 | 1 | 2.0058 | 2.0000 | 0.0000 | 0.0000 | 0.0000 |
| `seed_003` | 11 | 13 | 2.6084 | 2.0000 | 0.0000 | 0.0000 | 0.0482 |
| `seed_004` | 9 | 5 | 2.3705 | 2.0000 | 0.0000 | 0.0000 | 0.0000 |
| `seed_005` | 5 | 11 | 2.6052 | 2.0000 | 0.0000 | 0.0000 | 0.0000 |
| `seed_006` | 14 | 1 | 2.0881 | 2.0000 | 0.0000 | 0.0000 | 0.0000 |
| `seed_007` | 16 | 0 | 1.9265 | 1.9265 | 0.0000 | 0.0000 | 0.0000 |
