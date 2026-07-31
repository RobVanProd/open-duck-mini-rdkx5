# Phase 2 Seed Failure Modes

status: `PASS_SEED_FAILURE_MODE_REPORT_READY`

This is an offline seed-distribution analysis. It did not train, SSH,
deploy, touch the robot, or modify Playground.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_late_lunge_rate150_failed_seed_traces.json`
- trace_root: `outputs/analysis/phase2_z0075_late_lunge_rate150_failed_seed_traces`
- velocity_excess_tolerance: `0.1`

## Summary

- seeds: `7`
- status_counts: `{'HOLD_CANDIDATE_FALL_OR_TERMINATION': 6, 'HOLD_CANDIDATE_TARGET_VELOCITY': 1}`
- mode_counts: `{'ACTUATOR_ENVELOPE_EXCESS': 4, 'FORWARD_LUNGE_PITCHOVER': 2, 'PRE_PUSH_REVERSE_PITCHBACK': 1}`

## Per-Seed Modes

| seed | status | mode | samples | track | final_vx | final_pitch | final_height | p95_excess | max_excess | reasons |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `ACTUATOR_ENVELOPE_EXCESS` | 150 | 1.7842 | 1.5137 | 1.4322 | 0.0025 | 0.0000 | 0.1199 | `['actuator_envelope_excess', 'forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `ACTUATOR_ENVELOPE_EXCESS` | 580 | 0.7284 | 1.4942 | 1.3476 | 0.0124 | 0.0000 | 1.0405 | `['actuator_envelope_excess', 'forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `FORWARD_LUNGE_PITCHOVER` | 154 | 1.6349 | 1.4763 | 1.4345 | 0.0185 | 0.0000 | 0.0000 | `['forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |
| 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | `ACTUATOR_ENVELOPE_EXCESS` | 750 | 0.3365 | 0.0813 | 0.1744 | 0.1666 | 0.0000 | 0.2400 | `['actuator_envelope_excess']` |
| 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `FORWARD_LUNGE_PITCHOVER` | 277 | 1.1543 | 1.5300 | 1.3257 | -0.0053 | 0.0000 | 0.0537 | `['forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `PRE_PUSH_REVERSE_PITCHBACK` | 46 | -3.9985 | -1.4860 | -1.4298 | 0.0695 | 0.0000 | 0.0000 | `['reverse_velocity', 'pitch_back', 'low_base_height', 'pre_push_failure']` |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `ACTUATOR_ENVELOPE_EXCESS` | 425 | 0.8839 | 1.5552 | 1.4155 | -0.0021 | 0.0000 | 1.5385 | `['actuator_envelope_excess', 'forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |

## Recommendation

The next recovery dataset should cover each populated failure mode, not only the compact seed0/seed7 pair. If reverse pitch-back and forward lunge both appear, use seed-diverse live-oracle relabels plus pass-control traces; do not add a single scalar damping or progress term and call it distributional.
