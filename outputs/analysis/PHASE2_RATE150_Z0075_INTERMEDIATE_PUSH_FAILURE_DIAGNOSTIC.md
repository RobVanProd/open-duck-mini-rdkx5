# Phase 2 Intermediate-Push Failure Diagnostic

status: `HOLD_PHASE2_INTERMEDIATE_PUSH_POST_RECOVERY_PITCHOVER`

This is an offline trace analysis. It did not train, SSH, deploy, touch
the robot, or modify Playground.

## Executive Summary

- The intermediate-push hold is reproduced in traced seeds 0 and 7.
- Both failing seeds are marked recovered inside every 0.5 s push window.
- Collapse happens after the last push recovery window, as a delayed pitch-over.
- Seed 1 is a passing control under the same push/terrain settings.
- The next offline refinement should target post-push pitch/base-height stability,
  especially for seeds 0 and 7, without loosening the corrected actuator envelope.

## Inputs

- sweep_json: `outputs/analysis/phase2_rate150_z0075_intermediate_push_trace_seeds_0_1_7.json`
- fit_json: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- trace_root: `outputs/analysis/phase2_rate150_z0075_intermediate_push_trace_seeds_0_1_7`
- dt_s: `0.02`

## Per-Seed Timing

| seed | status | samples | pushes | push success | last push tick | pitch>0.8 tick | height<0.08 tick | ticks push-end to pitch>0.8 | ticks push-end to height<0.08 | max excess joint | max excess | classification |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 181 | 2 | 1.0000 | 121 | 172 | 177 | 26 | 31 | `right_hip_pitch` | 1.3268 | `POST_PUSH_DELAYED_PITCHOVER` |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 13 | 1.0000 | 714 | NA | NA | NA | NA | `NA` | 0.0000 | `PASS_CONTROL_STABLE` |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 550 | 7 | 1.0000 | 503 | 542 | 546 | 14 | 18 | `right_hip_pitch` | 0.4477 | `POST_PUSH_DELAYED_PITCHOVER` |

## Failed-Seed Interpretation

### Seed 0

- last push: tick `121`, magnitude `0.1203`, vector `[-0.029865946620702744, 0.11649270355701447]`
- last push recovery window ended at tick `146` and was marked recovered: `True`
- pitch exceeded 0.8 rad at tick `172`
- base height fell below 0.08 m at tick `177`
- final state: pitch `1.4907`, height `0.0094`, vx `1.5032`, contacts `[1, 1]`

### Seed 7

- last push: tick `503`, magnitude `0.1030`, vector `[0.07678105682134628, 0.06872115284204483]`
- last push recovery window ended at tick `528` and was marked recovered: `True`
- pitch exceeded 0.8 rad at tick `542`
- base height fell below 0.08 m at tick `546`
- final state: pitch `1.5294`, height `0.0201`, vx `1.4294`, contacts `[0, 0]`

## Recommendation

Do not treat the intermediate-push bracket as promotable. It is a
near-boundary stability hold: push windows themselves pass the short
recovery check, but failing seeds pitch over shortly after the final
recovery window. The next offline recipe should preserve the passing
gentle-push behavior while adding post-push pitch/base-height damping
or recovery data for seeds 0 and 7. The corrected actuator envelope
must remain fixed.
