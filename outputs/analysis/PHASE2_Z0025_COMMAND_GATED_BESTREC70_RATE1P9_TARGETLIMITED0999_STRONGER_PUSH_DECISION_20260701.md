# Phase 2 Target-Limited Command-Gated Stronger-Push Decision

status: `PASS_STRONGER_PUSH_Z0025_GATE`

This is an offline sim/eval result only. No robot test, SSH, deploy, grounded
replay, tuning, training, or runtime behavior change was performed.

## Candidate

- candidate: `outputs/analysis/phase2_z0025_command_gated_bestrec70_rate1p9_targetlimited0999_candidate/candidate.onnx`
- candidate_sha256: `6ba399528c6bc7543e0a5a3a43c30b0804357a4b98e21d723cbb5188e446b2a2`
- prior gentle-push decision: `outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_GENTLE_PUSH_DECISION_20260701.md`

## Gate

- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0025`
- bridge_mode: `fitted`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- duration: `15 s`
- seeds: `0-7`
- push interval: `1.0-1.5 s`
- push magnitude: `0.10-0.20`
- push recovery window: `0.5 s`

## Full Gate: x=0.08 Stronger Push

Artifact:
`outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_STRONGER_PUSH_X008.md`

- command_x: `0.08`
- status: `PASS_CANDIDATE_SIM_GATE` on `8/8`
- falls: `0/8`
- duration_complete: `8/8`
- mean_local_vx_mean: `0.0306 m/s`
- track_ratio_mean: `0.3821`
- body_pitch_p95_mean: `0.1379 rad`
- base_height_min_mean: `0.1526 m`
- max_pitch_vel_p95_mean: `1.9132 rad/s`
- p95 velocity excess mean: `0.0000 rad/s`
- max velocity excess mean: `0.0000 rad/s`
- max_tracking_p95_mean: `0.1939 rad`
- push events mean: `12.3750`
- push recovery success mean: `0.9704`

## Full Gate: x=0.0 Stronger Push

Artifact:
`outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_STRONGER_PUSH_X0.md`

- command_x: `0.0`
- status: `PASS_CANDIDATE_SIM_GATE` on `8/8`
- falls: `0/8`
- duration_complete: `8/8`
- mean_local_vx_mean: `-0.0004 m/s`
- body_pitch_p95_mean: `0.0423 rad`
- base_height_min_mean: `0.1526 m`
- max_pitch_vel_p95_mean: `2.7605 rad/s`
- p95 velocity excess mean: `0.0000 rad/s`
- max velocity excess mean: `0.0000 rad/s`
- max_tracking_p95_mean: `0.1940 rad`
- push events mean: `12.3750`
- push recovery success mean: `0.9704`

## Interpretation

The target-limited command-gated candidate clears the stronger-push stage at
both x=0.08 and x=0.0 on rough z=0.0025 terrain. It preserves corrected-envelope
compliance, standing command semantics, slow forward walking, and push recovery.

This does not authorize robot validation. The next Phase 2 offline curriculum
step should increase terrain difficulty or broaden dynamics randomization while
keeping the same corrected bridge gate.
