# Phase 2 Intermediate-Push Failure Diagnostic

status: `HOLD_PHASE2_INTERMEDIATE_PUSH_WINDOW_PITCHOVER`

This is an offline trace analysis. It did not train, SSH, deploy, touch
the robot, or modify Playground.

## Executive Summary

- traced seeds: `2`
- pass/control-stable seeds: `0`
- failing/held seeds: `2`
- classification counts: `{'PUSH_WINDOW_PITCHOVER': 2}`
- This report separates corrected actuator-envelope excess from post-push
  delayed pitch/base-height instability and push-window pitch-over.
  Envelope excess is treated as the harder blocker because it violates
  the canonical corrected bridge gate.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_seed0_push_window_recovery_rate150_seed0_7_trace.json`
- fit_json: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- trace_root: `outputs/analysis/phase2_z0075_seed0_push_window_recovery_rate150_seed0_7_trace`
- dt_s: `0.02`

## Per-Seed Timing

| seed | status | samples | pushes | push success | last push tick | pitch>0.8 tick | height<0.08 tick | ticks push-end to pitch>0.8 | ticks push-end to height<0.08 | max excess joint | max excess | classification |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 647 | 10 | 0.9000 | 609 | 637 | 642 | -9 | -4 | `NA` | 0.0000 | `PUSH_WINDOW_PITCHOVER` |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 633 | 8 | 0.8750 | 575 | 624 | 629 | -8 | -3 | `NA` | 0.0000 | `PUSH_WINDOW_PITCHOVER` |

## Failed-Seed Interpretation

### Seed 0

- last push: tick `609`, magnitude `0.1008`, vector `[0.08693043142557144, -0.05110517144203186]`
- last push recovery window ended at tick `646` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `637`
- base height fell below 0.08 m at tick `642`
- final state: pitch `1.2866`, height `-0.0059`, vx `1.4890`, contacts `[0, 1]`

### Seed 7

- last push: tick `575`, magnitude `0.1066`, vector `[-0.05506786331534386, -0.09131201356649399]`
- last push recovery window ended at tick `632` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `624`
- base height fell below 0.08 m at tick `629`
- final state: pitch `1.3423`, height `0.0024`, vx `1.5269`, contacts `[1, 0]`

## Recommendation

Do not treat this intermediate-push candidate as promotable. If a seed
is classified as `ACTUATOR_ENVELOPE_EXCESS`, the next recipe must remove
the corrected-envelope violation rather than only adding stability or
phase timing. If a seed is classified as `POST_PUSH_DELAYED_PITCHOVER`,
the next recipe should add post-push pitch/base-height recovery while
preserving the passing compact behavior. If a seed is classified as
`PUSH_WINDOW_PITCHOVER`, the next recipe should target recovery inside
the active push window. The corrected actuator envelope must remain fixed.
