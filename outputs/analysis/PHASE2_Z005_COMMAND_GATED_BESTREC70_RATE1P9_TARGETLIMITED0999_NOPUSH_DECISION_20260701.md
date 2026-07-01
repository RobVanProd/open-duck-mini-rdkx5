# Phase 2 Target-Limited Command-Gated z=0.005 Terrain Decision

status: `HOLD_Z005_TERRAIN_STABILITY`

This is an offline sim/eval result only. No robot test, SSH, deploy, grounded
replay, tuning, training, or runtime behavior change was performed.

## Candidate

- candidate: `outputs/analysis/phase2_z0025_command_gated_bestrec70_rate1p9_targetlimited0999_candidate/candidate.onnx`
- candidate_sha256: `6ba399528c6bc7543e0a5a3a43c30b0804357a4b98e21d723cbb5188e446b2a2`
- prior stronger-push decision: `outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_STRONGER_PUSH_DECISION_20260701.md`

## Gate

- command_x: `0.08`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.005`
- bridge_mode: `fitted`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- duration: `15 s`
- seeds: `0-7`
- push: disabled

Artifact:
`outputs/analysis/PHASE2_Z005_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_NOPUSH_X008.md`

## Result

- status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
- duration_complete: `6/8`
- falls/terminations: `2/8`
- terminating seeds: `1, 5`
- samples_mean: `658.5000`
- samples_min: `57`
- mean_local_vx_mean: `-0.0051 m/s`
- track_ratio_mean: `-0.0634`
- body_pitch_p95_mean: `0.1352 rad`
- base_height_min_mean: `0.1231 m`
- p95 velocity excess mean: `0.0000 rad/s`
- max velocity excess mean: `0.0000 rad/s`
- max_tracking_p95_mean: approximately `0.1924 rad`

Per-seed failures:

| seed | samples | termination | mean_local_vx | track_ratio | base_height_min |
|---:|---:|---|---:|---:|---:|
| 1 | 711 | `fall_or_nan` | `0.0565` | `0.7064` | `0.0045` |
| 5 | 57 | `fall_or_nan` | `-0.2711` | `-3.3886` | `0.0594` |

## Interpretation

The candidate that passes z=0.0025 rough terrain, gentle pushes, and stronger
pushes does not yet generalize to z=0.005 terrain. The hold is not caused by
corrected-envelope excess: both p95 and max velocity excess remain zero.

The next Phase 2 work should target terrain stability at z=0.005, especially
seed-5 early reverse/collapse and seed-1 late base-height collapse, while
preserving the already-passed z=0.0025 stronger-push gates.
