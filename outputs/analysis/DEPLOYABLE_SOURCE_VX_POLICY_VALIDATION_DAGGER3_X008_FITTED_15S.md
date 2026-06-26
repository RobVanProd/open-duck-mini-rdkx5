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
| `dagger3_128` | 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0196 | 0.2454 | 0.0490 | 0.1536 | 3.2894 | 0.2171 |
| `dagger3_128` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 31 | `fall_or_nan` | 0.0199 | 0.2487 | 0.0003 | 0.0897 | 2.8691 | 0.3068 |
| `dagger3_128` | 2 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0219 | 0.2739 | 0.0536 | 0.1525 | 3.3154 | 0.2166 |
| `dagger3_128` | 3 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0203 | 0.2532 | 0.0550 | 0.1582 | 3.2986 | 0.2151 |
| `dagger3_128` | 4 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0222 | 0.2777 | 0.0565 | 0.1515 | 3.3225 | 0.2169 |
| `dagger3_128` | 5 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0245 | 0.3056 | 0.0517 | 0.1467 | 3.3275 | 0.2216 |
| `dagger3_128` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0189 | 0.2361 | 0.0577 | 0.1583 | 3.3210 | 0.2183 |
| `dagger3_128` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | 0.0274 | 0.3427 | 0.0336 | 0.0819 | 2.4139 | 0.3278 |
| `dagger3_512` | 0 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0249 | 0.3108 | 0.0572 | 0.1536 | 3.4721 | 0.2242 |
| `dagger3_512` | 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | 0.0128 | 0.1597 | 0.0003 | 0.0860 | 2.2969 | 0.2813 |
| `dagger3_512` | 2 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0252 | 0.3155 | 0.0572 | 0.1525 | 3.4347 | 0.2208 |
| `dagger3_512` | 3 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0239 | 0.2990 | 0.0598 | 0.1575 | 3.5095 | 0.2228 |
| `dagger3_512` | 4 | `HOLD_CANDIDATE_TRACKING` | 750 | `duration_complete` | 0.0231 | 0.2889 | 0.0604 | 0.1515 | 3.4758 | 0.2228 |
| `dagger3_512` | 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 72 | `fall_or_nan` | -0.2003 | -2.5032 | 0.0960 | 0.0678 | 3.2574 | 0.2805 |
| `dagger3_512` | 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | `duration_complete` | 0.0183 | 0.2291 | 0.0668 | 0.1578 | 3.4836 | 0.2202 |
| `dagger3_512` | 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | 0.0161 | 0.2018 | 0.0083 | 0.0747 | 3.1984 | 0.3235 |

## Distribution Summary

| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dagger3_128` | 8 | 2 | 6 | 570.5000 | 31 | 750 | 0.2729 | 0.0218 | 0.0447 | 0.1365 |
| `dagger3_512` | 8 | 3 | 5 | 486.0000 | 33 | 750 | -0.0873 | -0.0070 | 0.0507 | 0.1252 |

## Interpretation

- Treat this as a stability distribution, not a deployability approval.
- A candidate still needs the standard full-duration x=0.0 and x=0.08
  gates reviewed before any robot-side validation.
- If fall samples vary widely across seeds, grade later recipes by
  distribution shift, not by a single lucky rollout.
