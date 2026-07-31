# Phase 2 Live-Oracle Iter0 Terrain z=0.002 Window Source Score

status: `PASS_TERRAIN_WINDOW_SOURCE`

root: `outputs/analysis/phase2_live_oracle_iter0_terrain_z002_swing_gate_cpu/live_oracle_iter0`

## Best By Seed

| seed | window | start | end | mean_vx | sent_vel_p95 | tracking_p95 | single_support | double_support | min_swing_segments | min_rel_x_range | min_peak_lift | failures |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2 | 100 | 60 | 160 | 0.0558 | 2.0902 | 0.1788 | 40.0 | 60.0 | 3 | 0.0098 | 0.0116 | `PASS` |
| 4 | 100 | 140 | 240 | 0.0532 | 2.2194 | 0.1704 | 38.0 | 62.0 | 3 | 0.0156 | 0.0111 | `PASS` |

## Interpretation

- The rough-terrain z=0.002 rollout contains at least one source window per seed that clears the hard-step and corrected-envelope criteria.
- No robot, SSH, deploy, grounded replay, runtime change, or training was performed.
