# Phase 2 Intermediate-Push Failure Diagnostic

status: `HOLD_PHASE2_INTERMEDIATE_PUSH_ACTUATOR_ENVELOPE_EXCESS`

This is an offline trace analysis. It did not train, SSH, deploy, touch
the robot, or modify Playground.

## Executive Summary

- traced seeds: `3`
- pass/control-stable seeds: `0`
- failing/held seeds: `3`
- classification counts: `{'ACTUATOR_ENVELOPE_EXCESS': 2, 'PUSH_WINDOW_PITCHOVER': 1}`
- This report separates corrected actuator-envelope excess from post-push
  delayed pitch/base-height instability and push-window pitch-over.
  Envelope excess is treated as the harder blocker because it violates
  the canonical corrected bridge gate.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_iter21_resetsettle10_failure_traces.json`
- fit_json: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- trace_root: `outputs/analysis/phase2_z0075_iter21_resetsettle10_failure_traces`
- dt_s: `0.02`

## Per-Seed Timing

| seed | status | samples | pushes | push success | last push tick | pitch>0.8 tick | height<0.08 tick | ticks push-end to pitch>0.8 | ticks push-end to height<0.08 | max excess joint | max excess | classification |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 13 | 0.9231 | 714 | NA | NA | NA | NA | `right_ankle` | 0.0583 | `ACTUATOR_ENVELOPE_EXCESS` |
| 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 13 | 0.9231 | 701 | NA | NA | NA | NA | `right_ankle` | 0.0097 | `ACTUATOR_ENVELOPE_EXCESS` |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 599 | 10 | 0.9000 | 549 | 590 | 598 | -8 | 0 | `NA` | 0.0000 | `PUSH_WINDOW_PITCHOVER` |

## Failed-Seed Interpretation

### Seed 1

- last push: tick `714`, magnitude `0.1235`, vector `[0.11822100728750229, 0.03568168729543686]`
- last push recovery window ended at tick `749` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `NA`
- base height fell below 0.08 m at tick `NA`
- final state: pitch `0.2848`, height `0.1584`, vx `0.0280`, contacts `[1, 1]`

### Seed 3

- last push: tick `701`, magnitude `0.1245`, vector `[-0.06421075761318207, -0.10661925375461578]`
- last push recovery window ended at tick `749` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `NA`
- base height fell below 0.08 m at tick `NA`
- final state: pitch `0.1040`, height `0.1702`, vx `0.0833`, contacts `[1, 1]`

### Seed 5

- last push: tick `549`, magnitude `0.0884`, vector `[0.08817565441131592, 0.005833707749843597]`
- last push recovery window ended at tick `598` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `590`
- base height fell below 0.08 m at tick `598`
- final state: pitch `-1.4099`, height `0.0630`, vx `-1.5263`, contacts `[0, 0]`

## Recommendation

Do not treat this intermediate-push candidate as promotable. If a seed
is classified as `ACTUATOR_ENVELOPE_EXCESS`, the next recipe must remove
the corrected-envelope violation rather than only adding stability or
phase timing. If a seed is classified as `POST_PUSH_DELAYED_PITCHOVER`,
the next recipe should add post-push pitch/base-height recovery while
preserving the passing compact behavior. If a seed is classified as
`PUSH_WINDOW_PITCHOVER`, the next recipe should target recovery inside
the active push window. The corrected actuator envelope must remain fixed.
