# Phase 2 Stage A Terrain Z002 Decision

status: `NEAR_PASS_STAGE_A_TERRAIN_Z002`

## Summary

The promoted Stage A candidate was evaluated on the existing rough terrain
scene with the hfield vertical scale reduced from the stock `0.01` to `0.002`.
The override is eval-only and uses a temporary XML file that is removed after
the worker constructs the environment.

```text
policy: policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
bridge: fitted corrected bridge
command_x: 0.08
duration: 15 s
seeds: 0-7
push: disabled
```

Artifacts:

```text
outputs/analysis/PHASE2_STAGE_A_TERRAIN_Z002_GATE_CPU.md
outputs/analysis/phase2_stage_a_terrain_z002_gate_cpu.json
```

## Result

```text
duration_complete: 8/8
falls: 0/8
pass: 7/8
hold: 1/8
mean track ratio: 0.4033
mean vx: 0.0323 m/s
max velocity excess: 0.0000 rad/s
seed 7 tracking p95: 0.2001 rad
tracking gate: <= 0.2000 rad
```

## Interpretation

This is a near-pass, not a strict pass. The policy stayed upright on every seed
and stayed inside the corrected actuator envelope. The only miss was a
`0.0001 rad` tracking excess on seed 7.

Compared with the stock rough hfield (`0.01`), which produced `5/8`
terminations and `3/8` low-progress holds, z-scale `0.002` is a valid first
terrain curriculum rung. It should be used before attempting `0.005` or the
stock rough terrain.

No robot motion, SSH, deployment, grounded replay, runtime behavior change, or
training was performed by this terrain gate.
