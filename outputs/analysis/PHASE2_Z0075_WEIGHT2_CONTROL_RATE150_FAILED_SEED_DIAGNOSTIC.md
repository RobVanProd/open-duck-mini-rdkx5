# Phase 2 Intermediate-Push Failure Diagnostic

status: `HOLD_PHASE2_INTERMEDIATE_PUSH_ACTUATOR_ENVELOPE_EXCESS`

This is an offline trace analysis. It did not train, SSH, deploy, touch
the robot, or modify Playground.

## Executive Summary

- traced seeds: `6`
- pass/control-stable seeds: `0`
- failing/held seeds: `6`
- classification counts: `{'PUSH_WINDOW_PITCHOVER': 4, 'ACTUATOR_ENVELOPE_EXCESS': 1, 'FALL_OR_TERMINATION_UNCLASSIFIED': 1}`
- This report separates corrected actuator-envelope excess from post-push
  delayed pitch/base-height instability and push-window pitch-over.
  Envelope excess is treated as the harder blocker because it violates
  the canonical corrected bridge gate.

## Inputs

- sweep_json: `outputs/analysis/phase2_z0075_weight2_control_rate150_failed_seed_traces.json`
- fit_json: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- trace_root: `outputs/analysis/phase2_z0075_weight2_control_rate150_failed_seed_traces`
- dt_s: `0.02`

## Per-Seed Timing

| seed | status | samples | pushes | push success | last push tick | pitch>0.8 tick | height<0.08 tick | ticks push-end to pitch>0.8 | ticks push-end to height<0.08 | max excess joint | max excess | classification |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 494 | 8 | 0.8750 | 439 | 486 | NA | -7 | NA | `NA` | 0.0000 | `PUSH_WINDOW_PITCHOVER` |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 157 | 2 | 0.5000 | 113 | 148 | 152 | -8 | -4 | `NA` | 0.0000 | `PUSH_WINDOW_PITCHOVER` |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 450 | 8 | 0.8750 | 431 | 442 | 449 | -7 | 0 | `right_ankle` | 0.3926 | `ACTUATOR_ENVELOPE_EXCESS` |
| 4 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 724 | 12 | 0.9167 | 695 | 715 | 720 | -8 | -3 | `NA` | 0.0000 | `PUSH_WINDOW_PITCHOVER` |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 47 | 0 | NA | NA | 38 | 46 | NA | NA | `NA` | 0.0000 | `FALL_OR_TERMINATION_UNCLASSIFIED` |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 246 | 4 | 0.7500 | 223 | 237 | 245 | -8 | 0 | `NA` | 0.0000 | `PUSH_WINDOW_PITCHOVER` |

## Failed-Seed Interpretation

### Seed 1

- last push: tick `439`, magnitude `0.0976`, vector `[0.08837219327688217, 0.04152502119541168]`
- last push recovery window ended at tick `493` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `486`
- base height fell below 0.08 m at tick `NA`
- final state: pitch `-1.4101`, height `0.0851`, vx `-1.3897`, contacts `[0, 0]`

### Seed 2

- last push: tick `113`, magnitude `0.1139`, vector `[-0.10984829813241959, -0.03023681789636612]`
- last push recovery window ended at tick `156` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `148`
- base height fell below 0.08 m at tick `152`
- final state: pitch `1.2756`, height `0.0005`, vx `1.5026`, contacts `[0, 0]`

### Seed 3

- last push: tick `431`, magnitude `0.1068`, vector `[-0.03491779416799545, -0.1008792370557785]`
- last push recovery window ended at tick `449` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `442`
- base height fell below 0.08 m at tick `449`
- final state: pitch `-1.4724`, height `0.0776`, vx `-1.4748`, contacts `[0, 0]`

### Seed 4

- last push: tick `695`, magnitude `0.1235`, vector `[-0.01862301491200924, 0.1220477819442749]`
- last push recovery window ended at tick `723` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `715`
- base height fell below 0.08 m at tick `720`
- final state: pitch `1.4869`, height `0.0018`, vx `1.5183`, contacts `[1, 1]`

### Seed 5

- last push: tick `NA`, magnitude `NA`, vector `None`
- last push recovery window ended at tick `NA` and was marked recovered: `None`
- pitch exceeded 0.8 rad at tick `38`
- base height fell below 0.08 m at tick `46`
- final state: pitch `-1.4327`, height `0.0706`, vx `-1.4345`, contacts `[0, 0]`

### Seed 6

- last push: tick `223`, magnitude `0.1038`, vector `[-0.011790018528699875, -0.10317188501358032]`
- last push recovery window ended at tick `245` and was marked recovered: `False`
- pitch exceeded 0.8 rad at tick `237`
- base height fell below 0.08 m at tick `245`
- final state: pitch `-1.4542`, height `0.0687`, vx `-1.5359`, contacts `[1, 0]`

## Recommendation

Do not treat this intermediate-push candidate as promotable. If a seed
is classified as `ACTUATOR_ENVELOPE_EXCESS`, the next recipe must remove
the corrected-envelope violation rather than only adding stability or
phase timing. If a seed is classified as `POST_PUSH_DELAYED_PITCHOVER`,
the next recipe should add post-push pitch/base-height recovery while
preserving the passing compact behavior. If a seed is classified as
`PUSH_WINDOW_PITCHOVER`, the next recipe should target recovery inside
the active push window. The corrected actuator envelope must remain fixed.
