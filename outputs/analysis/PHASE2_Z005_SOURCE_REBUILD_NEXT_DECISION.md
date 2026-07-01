# Phase 2 z=0.005 Source Rebuild Next Decision

status: `PLAN_Z005_SOURCE_REBUILD_REQUIRED`

This is an offline planning artifact. It did not train, SSH, deploy, run robot
tests, grounded replay, or change runtime behavior.

## Current Evidence

The current corrected-bridge Phase 2 path is blocked at the source/oracle level,
not by the student architecture alone.

Committed evidence:

- `outputs/analysis/PHASE2_Z005_LIVE_ORACLE_ITER0_STUDENT_FIT_DECISION.md`
- `outputs/analysis/PHASE2_Z005_SEED5_RECOVERY_ENHANCED_SOURCE_DECISION.md`

Findings:

- Iter0 phase/command-modulated BC fit was clean and mostly in-envelope, but
  held at z=0.005 with seed 5 still falling and other seeds under-progressing.
- Iter0 recurrent H96 diagnostic was worse: 8/8 falls and target-slew overdrive.
- Same-tick neighbor recovery relabeling for seed 5 did not fix seed 5 and
  introduced a seed-3 fall.
- The current oracle/source does not produce recovery labels that change the
  z=0.005 support state enough for distillation.

## Closed Inside This Branch

Do not spend more compute on these without a new pre-registration:

- larger supervised fits on `3f68992af82062f7`
- recurrent hidden-size or sequence-length tweaks on the same aggregate
- same-tick neighbor recovery relabeling for seed 5
- scalar support/base-height reward continuation as the next default move
- treating z=0.0024 pass traces as sufficient z=0.005 source data

## Required Next Source

Before another live-oracle DAgger iteration, build or mine a source that itself
passes a z=0.005 source gate under the corrected bridge.

Minimum source gate:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.005
bridge: corrected fitted bridge
fit_json: outputs/analysis/actuator_response_fit_corrected_knee.json
command_x: 0.08
seeds: 0-7
duration: 15s
```

Required:

- `8/8` no early fall or NaN
- seed 5 duration complete
- mean track ratio `>= 0.35`
- no corrected per-joint pitch-chain p95 velocity excess
- max pitch-chain tracking p95 `<= 0.20 rad`
- base height minimum `>= 0.12 m` on every seed
- useful support transfer: single-support mean `>= 20%` and double-support mean
  `<= 80%`

This is a source gate, not a deployment gate. Passing it authorizes another
offline distillation iteration only.

## Next Allowed Work

1. Produce a candidate z=0.005 source using a method that is not same-tick
   neighbor averaging. Valid options include a closed-loop controller/source
   that explicitly stabilizes seed 5, an intermediate terrain curriculum that
   generates z=0.005-surviving traces, or a new policy/source that passes the
   source gate above.
2. Write a compact source manifest with hashes and source-gate metrics.
3. Run live-oracle DAgger iteration 1 only after the source gate passes.
4. Keep robot validation blocked until a deployable ONNX clears the corrected
   candidate gate.

## Stop Rule

If no z=0.005 source can satisfy the source gate without leaving the corrected
envelope, stop Phase 2 training and report:

```text
HOLD_Z005_SOURCE_NOT_AVAILABLE
```

That result would mean the next work is source/controller design, not another
student fit.
