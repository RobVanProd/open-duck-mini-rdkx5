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
| `c2_0` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0320 | 0.4000 | 0.1366 | 0.1519 | 1.7688 | 0.0000 | 0.2070 | 0 | NA |
| `c2_0` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0349 | 0.4367 | 0.1416 | 0.1562 | 1.7941 | 0.0000 | 0.1947 | 0 | NA |
| `c2_81920` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0293 | 0.3662 | 0.1270 | 0.1519 | 1.7857 | 0.0000 | 0.2049 | 0 | NA |
| `c2_81920` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0321 | 0.4019 | 0.1349 | 0.1562 | 1.7739 | 0.0000 | 0.1965 | 0 | NA |
| `c2_163840` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0309 | 0.3866 | 0.1357 | 0.1519 | 1.8222 | 0.0000 | 0.2044 | 0 | NA |
| `c2_163840` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0342 | 0.4274 | 0.1402 | 0.1562 | 1.7909 | 0.0000 | 0.1941 | 0 | NA |
| `c2_245760` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0293 | 0.3657 | 0.1290 | 0.1519 | 1.7701 | 0.0000 | 0.2057 | 0 | NA |
| `c2_245760` | 1 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0343 | 0.4285 | 0.1423 | 0.1562 | 1.8288 | 0.0000 | 0.1969 | 0 | NA |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean | push_events_mean | push_success_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `c2_0` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.4184 | 0.0335 | 0.1391 | 0.1541 | 0.0000 | 0.0000 | NA |
| `c2_81920` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.3840 | 0.0307 | 0.1310 | 0.1541 | 0.0000 | 0.0000 | NA |
| `c2_163840` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.4070 | 0.0326 | 0.1379 | 0.1541 | 0.0000 | 0.0000 | NA |
| `c2_245760` | 2 | 0 | 2 | 250.0000 | 250 | 250 | 0.3971 | 0.0318 | 0.1357 | 0.1540 | 0.0000 | 0.0000 | NA |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
