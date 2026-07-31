# Candidate Seed Sweep

Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,
train, or touch the robot.

command_x: `0.08`
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
| `pitch_chain_4p3` | 0 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0494 | 0.6171 | 0.0988 | 0.1520 | 4.2240 | 0.2719 |
| `pitch_chain_4p3` | 1 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0461 | 0.5759 | 0.0957 | 0.1556 | 4.2879 | 0.2794 |
| `pitch_chain_4p3` | 2 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0517 | 0.6464 | 0.0972 | 0.1509 | 4.2395 | 0.2743 |
| `pitch_chain_4p3` | 3 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0432 | 0.5394 | 0.1005 | 0.1549 | 4.1935 | 0.2685 |
| `pitch_chain_4p3` | 4 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0475 | 0.5933 | 0.0983 | 0.1506 | 4.2663 | 0.2721 |
| `pitch_chain_4p3` | 5 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0503 | 0.6290 | 0.0956 | 0.1462 | 4.2265 | 0.2719 |
| `pitch_chain_4p3` | 6 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0460 | 0.5755 | 0.1000 | 0.1557 | 4.2533 | 0.2762 |
| `pitch_chain_4p3` | 7 | `HOLD_CANDIDATE_TRACKING` | 500 | `duration_complete` | 0.0476 | 0.5954 | 0.0991 | 0.1559 | 4.2281 | 0.2737 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `pitch_chain_4p3` | 8 | 0 | 8 | 500.0000 | 500 | 500 | 0.5965 | 0.0477 | 0.0982 | 0.1527 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
