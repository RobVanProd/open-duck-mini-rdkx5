# Phase 2 Seed Failure Modes

status: `PASS_SEED_FAILURE_MODE_REPORT_READY`

This is an offline seed-distribution analysis. It did not train, SSH,
deploy, touch the robot, or modify Playground.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_spike_local_rate150_failed_seed_traces.json`
- trace_root: `outputs/analysis/phase2_z0075_spike_local_rate150_failed_seed_traces`
- velocity_excess_tolerance: `0.1`

## Summary

- seeds: `5`
- status_counts: `{'HOLD_CANDIDATE_FALL_OR_TERMINATION': 5}`
- mode_counts: `{'ACTUATOR_ENVELOPE_EXCESS': 2, 'FORWARD_LUNGE_PITCHOVER': 1, 'PRE_PUSH_REVERSE_PITCHBACK': 1, 'REVERSE_PITCHBACK': 1}`

## Per-Seed Modes

| seed | status | mode | samples | track | final_vx | final_pitch | final_height | p95_excess | max_excess | reasons |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `REVERSE_PITCHBACK` | 419 | -0.1401 | -1.4402 | -1.4680 | 0.0836 | 0.0000 | 0.0000 | `['reverse_velocity', 'pitch_back']` |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `ACTUATOR_ENVELOPE_EXCESS` | 714 | 0.6560 | 1.4213 | 1.2895 | 0.0104 | 0.0000 | 0.2900 | `['actuator_envelope_excess', 'forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `FORWARD_LUNGE_PITCHOVER` | 527 | 0.6962 | 1.5117 | 1.4677 | 0.0040 | 0.0000 | 0.0000 | `['forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `PRE_PUSH_REVERSE_PITCHBACK` | 45 | -3.7453 | -1.4291 | -1.4972 | 0.0888 | 0.0000 | 0.0000 | `['reverse_velocity', 'pitch_back', 'pre_push_failure']` |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | `ACTUATOR_ENVELOPE_EXCESS` | 611 | 0.6569 | 1.4558 | 1.2616 | 0.0031 | 0.0000 | 0.1897 | `['actuator_envelope_excess', 'forward_lunge_velocity', 'pitch_forward', 'low_base_height']` |

## Recommendation

The next recovery dataset should cover each populated failure mode, not only the compact seed0/seed7 pair. If reverse pitch-back and forward lunge both appear, use seed-diverse live-oracle relabels plus pass-control traces; do not add a single scalar damping or progress term and call it distributional.
