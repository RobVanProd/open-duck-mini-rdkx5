# Phase 2 z=0.0075 Control-Preserving Recovery Rate150

status: `HOLD_SEED7_RESTORED_SEED0_EARLY_LUNGE`

This candidate is an offline Phase 2 experiment only. Do not deploy it, do not
run robot validation with it, and do not treat it as a promoted policy.

## Artifacts

- ONNX: `candidate.onnx`
- ONNX sha256: `290a4dc13c37396d3556d7a0425951374f4597646b419331ced9f8d21c38cd9c`
- student NPZ: `student.npz`
- student NPZ sha256: `26a154bf437daf91af3bb534e0f1a2357788046e8fbae4a29a9eba36c99d13fb`
- source manifest: `outputs/analysis/phase2_z0075_iter4_control_preserving_recovery_manifest.json`

## Result

The candidate was trained from the iter3 recovery manifest plus a weighted
iter2 seed-7 pass-control trace.

The seed-7 pass-control worked: seed 7 returned to a full-duration pass under
the compact z=0.0075 intermediate-push boundary. Seed 0 regressed to an early
high-track-ratio lunge and fall at sample 142, with zero corrected-envelope
velocity excess.

Decision artifact:

`outputs/analysis/PHASE2_Z0075_CONTROL_PRESERVING_RECOVERY_RATE150_DECISION.md`
