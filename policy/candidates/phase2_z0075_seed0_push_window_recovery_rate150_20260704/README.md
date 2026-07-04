# Phase 2 z=0.0075 Seed0 Push-Window Recovery Rate150

status: `HOLD_PUSH_WINDOW_PITCHOVER_REGRESSION`

This candidate is an offline Phase 2 experiment only. Do not deploy it, do not
run robot validation with it, and do not treat it as a promoted policy.

## Artifacts

- ONNX: `candidate.onnx`
- ONNX sha256: `7bfbc920dd9c7edb423831c3c0aa05b0a444f15640b5e6974a2ac94169ba495e`
- student NPZ: `student.npz`
- student NPZ sha256: `6e52662125413c9318ccd5e8b7626b25ee6ac7e8e76e72161d181a36751547f0`
- source manifest: `outputs/analysis/phase2_z0075_iter3_seed0_push_window_recovery_manifest.json`

## Result

The candidate was trained from the iter2 recovery aggregate plus a source-VX
teacher relabel of the iter2 seed-0 failure trace, with ticks `650-687`
upweighted as the active late push-window recovery region.

It failed the compact boundary screen:

- z=0.0075 rough terrain
- x=0.08
- fitted corrected bridge
- intermediate push magnitude `0.075-0.125`
- seeds `0,7`

Both seeds fell with zero p95/max corrected-envelope excess. The failure
diagnostic classified both as `PUSH_WINDOW_PITCHOVER`.

Decision artifact:

`outputs/analysis/PHASE2_Z0075_SEED0_PUSH_WINDOW_RECOVERY_RATE150_DECISION.md`
