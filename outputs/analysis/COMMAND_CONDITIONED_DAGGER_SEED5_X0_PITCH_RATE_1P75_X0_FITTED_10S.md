# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.0`
task: `flat_terrain_backlash`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `10.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 0 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0005 | NA | 0.0259 | 0.1520 | 0.4460 | 0.0721 |
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 1 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0010 | NA | 0.0256 | 0.1556 | 0.4174 | 0.0688 |
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 2 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0017 | NA | 0.0233 | 0.1509 | 0.3743 | 0.0686 |
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 3 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0055 | NA | 0.0339 | 0.1547 | 0.3681 | 0.0676 |
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 4 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0031 | NA | 0.0220 | 0.1506 | 0.3789 | 0.0691 |
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 5 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0053 | NA | 0.0223 | 0.1462 | 0.5519 | 0.0725 |
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 6 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | -0.0014 | NA | 0.0243 | 0.1557 | 0.4255 | 0.0691 |
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 7 | `PASS_CANDIDATE_SIM_GATE` | 500 | `duration_complete` | 0.0005 | NA | 0.0245 | 0.1559 | 0.3879 | 0.0694 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `command_conditioned_dagger_seed5_x0_pitch_rate_1p75_candidate` | 8 | 0 | 8 | 500.0000 | 500 | 500 | NA | 0.0004 | 0.0252 | 0.1527 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
