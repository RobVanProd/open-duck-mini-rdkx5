# Phase 2 Terrain Support Source Next Plan

status: `PASS_TERRAIN_SUPPORT_SOURCE_PLAN_READY`

This is an offline planning artifact. It did not run robot tests, SSH, deploy,
grounded replay, training, or runtime behavior changes.

## Why This Plan Exists

The live/on-policy z=0.005 recovery-DAGger path needs a positive support source
closer to z=0.005 than the current z=0.0024 traces. The latest boundary probes
show that simply taking the current Phase A2 gain099 candidate above z=0.0024
does not create such a source:

```text
z=0.00240: seed-5 x=0.08 passes 15s and source traces are BC-ready
z=0.00255: seed-5 x=0.0 and x=0.08 fail before 2s
z=0.00270: seed-5 x=0.0 and x=0.08 fail before 2s
z=0.00300: seed-5 x=0.0 and x=0.08 fail before 2s
```

Therefore `z=0.00255+` rollouts from the current candidate must not be used as
positive labels. They are failure probes only.

## Current Diagnosis

The current candidate has almost no terrain-height margin beyond z=0.0024.
The failure is a seed-5 support collapse and backward drift, not a simple
supervised-fit capacity problem:

- tiny composite fixed BC overdrives and fails,
- bounded live/on-policy recovery DAgger avoids global saturation but still
  falls before 2s,
- z=0.00255 already fails both support commands.

The source/oracle is now the bottleneck. More DAgger iterations against the
same z=0.0024 source are not justified until a stronger source exists.

## Next Authorized Offline Branch

Create a trainable terrain-support source rung, warm-started from the current
Phase A2 candidate/checkpoint, with terrain no higher than the bracketed
boundary at launch.

Initial source-training target:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.00245 or 0.00250
bridge: outputs/analysis/actuator_response_fit_corrected_knee.json
warm_start: Phase A2 / gain099 lineage
push: disabled
commands: x=0.0 and x=0.08
primary blocker: seed-5 support survival
```

This is not a full Phase 2 robustness escalation. It is a source-generation
rung whose only job is to produce passing, in-envelope support traces slightly
above z=0.0024.

## Required Gate Before Accepting Source Traces

Before any trace from the new rung can be used as a positive label or oracle
source, it must pass:

| gate | requirement |
|---|---|
| seed | seed 5 minimum; later all 8 seeds |
| `x=0.0` | duration complete; no backward drift below `-0.02 m/s`; base height min `>=0.12 m`; no corrected velocity excess |
| `x=0.08` | duration complete; positive mean vx; no corrected velocity excess; max tracking p95 `<=0.20 rad` |
| duration | start with 2s, then 15s before source promotion |
| terrain | exact z scale recorded in the artifact and manifest |

If seed-5 `x=0.0` support fails, the run is not a source no matter how good
`x=0.08` looks.

## Closed Moves

Do not:

- use `z=0.00255+` failing traces as positive labels,
- run another fixed BC fit on the failed recovery datasets,
- continue DAgger against the z=0.0024 source without a stronger source,
- escalate to z=0.005 training directly,
- add push perturbations before no-push support passes,
- run robot validation.

## Decision

Proceed next with a small terrain-support source-generation rung at
`z=0.00245` or `z=0.00250`, warm-started from Phase A2, and gate seed-5
`x=0.0` support first. The Phase 2 robustness goal remains incomplete until a
deployable candidate clears the corrected staged gates and source traces are
validated rather than inferred.
