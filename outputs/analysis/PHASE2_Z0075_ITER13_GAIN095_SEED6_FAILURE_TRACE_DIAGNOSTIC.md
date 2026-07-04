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

- sweep_json: `outputs/analysis/phase2_z0075_iter13_gain095_seed6_trace.json`
- fit_json: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- trace_root: `outputs/analysis/phase2_z0075_iter13_gain095_seed6_trace`
- dt_s: `0.02`

## Per-Seed Timing

| seed | status | samples | pushes | push success | last push tick | pitch>0.8 tick | height<0.08 tick | ticks push-end to pitch>0.8 | ticks push-end to height<0.08 | max excess joint | max excess | classification |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 749 | 13 | 0.9231 | 727 | 740 | 747 | -8 | -1 | `NA` | 0.0000 | `PUSH_WINDOW_PITCHOVER` |

## Failed-Seed Interpretation

### Seed 6

- last push: tick `727`, magnitude `0.0902`, vector `[0.08445803821086884, 0.031624685972929]`
- last push recovery window ended at tick `748` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `740`
- base height fell below 0.08 m at tick `747`
- final state: pitch `-1.3465`, height `0.0556`, vx `-1.4312`, contacts `[0, 0]`

## Recommendation

Do not treat this intermediate-push candidate as promotable. If a seed
is classified as `ACTUATOR_ENVELOPE_EXCESS`, the next recipe must remove
the corrected-envelope violation rather than only adding stability or
phase timing. If a seed is classified as `POST_PUSH_DELAYED_PITCHOVER`,
the next recipe should add post-push pitch/base-height recovery while
preserving the passing compact behavior. If a seed is classified as
`PUSH_WINDOW_PITCHOVER`, the next recipe should target recovery inside
the active push window. The corrected actuator envelope must remain fixed.
