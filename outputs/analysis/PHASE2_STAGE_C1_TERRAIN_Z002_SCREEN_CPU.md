# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `rough_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[0, 1]`
eval_push_enable: `False`
eval_push_interval_s: `None`-`None`
eval_push_magnitude: `None`-`None`
push_recovery_window_s: `0.5`
terrain_hfield_z_scale: `0.002`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 | push_events | push_success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `c1_0` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0301 | 0.3758 | 0.1391 | 0.1519 | 1.8078 | 0.0000 | 0.2040 | 0 | NA |
| `c1_0` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0334 | 0.4173 | 0.1402 | 0.1562 | 1.7694 | 0.0000 | 0.1965 | 0 | NA |
| `c1_81920` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0320 | 0.4000 | 0.1366 | 0.1519 | 1.7688 | 0.0000 | 0.2070 | 0 | NA |
| `c1_81920` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0349 | 0.4367 | 0.1416 | 0.1562 | 1.7941 | 0.0000 | 0.1947 | 0 | NA |
| `c1_163840` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0302 | 0.3780 | 0.1266 | 0.1519 | 1.7693 | 0.0000 | 0.2070 | 0 | NA |
| `c1_163840` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0333 | 0.4163 | 0.1393 | 0.1562 | 1.7938 | 0.0000 | 0.1975 | 0 | NA |
| `c1_245760` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0286 | 0.3578 | 0.1320 | 0.1519 | 1.7881 | 0.0000 | 0.2066 | 0 | NA |
| `c1_245760` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0346 | 0.4327 | 0.1382 | 0.1562 | 1.8062 | 0.0000 | 0.1967 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `c1_0` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.3965 | 0.0317 | 0.1396 | 0.1541 | 0.0000 | 0.0000 | NA |
| `c1_81920` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.4184 | 0.0335 | 0.1391 | 0.1541 | 0.0000 | 0.0000 | NA |
| `c1_163840` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.3972 | 0.0318 | 0.1330 | 0.1541 | 0.0000 | 0.0000 | NA |
| `c1_245760` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.3953 | 0.0316 | 0.1351 | 0.1541 | 0.0000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
