# Phase 2 Stage-A2 Gain-0.99 Terrain z=0.005 Boundary

status: `HOLD_TERRAIN_Z005_SEED5_FALL`

## Scope

This is an offline CPU sim probe only. No robot tests, SSH, deploy, grounded
replay, runtime behavior changes, or policy overwrite were performed.

## Candidate

```text
candidate:
  policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx

candidate_sha256:
  209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b
```

## Probe

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.005
command_x: 0.08
bridge_mode: fitted corrected knee bridge
duration: 15 s
seeds: 0-7
pushes: disabled
policy_action_gain: 1.0
```

Artifact:

```text
outputs/analysis/PHASE2_STAGEA2_SEED5_RECOVERY_COMMAND_GATED_GAIN099_X008_ROUGH_Z005_NOPUSH_15S_8SEED_CPU.md
outputs/analysis/phase2_stagea2_seed5_recovery_command_gated_gain099_x008_rough_z005_nopush_15s_8seed_cpu.json
```

## Result

```text
PASS_CANDIDATE_SIM_GATE:       7/8
HOLD_CANDIDATE_FALL_OR_TERMINATION: 1/8
fall seed:                     5
fall sample count:             56
fall termination:              fall_or_nan
seed5 mean vx:                 -0.2654 m/s
seed5 base height min:         0.0677 m
max velocity excess:           0.0000 rad/s
```

The seven surviving seeds stayed inside the corrected actuator envelope and
completed the 15-second horizon. The hold is a terrain stability/contact
boundary, not an actuator-envelope violation.

## Decision

Do not advance this candidate to `z=0.005` terrain as-is. The current packaged
gain-0.99 candidate remains the best `z=0.002` rough-terrain gentle-push
candidate, but the next Phase 2 training/eval step should target the seed-5
rougher-terrain fall before widening the terrain curriculum.
