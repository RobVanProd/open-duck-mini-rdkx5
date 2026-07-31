# Phase 2 Stage A Rough Terrain Decision

status: `HOLD_STAGE_A_ROUGH_TERRAIN_CONTACT_MARGIN`

## Summary

The promoted Stage A candidate was evaluated on the existing Playground rough
hfield terrain task with the corrected fitted bridge and no push perturbations.

```text
policy: policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx
task: rough_terrain_backlash
bridge: fitted corrected bridge
command_x: 0.08
duration: 15 s
seeds: 0-7
push: disabled
```

Artifacts:

```text
outputs/analysis/PHASE2_STAGE_A_ROUGH_TERRAIN_GATE_CPU.md
outputs/analysis/phase2_stage_a_rough_terrain_gate_cpu.json
```

## Result

```text
status: HOLD
falls/terminations: 5/8
duration_complete: 3/8
mean track ratio: -0.5120
mean vx: -0.0410 m/s
max velocity excess: 0.0000 rad/s
```

Per-seed failures included early reverse/fall cases and longer rollouts that
eventually collapsed. The held seeds that completed the duration did so with
low forward progress.

## Interpretation

This is not an actuator-envelope failure. The policy stayed under the corrected
velocity envelope, but rough terrain broke contact margin and forward progress.

Phase 2 should not jump directly to the stock rough hfield task. The next
terrain step should use a gentler curriculum, such as lower roughness, smaller
heightfield amplitude, or a foot-clearance/contact-margin preserving training
stage that is explicitly checked against the flat Stage A gate after each
update.

No robot motion, SSH, deployment, grounded replay, runtime behavior change, or
training was performed by this terrain gate.
