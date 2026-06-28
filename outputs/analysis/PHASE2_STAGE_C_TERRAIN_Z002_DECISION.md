# Phase 2 Stage C Terrain z=0.002 Decision

status: `HOLD_STAGE_C_TERRAIN_Z002_TRACKING_MARGIN`

## Scope

Offline sim only. No robot, SSH, deploy, grounded replay, or runtime behavior
change was performed.

This stage tested whether the promoted Stage A candidate could be hardened from
flat ground to a very mild rough-terrain heightfield:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
bridge: corrected fitted actuator bridge
command_x: 0.08
screen: 2 seeds, 5 s, CPU closed-loop eval
strict tracking gate: max pitch-chain tracking p95 <= 0.2000 rad
```

## Baseline

The Stage A promoted candidate is already close on this terrain but does not
strictly pass the short screen:

```text
policy: policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx
seed 0: HOLD_CANDIDATE_TRACKING, tracking p95 0.2079 rad
seed 1: PASS_CANDIDATE_SIM_GATE, tracking p95 0.1981 rad
mean track ratio: 0.3914
mean vx: 0.0313 m/s
velocity excess: 0.0000 rad/s
```

## Stage C0

Recipe: warm-start from the Stage A2 checkpoint, train on
`rough_terrain_backlash` with `terrain_hfield_z_scale=0.002`, narrow domain
randomization, no pushes, and strong behavior/restore-policy anchoring.

Training completed successfully:

```text
artifact:
  outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu
status: PASS_SMOKE_RUN
elapsed_s: 428.43
terrain XML restored: true
```

Best short-screen export:

```text
policy: c0_245760
onnx: outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu/2026_06_28_064431_245760.onnx
seed 0: HOLD_CANDIDATE_TRACKING, tracking p95 0.2040 rad
seed 1: PASS_CANDIDATE_SIM_GATE, tracking p95 0.1965 rad
mean track ratio: 0.3965
mean vx: 0.0317 m/s
velocity excess: 0.0000 rad/s
```

C0 improved the seed-0 tracking miss from `0.2079` to `0.2040` rad, but did not
clear the strict gate.

## Stage C1

Recipe: warm-start from C0 final checkpoint, same terrain, add an
`actuator_tracking_scale=-0.20` penalty.

Training completed successfully:

```text
artifact:
  outputs/phase2_domain_randomization/stage_c1_terrain_z002_tracking_from_c0_gpu/smoke_20260628T110711Z_gpu
status: PASS_SMOKE_RUN
elapsed_s: 421.03
terrain XML restored: true
```

Result: C1 did not improve the best strict tracking margin. The step-0 export
matches C0 final, and trained exports retained the same pass/hold shape:

```text
best by tracking: c1_0
seed 0 tracking p95: 0.2040 rad
seed 1 tracking p95: 0.1965 rad
best mean track ratio: c1_81920, 0.4184
velocity excess: 0.0000 rad/s
```

Inspection showed the seed-0 miss was dominated by joint target tracking, not
bridge tracking. For example, `c1_81920` seed 0 had:

```text
left_knee joint_target_tracking_p95: 0.2070 rad
pitch-chain bridge_tracking_p95 max: 0.1103 rad
max pitch-chain sent velocity p95: 1.7688 rad/s
velocity excess: 0.0000 rad/s
```

Therefore the C1 penalty was aimed mostly at the wrong layer: it penalizes
sent-vs-applied actuator bridge error, while the hold is applied-target vs
simulated-joint tracking on terrain.

## Stage C2

Recipe: warm-start from C1 81920, same terrain, add target-rate penalty
(`target_rate_scale=-0.05`) with mild actuator-tracking penalty
(`actuator_tracking_scale=-0.05`).

Training completed successfully:

```text
artifact:
  outputs/phase2_domain_randomization/stage_c2_terrain_z002_targetrate_from_c1_gpu/smoke_20260628T113221Z_gpu
status: PASS_SMOKE_RUN
elapsed_s: 422.28
terrain XML restored: true
```

Best short-screen export:

```text
policy: c2_163840
onnx: outputs/phase2_domain_randomization/stage_c2_terrain_z002_targetrate_from_c1_gpu/smoke_20260628T113221Z_gpu/2026_06_28_073829_163840.onnx
seed 0: HOLD_CANDIDATE_TRACKING, tracking p95 0.2044 rad
seed 1: PASS_CANDIDATE_SIM_GATE, tracking p95 0.1941 rad
mean track ratio: 0.4070
mean vx: 0.0326 m/s
velocity excess: 0.0000 rad/s
```

C2 reduced neither the strict seed-0 tracking hold nor the terrain stage enough
to promote.

## Decision

Do not promote a Stage C terrain candidate yet.

The useful result is the bracket:

```text
flat: pass
terrain z=0.002: near-pass, upright and in-envelope, tracking p95 still ~0.204 rad on seed 0
terrain z=0.005: hold
stock z=0.010: hard hold
```

The current Stage C blocker is not falling, saturation, or velocity-envelope
excess. It is a small terrain-induced joint target tracking margin, currently
most visible on seed 0 and the left knee.

Next Stage C work should target joint-target tracking on mild terrain without
eroding forward progress. A stronger generic bridge-tracking penalty is not the
right lever; target-rate reduction helped only marginally.
