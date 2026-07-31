# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `3.0`
seeds: `[0, 1]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_vel_excess | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `dagger_iter3` | 0 | `HOLD_CANDIDATE_TRACKING` | 150 | `duration_complete` | 0.0452 | 0.5647 | 0.1007 | 0.1520 | 3.6144 | 0.8644 | 0.2557 |
| `dagger_iter3` | 1 | `HOLD_CANDIDATE_TRACKING` | 150 | `duration_complete` | 0.0414 | 0.5173 | 0.0928 | 0.1556 | 3.7267 | 1.1265 | 0.2551 |
| `phase_quadrant` | 0 | `HOLD_CANDIDATE_TRACKING` | 150 | `duration_complete` | 0.0439 | 0.5486 | 0.1110 | 0.1520 | 4.3856 | 1.6356 | 0.2691 |
| `phase_quadrant` | 1 | `HOLD_CANDIDATE_TRACKING` | 150 | `duration_complete` | 0.0390 | 0.4880 | 0.1017 | 0.1556 | 4.7190 | 1.9690 | 0.2625 |
| `phase_smooth` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 150 | `duration_complete` | 0.0143 | 0.1788 | 0.0675 | 0.1520 | 4.6032 | 1.8532 | 0.2486 |
| `phase_smooth` | 1 | `HOLD_CANDIDATE_TRACKING` | 150 | `duration_complete` | 0.0358 | 0.4479 | 0.0995 | 0.1556 | 4.3406 | 1.5906 | 0.2594 |
| `gate_aware_smoke` | 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 82 | `fall_or_nan` | -0.1921 | -2.4018 | 0.0156 | 0.0938 | 5.2400 | 2.4900 | 0.3990 |
| `gate_aware_smoke` | 1 | `HOLD_CANDIDATE_ACTION_SATURATION` | 150 | `duration_complete` | 0.0317 | 0.3966 | 0.3174 | 0.1556 | 5.2400 | 2.4900 | 0.2752 |
| `ppo_warmstart` | 0 | `HOLD_CANDIDATE_TRACKING` | 150 | `duration_complete` | 0.0429 | 0.5362 | 0.1071 | 0.1520 | 3.6854 | 0.9354 | 0.2534 |
| `ppo_warmstart` | 1 | `HOLD_CANDIDATE_TRACKING` | 150 | `duration_complete` | 0.0393 | 0.4911 | 0.0984 | 0.1556 | 3.6415 | 0.8915 | 0.2452 |
| `cmd_conditioned` | 0 | `PASS_CANDIDATE_SIM_GATE` | 150 | `duration_complete` | 0.0352 | 0.4405 | 0.1115 | 0.1520 | 1.7698 | 0.0000 | 0.1991 |
| `cmd_conditioned` | 1 | `PASS_CANDIDATE_SIM_GATE` | 150 | `duration_complete` | 0.0297 | 0.3714 | 0.1141 | 0.1556 | 1.7503 | 0.0000 | 0.1909 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | max_vel_excess_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dagger_iter3` | 2 | 0 | 2 | 150.0000 | 150 | 150 | 0.5410 | 0.0433 | 0.0968 | 0.1538 | 0.9955 |
| `phase_quadrant` | 2 | 0 | 2 | 150.0000 | 150 | 150 | 0.5183 | 0.0415 | 0.1064 | 0.1538 | 1.8023 |
| `phase_smooth` | 2 | 0 | 2 | 150.0000 | 150 | 150 | 0.3134 | 0.0251 | 0.0835 | 0.1538 | 1.7219 |
| `gate_aware_smoke` | 2 | 1 | 1 | 116.0000 | 82 | 150 | -1.0026 | -0.0802 | 0.1665 | 0.1247 | 2.4900 |
| `ppo_warmstart` | 2 | 0 | 2 | 150.0000 | 150 | 150 | 0.5136 | 0.0411 | 0.1027 | 0.1538 | 0.9135 |
| `cmd_conditioned` | 2 | 0 | 2 | 150.0000 | 150 | 150 | 0.4059 | 0.0325 | 0.1128 | 0.1538 | 0.0000 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
