# Phase 2 z=0.0075 Anti-Lunge Zero50 Rate150

status: `HOLD_ANTILUNGE_REGRESSED_SEED7`

This candidate is an offline Phase 2 experiment only. Do not deploy it, do not
run robot validation with it, and do not treat it as a promoted policy.

## Artifacts

- ONNX: `candidate.onnx`
- ONNX sha256: `abced43cfaaa2a05f2b6576819dae0950b6a72f946d336a7f541ad0ab8c49b7c`
- student NPZ: `student.npz`
- student NPZ sha256: `ff97e0b81f50628327bfad0627636e3eea24caedcee42dc5cdba2a7bd589a492`
- source manifest: `outputs/analysis/phase2_z0075_iter5_antilunge_zero50_manifest.json`
- dataset id: `45f8a46ea0430e64`
- samples: `50273`

## Result

The candidate was trained from the iter4 control-preserving recovery manifest
plus a zero-action teacher relabel of the iter4 seed-0 lunge trace. The immediate
pre-fall anti-lunge tail window was weighted to damp seed-0 overspeed without
losing seed-7 control behavior.

It failed the compact boundary screen:

- z=0.0075 rough terrain
- x=0.08
- fitted corrected bridge
- intermediate push magnitude `0.075-0.125`
- seeds `0,7`

Seed 0 still fell at sample 205 with high track ratio. Seed 7 regressed from the
iter4 full-duration pass to a sample-621 fall.

Decision artifact:

`outputs/analysis/PHASE2_Z0075_ANTILUNGE_ZERO50_RATE150_DECISION.md`
