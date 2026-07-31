# Phase 2 Intermediate-Push Failure Diagnostic

status: `HOLD_PHASE2_INTERMEDIATE_PUSH_WINDOW_PITCHOVER`

This is an offline trace analysis. It did not train, SSH, deploy, touch
the robot, or modify Playground.

## Executive Summary

- traced seeds: `3`
- pass/control-stable seeds: `0`
- failing/held seeds: `3`
- classification counts: `{'PUSH_WINDOW_PITCHOVER': 3}`
- This report separates corrected actuator-envelope excess from post-push
  delayed pitch/base-height instability and push-window pitch-over.
  Envelope excess is treated as the harder blocker because it violates
  the canonical corrected bridge gate.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_home_support_push_failure_trace_seeds_0_2_6.json`
- fit_json: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- trace_root: `outputs/analysis/phase2_z0075_home_support_push_failure_trace_seeds_0_2_6`
- dt_s: `0.02`

## Per-Seed Timing

| seed | status | samples | pushes | push success | last push tick | pitch>0.8 tick | height<0.08 tick | ticks push-end to pitch>0.8 | ticks push-end to height<0.08 | max excess joint | max excess | classification |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 114 | 1 | 0.0000 | 60 | 105 | 110 | -8 | -3 | `NA` | 0.0000 | `PUSH_WINDOW_PITCHOVER` |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 604 | 10 | 0.9000 | 569 | 596 | NA | -7 | NA | `NA` | 0.0000 | `PUSH_WINDOW_PITCHOVER` |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 672 | 12 | 0.8333 | 671 | 663 | 671 | -8 | 0 | `NA` | 0.0000 | `PUSH_WINDOW_PITCHOVER` |

## Failed-Seed Interpretation

### Seed 0

- last push: tick `60`, magnitude `0.0798`, vector `[0.07972996681928635, 0.002081675222143531]`
- last push recovery window ended at tick `113` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `105`
- base height fell below 0.08 m at tick `110`
- final state: pitch `1.3779`, height `0.0059`, vx `1.5128`, contacts `[1, 0]`

### Seed 2

- last push: tick `569`, magnitude `0.1063`, vector `[0.10541938245296478, -0.013388034887611866]`
- last push recovery window ended at tick `603` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `596`
- base height fell below 0.08 m at tick `NA`
- final state: pitch `-1.4035`, height `0.0821`, vx `-1.3854`, contacts `[0, 0]`

### Seed 6

- last push: tick `671`, magnitude `0.1065`, vector `[0.04916354641318321, -0.09450727701187134]`
- last push recovery window ended at tick `671` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `663`
- base height fell below 0.08 m at tick `671`
- final state: pitch `-1.3916`, height `0.0755`, vx `-1.3718`, contacts `[0, 0]`

## Recommendation

Do not treat this intermediate-push candidate as promotable. If a seed
is classified as `ACTUATOR_ENVELOPE_EXCESS`, the next recipe must remove
the corrected-envelope violation rather than only adding stability or
phase timing. If a seed is classified as `POST_PUSH_DELAYED_PITCHOVER`,
the next recipe should add post-push pitch/base-height recovery while
preserving the passing compact behavior. If a seed is classified as
`PUSH_WINDOW_PITCHOVER`, the next recipe should target recovery inside
the active push window. The corrected actuator envelope must remain fixed.
