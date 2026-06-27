# BC Replay Seed Mode Analysis

status: `HOLD_FREEZE_LOW_ACTION_DOUBLE_SUPPORT`

This is an offline analysis of ignored BC replay traces. It does not run
simulation, training, deployment, SSH, or robot tests.

## Summary

- trace_glob: `outputs/analysis/closed_loop_teacher_dataset_blend080_bc_gate_x008_traces/*.jsonl`
- command_x: `0.0800`
- moving_threshold_m_s: `0.0200`
- moving_seeds: `[0, 2, 3, 5, 6]`
- frozen_seeds: `[1, 4, 7]`

| group | count | mean_vx | ratio | single_% | double_% | pitch_vel95 | early_action_abs | early_pitch_vel95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| moving | 5 | 0.0586 | 0.7319 | 46.2400 | 53.5200 | 3.1944 | 0.3229 | 3.3032 |
| frozen | 3 | 0.0031 | 0.0391 | 2.6667 | 97.2000 | 0.3986 | 0.4299 | 2.1046 |

## Per Seed

| seed | mode | samples | termination | vx | ratio | single_% | double_% | pitch_vel95 | early_action_abs | early_pitch_vel95 | pitch95 | height_min |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | moving | 250 | duration_complete | 0.0622 | 0.7777 | 47.6000 | 52.4000 | 3.1521 | 0.3236 | 3.2519 | 0.0673 | 0.1519 |
| 1 | frozen | 250 | duration_complete | 0.0001 | 0.0008 | 2.8000 | 96.8000 | 0.4642 | 0.4279 | 2.1683 | 0.0553 | 0.1559 |
| 2 | moving | 250 | duration_complete | 0.0648 | 0.8106 | 47.6000 | 52.4000 | 3.1928 | 0.3209 | 3.3494 | 0.0586 | 0.1511 |
| 3 | moving | 250 | duration_complete | 0.0445 | 0.5558 | 45.2000 | 54.4000 | 3.1570 | 0.3245 | 2.9565 | 0.1255 | 0.1535 |
| 4 | frozen | 250 | duration_complete | 0.0070 | 0.0872 | 1.6000 | 98.4000 | 0.3686 | 0.4322 | 2.1086 | 0.0577 | 0.1509 |
| 5 | moving | 250 | duration_complete | 0.0645 | 0.8062 | 40.4000 | 58.8000 | 3.2935 | 0.3240 | 3.4830 | 0.1245 | 0.1462 |
| 6 | moving | 250 | duration_complete | 0.0567 | 0.7093 | 50.4000 | 49.6000 | 3.1768 | 0.3213 | 3.4750 | 0.0609 | 0.1556 |
| 7 | frozen | 250 | duration_complete | 0.0023 | 0.0292 | 3.6000 | 96.4000 | 0.3629 | 0.4296 | 2.0368 | 0.0480 | 0.1558 |

## Interpretation

- The next student must beat the frozen-seed pattern, not merely reduce fall count.
- If frozen seeds show low action/target velocity and high double support, the next design should add closed-loop selection pressure against quiet double-support dwell.
- No robot validation is implied by this analysis.
