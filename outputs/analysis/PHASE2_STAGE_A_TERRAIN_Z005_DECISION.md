# Phase 2 Stage A Terrain Z005 Decision

status: `HOLD_STAGE_A_TERRAIN_Z005`

## Summary

The promoted Stage A candidate was evaluated on `rough_terrain_backlash` with
the hfield vertical scale reduced from stock `0.01` to `0.005`.

```text
policy: policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.005
bridge: fitted corrected bridge
command_x: 0.08
duration: 15 s
seeds: 0-7
push: disabled
```

Artifacts:

```text
outputs/analysis/PHASE2_STAGE_A_TERRAIN_Z005_GATE_CPU.md
outputs/analysis/phase2_stage_a_terrain_z005_gate_cpu.json
```

## Result

```text
status: HOLD
duration_complete: 7/8
falls/terminations: 1/8
pass: 2/8
tracking holds: 5/8
mean track ratio: -0.0485
mean vx: -0.0039 m/s
max velocity excess: 0.0000 rad/s
```

## Interpretation

This is a terrain/contact-margin hold, not an actuator-envelope hold. The
candidate stayed inside the corrected velocity envelope, but z-scale `0.005`
caused one fall/termination and pushed most completed seeds over the strict
tracking threshold.

The useful terrain bracket is:

```text
flat terrain: pass
z=0.002: near-pass, 8/8 upright, one 0.0001 rad tracking miss
z=0.005: hold
z=0.010 stock rough: hard hold
```

The next terrain curriculum should start at `z=0.002` and preserve the flat
Stage A gait before attempting `z=0.005`.

No robot motion, SSH, deployment, grounded replay, runtime behavior change, or
training was performed by this terrain gate.
