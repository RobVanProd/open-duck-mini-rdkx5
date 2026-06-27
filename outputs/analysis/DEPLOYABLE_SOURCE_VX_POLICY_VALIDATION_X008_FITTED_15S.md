# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
task: `flat_terrain`
bridge_mode: `fitted`
reward_overrides_json: `None`
reward_overrides_phase: `None`
duration_s: `15.0`
seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
trace_seeds: `[]`
trace_full_obs: `False`
run: `True`

## Per-Seed Results

| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| `dagger2` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0191 | 0.2387 | 0.0478 | 0.1536 | 3.8414 | 0.2166 |
| `dagger2` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | 0.0160 | 0.1999 | 0.0011 | 0.0686 | 2.4613 | 0.3055 |
| `dagger2` | 2 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0208 | 0.2598 | 0.0490 | 0.1525 | 3.7729 | 0.2160 |
| `dagger2` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0177 | 0.2208 | 0.0520 | 0.1573 | 3.7577 | 0.2142 |
| `dagger2` | 4 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0215 | 0.2693 | 0.0540 | 0.1515 | 3.8905 | 0.2166 |
| `dagger2` | 5 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0231 | 0.2884 | 0.0474 | 0.1467 | 3.8828 | 0.2153 |
| `dagger2` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0186 | 0.2329 | 0.0543 | 0.1576 | 3.8312 | 0.2147 |
| `dagger2` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 35 | `fall_or_nan` | 0.0224 | 0.2797 | 0.0094 | 0.0710 | 3.0224 | 0.3058 |
| `dagger2_rate` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0117 | 0.1462 | 0.0455 | 0.1536 | 2.9935 | 0.2034 |
| `dagger2_rate` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 31 | `fall_or_nan` | 0.0214 | 0.2677 | 0.0003 | 0.0820 | 2.6618 | 0.3047 |
| `dagger2_rate` | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0143 | 0.1794 | 0.0477 | 0.1525 | 3.0264 | 0.2008 |
| `dagger2_rate` | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0099 | 0.1240 | 0.0508 | 0.1580 | 3.0328 | 0.2044 |
| `dagger2_rate` | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0148 | 0.1845 | 0.0479 | 0.1515 | 3.0383 | 0.2049 |
| `dagger2_rate` | 5 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0148 | 0.1851 | 0.0474 | 0.1467 | 3.0300 | 0.2053 |
| `dagger2_rate` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0132 | 0.1647 | 0.0499 | 0.1578 | 3.0582 | 0.2036 |
| `dagger2_rate` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | 0.0181 | 0.2265 | 0.0313 | 0.0817 | 2.6691 | 0.3134 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dagger2` | 8 | 2 | 6 | 571.0000 | 33 | 750 | 0.2487 | 0.0199 | 0.0394 | 0.1324 |
| `dagger2_rate` | 8 | 2 | 6 | 570.5000 | 31 | 750 | 0.1847 | 0.0148 | 0.0401 | 0.1355 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
