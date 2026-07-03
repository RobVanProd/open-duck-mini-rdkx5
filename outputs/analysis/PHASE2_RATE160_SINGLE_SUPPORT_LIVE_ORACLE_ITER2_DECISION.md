# Phase 2 Rate160 Live-Oracle Iter2 Decision

status: `HOLD_RATE160_MAX_VELOCITY_SPIKE`

## Summary

The `rate160` refit tested whether simply lowering the supervised
target-rate limit from `1.65` to `1.60 rad/s` would remove the iter2
student's strict corrected max-velocity excess while preserving the improved
motion.

It did not. The seed-0 screen preserved similar forward motion, but the
instantaneous corrected max velocity excess worsened from `0.0149 rad/s` in
the rate165 iter2 gate to `0.2730 rad/s`.

No robot test, SSH, deploy, grounded replay, PPO/domain-randomization training,
or runtime behavior change was performed.

## Fit

- fit artifact:
  `outputs/analysis/PHASE2_RATE160_SINGLE_SUPPORT_LIVE_ORACLE_ITER2_STUDENT.md`
- ONNX:
  `outputs/analysis/phase2_rate160_single_support_live_oracle_iter2_student/candidate.onnx`
- ONNX sha256:
  `53d1694f964870f1bd2c51d5759234f088bc154c90eddb2db845ccbf55ee74af`
- samples: `28500`
- p95 action error: `0.021361`
- ONNX max abs error: `0.0000003576`

## Seed-0 x=0.08 Screen

Gate artifact:

```text
outputs/analysis/PHASE2_RATE160_SINGLE_SUPPORT_LIVE_ORACLE_ITER2_STUDENT_X008_SEED0_SCREEN.md
outputs/analysis/phase2_rate160_single_support_live_oracle_iter2_student_x008_seed0_screen.json
```

Result:

- status: `HOLD_CANDIDATE_TARGET_VELOCITY`
- duration complete: `1/1`
- falls: `0/1`
- mean local vx: `0.0323 m/s`
- track ratio: `0.4031`
- single support: `26.2667%`
- double support: `73.7333%`
- max pitch-chain p95 velocity: `1.6400 rad/s`
- corrected p95 velocity excess: `0.0000 rad/s`
- corrected max velocity excess: `0.2730 rad/s`
- max tracking p95: `0.1850 rad`

## Decision

Do not run the full 8-seed gate for this candidate and do not promote it.

This result rejects the simple scalar lower-rate refit as the next fix. The
next attempt should use an explicit instantaneous max-velocity/spike guard in
the supervised objective or post-fit screening, while preserving the iter2
motion and single-support gains.
