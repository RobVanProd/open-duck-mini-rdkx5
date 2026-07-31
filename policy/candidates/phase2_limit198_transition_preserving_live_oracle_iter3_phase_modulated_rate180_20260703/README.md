# Phase 2 Limit198 Transition-Preserving Iter3 Phase-Modulated Rate180 Candidate

status: `PASS_PHASE2_RATE180_CORRECTED_BRIDGE_GATES`

This is the current deployable offline sim candidate from the transition-
preserving live-oracle iter3 branch. It is a behavior-cloned, feed-forward
phase/command-modulated student with the deployed policy contract:

`obs[1,101] -> continuous_actions[1,14]`

It passed the corrected-bridge `rough_terrain_backlash` z=0.0026 screens:

- x=0.08: `8/8` seeds, `0` falls, `0` velocity excess
- x=0.0: `8/8` seeds, `0` falls, `0` velocity excess

This candidate is not a grounded-test authorization by itself. Robot validation
remains a separate operator-approved step.

## Files

- `candidate.onnx`
  - sha256: `b658c3380d1ad3dbd8912c988a3ff0e4b019735f220cf56351e9c783f328d5b1`
- `student.npz`
  - sha256: `6ecbeffc9037658386b3ec2c3722f30e5dc5ae31547c7182550140e11666a505`

## Gate Summary

### x=0.08

- mean vx: `0.035237 m/s`
- track ratio: `0.440467`
- max pitch vel p95: `1.771620 rad/s`
- max velocity excess: `0.0 rad/s`
- max tracking p95: `0.189108 rad`
- min swing peak lift: `0.014507 m`
- single support: `28.0%`

### x=0.0

- mean vx: `0.000169 m/s`
- max pitch vel p95: `0.047043 rad/s`
- max velocity excess: `0.0 rad/s`
- max tracking p95: `0.033892 rad`
- double support: `100.0%`

## Source

- manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json`
- fit report: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_student_rate180/PHASE_MODULATED_BC_STUDENT.md`
- decision: `outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE180_DECISION.md`
