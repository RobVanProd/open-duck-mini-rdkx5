# Phase 2 z0.0075 Iter21 Balanced + Seed6/7 Recovery Rate150

Status: `HOLD_SEED67_RECOVERY_REGRESSED_SEED0`

This candidate was trained from the Iter21 balanced post-push recovery manifest plus two
additional relabelled failed-push snippets from seeds 6 and 7. It is not promotable.

## Files

- `candidate.onnx`
- source manifest: `outputs/analysis/phase2_z0075_iter21_balanced_plus_seed67_recovery_merged_manifest.json`
- student report: `outputs/analysis/PHASE2_Z0075_ITER21_BALANCED_PLUS_SEED67_RECOVERY_RATE150_STUDENT.md`
- focused seed0 regression: `outputs/analysis/phase2_z0075_iter21_balanced_plus_seed67_recovery_rate150_student/x008_focused_seed_screen/iter21_balanced_seed67/seed_000/CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md`

## Hashes

- candidate ONNX sha256: `a1e703d63d8aaf339fb804ed5f73c12f7412bc449278515e53c00e54256150bf`
- student NPZ sha256: `9c402abc681a0689fa95aa55f2a6cfff6f5a2f6501e5be8705f7cb27012139e6`
- merged manifest sha256: `a5a69c43f1f9e56d79549e39fba92262537876a0c7a1f914351818cd7cd174a9`

## Gate Result

The x=0.08 rough-terrain intermediate-push focused screen was stopped after the first
regression guard failed:

- seed 0: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
- samples: `565`
- termination: `fall_or_nan`
- track ratio: `0.7615`
- max pitch-chain sent velocity p95: `1.5979 rad/s`
- max corrected-envelope excess: `0.0000 rad/s`
- max pitch-chain tracking p95: `0.1836 rad`
- base height min: `0.0054 m`

The failure is a stability regression, not an actuator-envelope violation.

## Decision

Do not deploy or promote this candidate. The seed6/7 recovery snippets are useful
evidence, but adding them directly to the balanced manifest over-corrected the student
and regressed seed0. The next step should change weighting or representation, not simply
append more high-fall recovery snippets at the same strength.
