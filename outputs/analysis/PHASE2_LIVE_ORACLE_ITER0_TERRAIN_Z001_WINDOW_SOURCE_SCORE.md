# Phase 2 Live-Oracle Iter0 Terrain z=0.001 Window Source Score

status: `PASS_TERRAIN_WINDOW_SOURCE`

root: `outputs/analysis/phase2_live_oracle_iter0_terrain_z001_swing_gate_cpu/live_oracle_iter0`

## Best By Seed

| seed | window | start | end | mean_vx | sent_vel_p95 | tracking_p95 | single_support | double_support | min_swing_segments | min_rel_x_range | min_peak_lift | failures |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2 | 100 | 80 | 180 | 0.0560 | 2.1892 | 0.1764 | 41.0 | 59.0 | 3 | 0.0085 | 0.0120 | `PASS` |
| 4 | 100 | 90 | 190 | 0.0493 | 1.9976 | 0.1714 | 39.0 | 61.0 | 3 | 0.0168 | 0.0112 | `PASS` |

## Interpretation

- The rough-terrain rollout contains at least one source window per seed that clears the hard-step and corrected-envelope criteria.
- No robot, SSH, deploy, grounded replay, runtime change, or training was performed.
