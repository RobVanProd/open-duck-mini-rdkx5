# BC Replay Seed Mode Analysis

status: `PASS_NO_FREEZE_SEEDS`

This is an offline analysis of ignored BC replay traces. It does not run
simulation, training, deployment, SSH, or robot tests.

## Summary

- trace_glob: `outputs/analysis/closed_loop_teacher_dataset_source_vx_blend080_100_srcvx002_alt_exclude_seed4_bc_gate_x008_traces/*.jsonl`
- command_x: `0.0800`
- moving_threshold_m_s: `0.0200`
- moving_seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`
- frozen_seeds: `[]`

| group | count | mean_vx | ratio | single_% | double_% | pitch_vel95 | early_action_abs | early_pitch_vel95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| moving | 8 | 0.0699 | 0.8732 | 51.7500 | 48.0500 | 3.1715 | 0.3268 | 3.3894 |
| frozen | 0 | NA | NA | NA | NA | NA | NA | NA |

## Per Seed

| seed | mode | samples | termination | vx | ratio | single_% | double_% | pitch_vel95 | early_action_abs | early_pitch_vel95 | pitch95 | height_min |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | moving | 250 | duration_complete | 0.0723 | 0.9042 | 51.6000 | 48.4000 | 3.1816 | 0.3269 | 3.3094 | 0.0575 | 0.1520 |
| 1 | moving | 250 | duration_complete | 0.0732 | 0.9150 | 55.2000 | 44.4000 | 3.1607 | 0.3304 | 3.2543 | 0.0625 | 0.1559 |
| 2 | moving | 250 | duration_complete | 0.0737 | 0.9212 | 52.8000 | 47.2000 | 3.1195 | 0.3254 | 3.1070 | 0.0623 | 0.1511 |
| 3 | moving | 250 | duration_complete | 0.0499 | 0.6242 | 46.4000 | 53.2000 | 3.1982 | 0.3255 | 3.1180 | 0.1362 | 0.1535 |
| 4 | moving | 250 | duration_complete | 0.0765 | 0.9565 | 49.6000 | 50.4000 | 3.2094 | 0.3256 | 4.3683 | 0.0636 | 0.1506 |
| 5 | moving | 250 | duration_complete | 0.0726 | 0.9074 | 48.8000 | 50.4000 | 3.1852 | 0.3299 | 3.4058 | 0.1259 | 0.1462 |
| 6 | moving | 250 | duration_complete | 0.0680 | 0.8503 | 56.0000 | 44.0000 | 3.1380 | 0.3223 | 3.1742 | 0.0607 | 0.1556 |
| 7 | moving | 250 | duration_complete | 0.0726 | 0.9071 | 53.6000 | 46.4000 | 3.1797 | 0.3280 | 3.3785 | 0.0584 | 0.1558 |

## Interpretation

- The next student must beat the frozen-seed pattern, not merely reduce fall count.
- If frozen seeds show low action/target velocity and high double support, the next design should add closed-loop selection pressure against quiet double-support dwell.
- No robot validation is implied by this analysis.
