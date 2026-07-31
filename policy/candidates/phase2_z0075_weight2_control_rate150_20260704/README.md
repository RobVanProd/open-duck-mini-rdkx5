# Phase 2 z=0.0075 Weight2 Control Rate150

status: `HOLD_FULL_SEED_DISTRIBUTION_REGRESSED`

This candidate is an offline Phase 2 experiment only. Do not deploy it, do not
run robot validation with it, and do not treat it as a promoted policy.

## Artifacts

- ONNX: `candidate.onnx`
- ONNX sha256: `a05c1629db07db42c54197f151d97b114ca1995862c403f0ddcd2d8a01c029a9`
- student NPZ: `student.npz`
- student NPZ sha256: `a243c38d17d5b55972cdf4a96991d280b973bad65ad19f732d289f76d9e2385c`
- source manifest: `outputs/analysis/phase2_z0075_iter6_weight2_control_manifest.json`
- dataset id: `084d8e7fd150d37c`
- samples: `50253`

## Result

This candidate lowered the seed-0 late push-window recovery weight from `4.0`
to `2.0` and preserved the seed-7 pass-control trace.

It passed the compact seed0/seed7 z=0.0075 intermediate-push boundary:

- seed 0: full 750 samples, track ratio `0.3257`, zero p95/max envelope excess
- seed 7: full 750 samples, track ratio `0.3823`, zero p95/max envelope excess

It failed the full 8-seed x=0.08 intermediate-push gate:

- pass: `2/8`
- falls / terminations: `6/8`
- mean track ratio: `-0.2312`
- max p95 envelope excess: `0.0000 rad/s`

Decision artifact:

`outputs/analysis/PHASE2_Z0075_WEIGHT2_CONTROL_RATE150_DECISION.md`
