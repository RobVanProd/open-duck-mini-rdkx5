# BC Replay Seed Mode Analysis

status: `HOLD_FREEZE_UNCLASSIFIED`

This is an offline analysis of ignored BC replay traces. It does not run
simulation, training, deployment, SSH, or robot tests.

## Summary

- trace_glob: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_bc_student_x008_gate/live_iter2_ppo_loc/seed_*/trace.jsonl`
- command_x: `0.0800`
- moving_threshold_m_s: `0.0200`
- moving_seeds: `[0, 1, 2, 7]`
- frozen_seeds: `[6]`

| group | count | mean_vx | ratio | single_% | double_% | pitch_vel95 | early_action_abs | early_pitch_vel95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| moving | 4 | 0.0223 | 0.2794 | 20.1667 | 79.8333 | 1.5169 | 0.3111 | 1.4870 |
| frozen | 1 | -0.0322 | -0.4030 | 14.9560 | 84.7507 | 1.5132 | 0.3111 | 1.4870 |

## Per Seed

| seed | mode | samples | termination | vx | ratio | single_% | double_% | pitch_vel95 | early_action_abs | early_pitch_vel95 | pitch95 | height_min |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | moving | 750 | duration_complete | 0.0231 | 0.2891 | 18.4000 | 81.6000 | 1.5137 | 0.3111 | 1.4870 | 0.1991 | 0.1575 |
| 1 | moving | 750 | duration_complete | 0.0216 | 0.2700 | 19.3333 | 80.6667 | 1.5202 | 0.3111 | 1.4870 | 0.1931 | 0.1579 |
| 2 | moving | 750 | duration_complete | 0.0226 | 0.2826 | 21.4667 | 78.5333 | 1.5142 | 0.3111 | 1.4870 | 0.1881 | 0.1581 |
| 6 | frozen | 341 | fall_or_progress_failure | -0.0322 | -0.4030 | 14.9560 | 84.7507 | 1.5132 | 0.3111 | 1.4870 | 0.4361 | 0.0731 |
| 7 | moving | 750 | duration_complete | 0.0221 | 0.2758 | 21.4667 | 78.5333 | 1.5195 | 0.3111 | 1.4870 | 0.1841 | 0.1577 |

## Interpretation

- The next student must beat the frozen-seed pattern, not merely reduce fall count.
- If frozen seeds show low action/target velocity and high double support, the next design should add closed-loop selection pressure against quiet double-support dwell.
- No robot validation is implied by this analysis.
