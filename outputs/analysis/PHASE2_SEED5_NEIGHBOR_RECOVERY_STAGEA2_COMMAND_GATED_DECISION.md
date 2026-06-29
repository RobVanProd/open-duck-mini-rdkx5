# Phase 2 Stage-A2 / Seed5-Recovery Command Gate

status: `PASS_ROUGH_TERRAIN_NO_PUSH_HOLD_GENTLE_PUSH_ENVELOPE`

This is an offline sim artifact. It did not train, deploy, SSH, run robot
tests, or change robot runtime behavior.

## Candidate

The deployable ONNX command gate composes:

- low-command branch: `policy/candidates/phase2_stage_a2_gain099_20260628/candidate.onnx`
- high-command branch: `outputs/analysis/phase2_seed5_neighbor_recovery_contactphase_bc_student/candidate.onnx`
- gate: `abs(obs[6]) <= 0.02`
- output: `outputs/analysis/phase2_seed5_neighbor_recovery_stagea2_command_gated_candidate/candidate.onnx`
- promoted copy: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_20260628/candidate.onnx`
- output sha256: `d0cec0b9dcc666416f0ecc8383a51367529273013d912b26399339e2c4b1c3e6`

ONNX branch verification passed with zero action error:

```text
outputs/analysis/phase2_seed5_neighbor_recovery_stagea2_command_gated_verify.json
status: PASS_ONNX_GATE_VERIFY
```

## Why This Branch

The contact-phase seed5 recovery student fixed the rough `x=0.08` seed-5
failure but fell at rough `x=0.0` seed 5. Existing low-command branches were
screened on the same rough zero-command seed:

```text
phase1:   PASS_CANDIDATE_SIM_GATE
stage_a2: PASS_CANDIDATE_SIM_GATE
old_x0safe: HOLD_CANDIDATE_FALL_OR_TERMINATION
scale075:   HOLD_CANDIDATE_FALL_OR_TERMINATION
```

Stage A2 was selected as the low-command branch because it is the current
Phase 2 lineage and survives the rough zero-command hard seed.

## Rough Terrain, No Push

Configuration:

```text
task: rough_terrain_backlash
hfield z scale: 0.002
bridge: corrected fitted bridge
duration: 5 s
seeds: 0-7
```

### `x=0.08`

Artifact:

```text
outputs/analysis/PHASE2_SEED5_NEIGHBOR_RECOVERY_STAGEA2_COMMAND_GATED_X008_ROUGH_Z002_8SEED_GATE_CPU.md
```

Result:

```text
status: PASS_CANDIDATE_SIM_GATE 8/8
falls: 0/8
duration_complete: 8/8
mean vx: 0.0332 m/s
mean track ratio: 0.4150
max pitch-chain p95 target velocity: 2.4109 rad/s
max velocity-envelope excess: 0.0000 rad/s
max tracking p95: 0.1984 rad
min swing peak lift: 0.0108 m
min swing rel-x p95 range: 0.00325 m
```

### `x=0.0`

Artifact:

```text
outputs/analysis/PHASE2_SEED5_NEIGHBOR_RECOVERY_STAGEA2_COMMAND_GATED_X0_ROUGH_Z002_8SEED_GATE_CPU.md
```

Result:

```text
status: PASS_CANDIDATE_SIM_GATE 8/8
falls: 0/8
duration_complete: 8/8
mean vx: 0.0024 m/s
max pitch-chain p95 target velocity: 0.9804 rad/s
max velocity-envelope excess: 0.0000 rad/s
max tracking p95: 0.1056 rad
```

This is the first recorded rough-terrain `z=0.002` deployable-shape result in
this branch that preserves both positive-command motion and zero-command
stability across all eight seeds.

## Gentle Push Diagnostic

Configuration:

```text
task: rough_terrain_backlash
hfield z scale: 0.002
push interval: 1.0-1.5 s
push magnitude: 0.05-0.10
duration: 5 s
seeds: 0-7
```

### `x=0.08`

Artifact:

```text
outputs/analysis/PHASE2_SEED5_NEIGHBOR_RECOVERY_STAGEA2_COMMAND_GATED_X008_ROUGH_Z002_GENTLE_PUSH_8SEED_GATE_CPU.md
```

Result:

```text
status: HOLD_CANDIDATE_TARGET_VELOCITY
falls: 0/8
duration_complete: 8/8
mean vx: 0.0341 m/s
mean track ratio: 0.4264
mean push recovery success: 0.9062
max pitch-chain p95 target velocity: 2.4392 rad/s
max velocity-envelope excess: 0.0212 rad/s
max tracking p95: 0.1964 rad
```

Interpretation: gentle pushes did not cause falls and did not break tracking,
but one seed crossed the corrected per-joint target-velocity envelope by
`0.0212 rad/s`. This is not a promotion pass.

### `x=0.0`

Artifact:

```text
outputs/analysis/PHASE2_SEED5_NEIGHBOR_RECOVERY_STAGEA2_COMMAND_GATED_X0_ROUGH_Z002_GENTLE_PUSH_8SEED_GATE_CPU.md
```

Result:

```text
status: PASS_CANDIDATE_SIM_GATE 8/8
falls: 0/8
duration_complete: 8/8
mean vx: 0.0023 m/s
mean push recovery success: 0.9062
max velocity-envelope excess: 0.0000 rad/s
max tracking p95: 0.1056 rad
```

## Decision

`PASS_ROUGH_TERRAIN_NO_PUSH_HOLD_GENTLE_PUSH_ENVELOPE`

The command-gated Stage-A2 / seed5-recovery composition is a meaningful Phase 2
terrain result: rough `z=0.002` no-push gate passes at both `x=0.08` and
`x=0.0` across all eight seeds while preserving corrected-envelope compliance.

It is not yet a robust push candidate. Gentle pushes are stable, but the moving
gate has a small target-velocity envelope excess on seed 6. The next offline
step should reduce high-command branch target-rate margin under perturbation,
or train a push-aware refinement from this command-gated artifact. Robot
validation remains blocked.
