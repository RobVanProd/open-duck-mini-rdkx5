# Phase 2 Seed Failure Modes

status: `PASS_SEED_FAILURE_MODE_REPORT_READY`

This is an offline seed-distribution analysis. It did not train, SSH,
deploy, touch the robot, or modify Playground.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_weight2_control_rate150_failed_seed_traces.json`
- trace_root: `outputs/analysis/phase2_z0075_weight2_control_rate150_failed_seed_traces`
- velocity_excess_tolerance: `0.1`

## Summary

- seeds: `6`
- status_counts: `{'HOLD_CANDIDATE_FALL_OR_TERMINATION': 6}`
- mode_counts: `{'ACTUATOR_ENVELOPE_EXCESS': 1, 'FORWARD_LUNGE_PITCHOVER': 2, 'PRE_PUSH_REVERSE_PITCHBACK': 1, 'REVERSE_PITCHBACK': 2}`

## Per-Seed Modes

| seed | status | mode | samples | track | final_vx | final_pitch | final_height | p95_excess | max_excess | reasons |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `REVERSE_PITCHBACK` | 494 | -0.1076 | -1.3897 | -1.4101 | 0.0851 | 0.0000 | 0.0000 | `['reverse_velocity', 'pitch_back']` |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `FORWARD_LUNGE_PITCHOVER` | 157 | 1.6957 | 1.5026 | 1.2756 | 0.0005 | 0.0000 | 0.0000 | `['forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `ACTUATOR_ENVELOPE_EXCESS` | 450 | -0.2733 | -1.4748 | -1.4724 | 0.0776 | 0.0000 | 0.3926 | `['actuator_envelope_excess', 'reverse_velocity', 'pitch_back', 'low_base_height']` |
| 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `FORWARD_LUNGE_PITCHOVER` | 724 | 0.6728 | 1.5183 | 1.4869 | 0.0018 | 0.0000 | 0.0000 | `['forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `PRE_PUSH_REVERSE_PITCHBACK` | 47 | -3.8964 | -1.4345 | -1.4327 | 0.0706 | 0.0000 | 0.0000 | `['reverse_velocity', 'pitch_back', 'low_base_height', 'pre_push_failure']` |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `REVERSE_PITCHBACK` | 246 | -0.6486 | -1.5359 | -1.4542 | 0.0687 | 0.0000 | 0.0000 | `['reverse_velocity', 'pitch_back', 'low_base_height']` |

## Recommendation

The next recovery dataset should cover each populated failure mode, not only the compact seed0/seed7 pair. If reverse pitch-back and forward lunge both appear, use seed-diverse live-oracle relabels plus pass-control traces; do not add a single scalar damping or progress term and call it distributional.
