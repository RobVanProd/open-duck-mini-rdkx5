# Phase 2 Seed Failure Modes

status: `PASS_SEED_FAILURE_MODE_REPORT_READY`

This is an offline seed-distribution analysis. It did not train, SSH,
deploy, touch the robot, or modify Playground.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_seed_diverse_recovery_rate150_failed_seed_traces.json`
- trace_root: `outputs/analysis/phase2_z0075_seed_diverse_recovery_rate150_failed_seed_traces`
- velocity_excess_tolerance: `0.1`

## Summary

- seeds: `7`
- status_counts: `{'HOLD_CANDIDATE_FALL_OR_TERMINATION': 7}`
- mode_counts: `{'ACTUATOR_ENVELOPE_EXCESS': 1, 'FORWARD_LUNGE_PITCHOVER': 5, 'PRE_PUSH_REVERSE_PITCHBACK': 1}`

## Per-Seed Modes

| seed | status | mode | samples | track | final_vx | final_pitch | final_height | p95_excess | max_excess | reasons |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `FORWARD_LUNGE_PITCHOVER` | 513 | 0.8139 | 1.4757 | 1.3128 | 0.0098 | 0.0000 | 0.0000 | `['forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `FORWARD_LUNGE_PITCHOVER` | 155 | 1.7105 | 1.5272 | 1.3542 | 0.0018 | 0.0000 | 0.0000 | `['forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `ACTUATOR_ENVELOPE_EXCESS` | 129 | -1.8271 | -1.3902 | -1.3592 | 0.0696 | 0.0000 | 0.2339 | `['actuator_envelope_excess', 'reverse_velocity', 'pitch_back', 'low_base_height']` |
| 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `FORWARD_LUNGE_PITCHOVER` | 422 | 0.7771 | 1.4935 | 1.4577 | 0.0126 | 0.0000 | 0.0000 | `['forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `PRE_PUSH_REVERSE_PITCHBACK` | 47 | -4.0006 | -1.5317 | -1.4068 | 0.0633 | 0.0000 | 0.0000 | `['reverse_velocity', 'pitch_back', 'low_base_height', 'pre_push_failure']` |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `FORWARD_LUNGE_PITCHOVER` | 430 | 0.8593 | 1.4963 | 1.3391 | -0.0028 | 0.0000 | 0.0000 | `['forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `FORWARD_LUNGE_PITCHOVER` | 617 | 0.6758 | 1.5000 | 1.4660 | 0.0067 | 0.0000 | 0.0000 | `['forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |

## Recommendation

The next recovery dataset should cover each populated failure mode, not only the compact seed0/seed7 pair. If reverse pitch-back and forward lunge both appear, use seed-diverse live-oracle relabels plus pass-control traces; do not add a single scalar damping or progress term and call it distributional.
