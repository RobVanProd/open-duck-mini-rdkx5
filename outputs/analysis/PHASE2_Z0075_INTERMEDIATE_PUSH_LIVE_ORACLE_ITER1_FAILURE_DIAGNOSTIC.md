# Phase 2 Intermediate-Push Failure Diagnostic

status: `HOLD_PHASE2_INTERMEDIATE_PUSH_ACTUATOR_ENVELOPE_EXCESS`

This is an offline trace analysis. It did not train, SSH, deploy, touch
the robot, or modify Playground.

## Executive Summary

- traced seeds: `5`
- pass/control-stable seeds: `0`
- failing/held seeds: `5`
- classification counts: `{'FALL_OR_TERMINATION_UNCLASSIFIED': 1, 'ACTUATOR_ENVELOPE_EXCESS': 4}`
- This report separates corrected actuator-envelope excess from post-push
  delayed pitch/base-height instability. Envelope excess is treated as the
  harder blocker because it violates the canonical corrected bridge gate.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter1_failure_traces.json`
- fit_json: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- trace_root: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter1_failure_traces`
- dt_s: `0.02`

## Per-Seed Timing

| seed | status | samples | pushes | push success | last push tick | pitch>0.8 tick | height<0.08 tick | ticks push-end to pitch>0.8 | ticks push-end to height<0.08 | max excess joint | max excess | classification |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 560 | 10 | 0.8000 | 549 | 550 | 555 | -9 | -4 | `NA` | 0.0000 | `FALL_OR_TERMINATION_UNCLASSIFIED` |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 643 | 11 | 0.9091 | 626 | 634 | 639 | -8 | -3 | `left_knee` | 1.9168 | `ACTUATOR_ENVELOPE_EXCESS` |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 85 | 1 | 0.0000 | 53 | 77 | 84 | -7 | 0 | `right_ankle` | 2.3114 | `ACTUATOR_ENVELOPE_EXCESS` |
| 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 478 | 8 | 0.8750 | 463 | 468 | 473 | -9 | -4 | `right_ankle` | 0.1771 | `ACTUATOR_ENVELOPE_EXCESS` |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 48 | 0 | NA | NA | 40 | NA | NA | NA | `right_ankle` | 3.2400 | `ACTUATOR_ENVELOPE_EXCESS` |

## Failed-Seed Interpretation

### Seed 1

- last push: tick `549`, magnitude `0.0866`, vector `[0.0031624913681298494, 0.08655151724815369]`
- last push recovery window ended at tick `559` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `550`
- base height fell below 0.08 m at tick `555`
- final state: pitch `1.3969`, height `-0.0135`, vx `1.5683`, contacts `[0, 0]`

### Seed 2

- last push: tick `626`, magnitude `0.1238`, vector `[0.10572541505098343, -0.06446702033281326]`
- last push recovery window ended at tick `642` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `634`
- base height fell below 0.08 m at tick `639`
- final state: pitch `1.3396`, height `0.0025`, vx `1.5014`, contacts `[0, 0]`

### Seed 3

- last push: tick `53`, magnitude `0.0869`, vector `[0.08462537080049515, 0.019808964803814888]`
- last push recovery window ended at tick `84` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `77`
- base height fell below 0.08 m at tick `84`
- final state: pitch `-1.3394`, height `0.0708`, vx `-1.4624`, contacts `[0, 0]`

### Seed 4

- last push: tick `463`, magnitude `0.0973`, vector `[-0.022124480456113815, 0.09475628286600113]`
- last push recovery window ended at tick `477` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `468`
- base height fell below 0.08 m at tick `473`
- final state: pitch `1.4115`, height `-0.0115`, vx `1.5909`, contacts `[0, 1]`

### Seed 5

- last push: tick `NA`, magnitude `NA`, vector `None`
- last push recovery window ended at tick `NA` and was marked recovered: `None`
- pitch exceeded 0.8 rad at tick `40`
- base height fell below 0.08 m at tick `NA`
- final state: pitch `-1.5409`, height `0.0875`, vx `-1.4290`, contacts `[0, 0]`

## Recommendation

Do not treat this intermediate-push candidate as promotable. If a seed
is classified as `ACTUATOR_ENVELOPE_EXCESS`, the next recipe must remove
the corrected-envelope violation rather than only adding stability or
phase timing. If a seed is classified as `POST_PUSH_DELAYED_PITCHOVER`,
the next recipe should add post-push pitch/base-height recovery while
preserving the passing compact behavior. The corrected actuator envelope
must remain fixed.
