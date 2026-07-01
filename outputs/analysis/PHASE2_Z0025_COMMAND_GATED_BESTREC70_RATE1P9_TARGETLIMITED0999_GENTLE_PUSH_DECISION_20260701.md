# Phase 2 Target-Limited Command-Gated Gentle-Push Decision

status: `PASS_GENTLE_PUSH_Z0025_GATE`

This is an offline sim/eval result only. No robot test, SSH, deploy, grounded
replay, tuning, training, or runtime behavior change was performed.

## Candidate

- candidate: `outputs/analysis/phase2_z0025_command_gated_bestrec70_rate1p9_targetlimited0999_candidate/candidate.onnx`
- candidate_sha256: `6ba399528c6bc7543e0a5a3a43c30b0804357a4b98e21d723cbb5188e446b2a2`
- parent candidate: `outputs/analysis/phase2_z0025_command_gated_bestrec70_rate1p9_candidate/candidate.onnx`
- parent_sha256: `41ec72e7d3ab2b2a351c36de57b38a3c78c273270b6ba10950979df73733fea7`
- wrapper: `tools/wrap_policy_command_scale.py`
- action scale: `1.0` at x=0.0 and x=0.08
- target limiter: `0.999 * corrected per-joint target-rate envelope`

The parent command-gated candidate passed the no-push rough-terrain z=0.0025
boundary gate at x=0.0 and x=0.08, but held the x=0.08 gentle-push gate on
small instantaneous target-velocity excess in 4/8 seeds. This candidate adds a
deployable ONNX target-delta limiter without changing the action gain.

## Held-Seed Screen

Artifact:
`outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_GENTLE_PUSH_HOLDSEED_SCREEN_X008.md`

Screened prior held seeds `1, 3, 4, 7` at x=0.08, rough z=0.0025, fitted
corrected bridge, gentle pushes.

- status: `PASS_CANDIDATE_SIM_GATE` on `4/4`
- falls: `0/4`
- duration_complete: `4/4`
- p95 velocity excess mean: `0.0000 rad/s`
- max velocity excess mean: `0.0000 rad/s`
- push recovery success mean: `1.0000`

## Full Gate: x=0.08 Gentle Push

Artifact:
`outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_GENTLE_PUSH_X008.md`

- command_x: `0.08`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0025`
- bridge_mode: `fitted`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- duration: `15 s`
- seeds: `0-7`
- push interval: `1.0-1.5 s`
- push magnitude: `0.05-0.10`
- status: `PASS_CANDIDATE_SIM_GATE` on `8/8`
- falls: `0/8`
- duration_complete: `8/8`
- mean_local_vx_mean: `0.0303 m/s`
- track_ratio_mean: `0.3792`
- body_pitch_p95_mean: `0.1210 rad`
- base_height_min_mean: `0.1526 m`
- max_pitch_vel_p95_mean: `1.9148 rad/s`
- p95 velocity excess mean: `0.0000 rad/s`
- max velocity excess mean: `0.0000 rad/s`
- max_tracking_p95_mean: `0.1931 rad`
- push events mean: `12.3750`
- push recovery success mean: `0.9704`

## Full Gate: x=0.0 Gentle Push

Artifact:
`outputs/analysis/PHASE2_Z0025_COMMAND_GATED_BESTREC70_RATE1P9_TARGETLIMITED0999_GENTLE_PUSH_X0.md`

- command_x: `0.0`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0025`
- bridge_mode: `fitted`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- duration: `15 s`
- seeds: `0-7`
- push interval: `1.0-1.5 s`
- push magnitude: `0.05-0.10`
- status: `PASS_CANDIDATE_SIM_GATE` on `8/8`
- falls: `0/8`
- duration_complete: `8/8`
- mean_local_vx_mean: `-0.0004 m/s`
- body_pitch_p95_mean: `0.0330 rad`
- base_height_min_mean: `0.1526 m`
- max_pitch_vel_p95_mean: `2.7472 rad/s`
- p95 velocity excess mean: `0.0000 rad/s`
- max velocity excess mean: `0.0000 rad/s`
- max_tracking_p95_mean: `0.1932 rad`
- push events mean: `12.3750`
- push recovery success mean: `0.9704`

## Interpretation

The target-delta limiter resolved the parent candidate's gentle-push
instantaneous velocity excess without destroying command semantics. The
candidate stands near zero command and walks at x=0.08 under rough z=0.0025
terrain, fitted corrected actuator bridge, and gentle torso pushes.

This is still a slow walker and not a robot-approved candidate. It clears the
current gentle-push robustness gate and can be used as the next Phase 2 warm
start or baseline for broader randomization. The next offline stage should add
the next curriculum difficulty only after preserving:

1. corrected-envelope compliance,
2. x=0.0 command semantics,
3. x=0.08 forward motion,
4. gentle-push recovery.
