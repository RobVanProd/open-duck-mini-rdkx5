# Phase 2 Intermediate-Push Failure Diagnostic

status: `HOLD_PHASE2_INTERMEDIATE_PUSH_WINDOW_PITCHOVER`

This is an offline trace analysis. It did not train, SSH, deploy, touch
the robot, or modify Playground.

## Executive Summary

- traced seeds: `1`
- pass/control-stable seeds: `0`
- failing/held seeds: `1`
- classification counts: `{'PUSH_WINDOW_PITCHOVER': 1}`
- This report separates corrected actuator-envelope excess from post-push
  delayed pitch/base-height instability and push-window pitch-over.
  Envelope excess is treated as the harder blocker because it violates
  the canonical corrected bridge gate.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_control_preserving_recovery_rate150_seed0_trace.json`
- fit_json: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- trace_root: `outputs/analysis/phase2_z0075_control_preserving_recovery_rate150_seed0_trace`
- dt_s: `0.02`

## Per-Seed Timing

| seed | status | samples | pushes | push success | last push tick | pitch>0.8 tick | height<0.08 tick | ticks push-end to pitch>0.8 | ticks push-end to height<0.08 | max excess joint | max excess | classification |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 142 | 2 | 0.5000 | 121 | 132 | 138 | -9 | -3 | `NA` | 0.0000 | `PUSH_WINDOW_PITCHOVER` |

## Failed-Seed Interpretation

### Seed 0

- last push: tick `121`, magnitude `0.0966`, vector `[-0.018855614587664604, 0.09474198520183563]`
- last push recovery window ended at tick `141` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `132`
- base height fell below 0.08 m at tick `138`
- final state: pitch `1.2816`, height `-0.0004`, vx `1.4909`, contacts `[0, 0]`

## Recommendation

Do not treat this intermediate-push candidate as promotable. If a seed
is classified as `ACTUATOR_ENVELOPE_EXCESS`, the next recipe must remove
the corrected-envelope violation rather than only adding stability or
phase timing. If a seed is classified as `POST_PUSH_DELAYED_PITCHOVER`,
the next recipe should add post-push pitch/base-height recovery while
preserving the passing compact behavior. If a seed is classified as
`PUSH_WINDOW_PITCHOVER`, the next recipe should target recovery inside
the active push window. The corrected actuator envelope must remain fixed.
