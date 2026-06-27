# BC Replay Seed Mode Analysis

status: `HOLD_FREEZE_LOW_ACTION_DOUBLE_SUPPORT`

This is an offline analysis of ignored BC replay traces. It does not run
simulation, training, deployment, SSH, or robot tests.

## Summary

- trace_glob: `outputs/analysis/closed_loop_teacher_dataset_vx_blend080_100_vxneg002_bc_gate_x008_traces/*.jsonl`
- command_x: `0.0800`
- moving_threshold_m_s: `0.0200`
- moving_seeds: `[0, 1, 2, 3, 5, 6]`
- frozen_seeds: `[4, 7]`

| group | count | mean_vx | ratio | single_% | double_% | pitch_vel95 | early_action_abs | early_pitch_vel95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| moving | 6 | 0.0672 | 0.8403 | 51.0000 | 48.7333 | 3.1652 | 0.3262 | 3.3105 |
| frozen | 2 | 0.0050 | 0.0629 | 2.4000 | 97.6000 | 0.4838 | 0.4319 | 2.2404 |

## Per Seed

| seed | mode | samples | termination | vx | ratio | single_% | double_% | pitch_vel95 | early_action_abs | early_pitch_vel95 | pitch95 | height_min |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | moving | 250 | duration_complete | 0.0700 | 0.8753 | 51.2000 | 48.8000 | 3.1765 | 0.3266 | 3.3428 | 0.0595 | 0.1519 |
| 1 | moving | 250 | duration_complete | 0.0697 | 0.8709 | 53.6000 | 46.0000 | 3.1797 | 0.3330 | 3.1940 | 0.0603 | 0.1559 |
| 2 | moving | 250 | duration_complete | 0.0729 | 0.9109 | 52.0000 | 48.0000 | 3.1069 | 0.3250 | 3.1081 | 0.0590 | 0.1511 |
| 3 | moving | 250 | duration_complete | 0.0501 | 0.6267 | 48.0000 | 51.6000 | 3.1292 | 0.3247 | 2.9565 | 0.1352 | 0.1535 |
| 4 | frozen | 250 | duration_complete | 0.0074 | 0.0925 | 2.0000 | 98.0000 | 0.4519 | 0.4317 | 2.0482 | 0.0667 | 0.1506 |
| 5 | moving | 250 | duration_complete | 0.0725 | 0.9059 | 47.2000 | 52.0000 | 3.2010 | 0.3262 | 4.0310 | 0.1226 | 0.1462 |
| 6 | moving | 250 | duration_complete | 0.0682 | 0.8520 | 54.0000 | 46.0000 | 3.1978 | 0.3213 | 3.2305 | 0.0557 | 0.1556 |
| 7 | frozen | 250 | duration_complete | 0.0027 | 0.0333 | 2.8000 | 97.2000 | 0.5156 | 0.4321 | 2.4326 | 0.0411 | 0.1558 |

## Interpretation

- The next student must beat the frozen-seed pattern, not merely reduce fall count.
- If frozen seeds show low action/target velocity and high double support, the next design should add closed-loop selection pressure against quiet double-support dwell.
- No robot validation is implied by this analysis.
