# Phase 2 Seed Failure Modes

status: `PASS_SEED_FAILURE_MODE_REPORT_READY`

This is an offline seed-distribution analysis. It did not train, SSH,
deploy, touch the robot, or modify Playground.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_iter3_seed0_recovery_rate150_seed0_failure_trace.json`
- trace_root: `outputs/analysis/phase2_z0075_iter3_seed0_recovery_rate150_seed0_failure_trace`
- velocity_excess_tolerance: `0.1`

## Summary

- seeds: `1`
- status_counts: `{'HOLD_CANDIDATE_FALL_OR_TERMINATION': 1}`
- mode_counts: `{'FORWARD_LUNGE_PITCHOVER': 1}`

## Per-Seed Modes

| seed | status | mode | samples | track | final_vx | final_pitch | final_height | p95_excess | max_excess | reasons |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `FORWARD_LUNGE_PITCHOVER` | 126 | 2.0714 | 1.4618 | 1.2752 | 0.0037 | 0.0000 | 0.0000 | `['forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |

## Recommendation

The next recovery dataset should cover each populated failure mode, not only the compact seed0/seed7 pair. If reverse pitch-back and forward lunge both appear, use seed-diverse live-oracle relabels plus pass-control traces; do not add a single scalar damping or progress term and call it distributional.
