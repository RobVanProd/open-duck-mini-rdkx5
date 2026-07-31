# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `5.0`
seeds: `[0]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `a2_164k` | 0 | `HOLD_CANDIDATE_TRACKING` | 250 | `duration_complete` | 0.0300 | 0.3755 | 0.1089 | 0.1520 | 1.7906 | 0.0000 | 0.2027 |
| `a2_328k` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0216 | 0.2704 | 0.0915 | 0.1520 | 1.7201 | 0.0000 | 0.1924 |
| `a2_492k` | 0 | `PASS_CANDIDATE_SIM_GATE` | 250 | `duration_complete` | 0.0218 | 0.2723 | 0.0911 | 0.1520 | 1.5751 | 0.0000 | 0.1820 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `a2_164k` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.3755 | 0.0300 | 0.1089 | 0.1520 | 0.0000 |
| `a2_328k` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.2704 | 0.0216 | 0.0915 | 0.1520 | 0.0000 |
| `a2_492k` | 1 | 0 | 1 | 250.0000 | 250 | 250 | 0.2723 | 0.0218 | 0.0911 | 0.1520 | 0.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
