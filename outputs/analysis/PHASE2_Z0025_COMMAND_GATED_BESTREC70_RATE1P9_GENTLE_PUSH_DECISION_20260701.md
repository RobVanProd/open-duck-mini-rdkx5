# Phase 2 Command-Gated Candidate Gentle-Push Decision

status: `HOLD_GENTLE_PUSH_INSTANT_TARGET_VELOCITY`

This is an offline sim/eval result only. No robot test, SSH, deploy, grounded
replay, tuning, training, or runtime behavior change was performed.

## Candidate

- candidate: `outputs/analysis/phase2_z0025_command_gated_bestrec70_rate1p9_candidate/candidate.onnx`
- candidate_sha256: `41ec72e7d3ab2b2a351c36de57b38a3c78c273270b6ba10950979df73733fea7`
- prior no-push decision: `outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_DECISION_20260701.md`

## Gate

- command_x: `0.08`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0025`
- bridge_mode: `fitted`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- duration: `15 s`
- seeds: `0-7`
- push interval: `1.0-1.5 s`
- push magnitude: `0.05-0.10`
- push recovery window: `0.5 s`
- pitch recovery bound: `0.8 rad`
- base-height recovery bound: `0.08 m`

Artifact:
`outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_GENTLE_PUSH_X008.md`

## Result

- duration_complete: `8/8`
- falls: `0/8`
- mean_local_vx_mean: `0.0304 m/s`
- track_ratio_mean: `0.3795`
- body_pitch_p95_mean: `0.1208 rad`
- base_height_min_mean: `0.1526 m`
- max_pitch_vel_p95_mean: `1.9156 rad/s`
- p95 velocity excess mean: `0.0000 rad/s`
- max velocity excess mean: `0.0147 rad/s`
- max_tracking_p95_mean: `0.1933 rad`
- push events mean: `12.3750`
- push recovery success mean: `0.9704`

Per-seed status:

| seed | status | max velocity excess | push success |
|---:|---|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | `0.0000` | `0.9167` |
| 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | `0.0119` | `1.0000` |
| 2 | `PASS_CANDIDATE_SIM_GATE` | `0.0000` | `0.9231` |
| 3 | `HOLD_CANDIDATE_TARGET_VELOCITY` | `0.0582` | `1.0000` |
| 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | `0.0063` | `1.0000` |
| 5 | `PASS_CANDIDATE_SIM_GATE` | `0.0000` | `1.0000` |
| 6 | `PASS_CANDIDATE_SIM_GATE` | `0.0000` | `0.9231` |
| 7 | `HOLD_CANDIDATE_TARGET_VELOCITY` | `0.0414` | `1.0000` |

## Interpretation

The command-gated candidate is stable under gentle pushes and recovers most push
events. It does not pass the gentle-push promotion gate because 4/8 seeds show
small instantaneous corrected-envelope target-velocity excess.

This is not a collapse or terrain/standing failure. The next Phase 2 step should
target push-time target-rate margin while preserving:

1. the no-push x=0.0 command semantics pass,
2. the no-push x=0.08 rough-terrain walking pass,
3. the gentle-push stability and recovery behavior.

Do not promote this candidate as push-robust yet.
