# BC Replay Seed Mode Analysis

status: `HOLD_FREEZE_DOUBLE_SUPPORT`

This is an offline analysis of ignored BC replay traces. It does not run
simulation, training, deployment, SSH, or robot tests.

## Summary

- trace_glob: `outputs/analysis/closed_loop_teacher_dataset_knn5_bc_gate_x008_traces/*.jsonl`
- command_x: `0.0800`
- moving_threshold_m_s: `0.0200`
- moving_seeds: `[0, 1, 2, 5, 6]`
- frozen_seeds: `[3, 4, 7]`

| group | count | mean_vx | ratio | single_% | double_% | pitch_vel95 | early_action_abs | early_pitch_vel95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| moving | 5 | 0.0698 | 0.8723 | 51.7600 | 48.0800 | 3.1605 | 0.3270 | 3.3671 |
| frozen | 3 | -0.0722 | -0.9028 | 11.8599 | 87.7181 | 1.4962 | 0.3979 | 2.4580 |

## Per Seed

| seed | mode | samples | termination | vx | ratio | single_% | double_% | pitch_vel95 | early_action_abs | early_pitch_vel95 | pitch95 | height_min |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | moving | 250 | duration_complete | 0.0700 | 0.8753 | 51.2000 | 48.8000 | 3.1765 | 0.3266 | 3.3428 | 0.0595 | 0.1519 |
| 1 | moving | 250 | duration_complete | 0.0697 | 0.8718 | 54.4000 | 45.6000 | 3.1987 | 0.3253 | 3.4748 | 0.0627 | 0.1559 |
| 2 | moving | 250 | duration_complete | 0.0729 | 0.9109 | 52.0000 | 48.0000 | 3.1069 | 0.3250 | 3.1081 | 0.0590 | 0.1511 |
| 3 | frozen | 79 | fall_or_progress_failure | -0.2268 | -2.8350 | 30.3797 | 68.3544 | 3.6120 | 0.3301 | 3.2554 | 1.1177 | 0.0735 |
| 4 | frozen | 250 | duration_complete | 0.0074 | 0.0925 | 2.0000 | 98.0000 | 0.4519 | 0.4321 | 2.0482 | 0.0664 | 0.1506 |
| 5 | moving | 250 | duration_complete | 0.0722 | 0.9023 | 47.2000 | 52.0000 | 3.1920 | 0.3281 | 3.7797 | 0.1208 | 0.1462 |
| 6 | moving | 250 | duration_complete | 0.0641 | 0.8014 | 54.0000 | 46.0000 | 3.1283 | 0.3300 | 3.1303 | 0.0614 | 0.1556 |
| 7 | frozen | 250 | duration_complete | 0.0027 | 0.0340 | 3.2000 | 96.8000 | 0.4247 | 0.4315 | 2.0705 | 0.0541 | 0.1558 |

## Interpretation

- The next student must beat the frozen-seed pattern, not merely reduce fall count.
- If frozen seeds show low action/target velocity and high double support, the next design should add closed-loop selection pressure against quiet double-support dwell.
- No robot validation is implied by this analysis.
