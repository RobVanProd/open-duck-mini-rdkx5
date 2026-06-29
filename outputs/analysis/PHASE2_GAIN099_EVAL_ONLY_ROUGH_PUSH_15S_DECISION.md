# Phase 2 Gain-0.99 Eval-Only Rough/Push 15s Decision

status: `PASS_EVAL_ONLY_GAIN099_ROUGH_PUSH_15S_NOT_DEPLOYABLE`

## Scope

This is an offline CPU sim gate only. No robot tests, SSH, deploy, grounded
replay, runtime behavior changes, or policy overwrite were performed.

## Candidate Under Test

```text
candidate:
  policy/candidates/phase2_stagea2_seed5_recovery_command_gated_20260628/candidate.onnx

candidate_sha256:
  d0cec0b9dcc666416f0ecc8383a51367529273013d912b26399339e2c4b1c3e6

corrected_bridge:
  outputs/analysis/actuator_response_fit_corrected_knee.json

task:
  rough_terrain_backlash

terrain_hfield_z_scale:
  0.002

bridge_mode:
  fitted

policy_action_gain:
  0.99
```

Important: `policy_action_gain=0.99` is an evaluator-side multiplier. This
result is not deployable as-is unless the gain is baked into a candidate ONNX
or otherwise represented in the deployable policy artifact and then re-gated.

## Artifacts

```text
x=0.08:
  outputs/analysis/PHASE2_SEED5_NEIGHBOR_RECOVERY_STAGEA2_COMMAND_GATED_GAIN099_X008_ROUGH_Z002_GENTLE_PUSH_15S_8SEED_CPU.md
  outputs/analysis/phase2_seed5_neighbor_recovery_stagea2_command_gated_gain099_x008_rough_z002_gentle_push_15s_8seed_cpu.json

x=0.0:
  outputs/analysis/PHASE2_SEED5_NEIGHBOR_RECOVERY_STAGEA2_COMMAND_GATED_GAIN099_X0_ROUGH_Z002_GENTLE_PUSH_15S_8SEED_CPU.md
  outputs/analysis/phase2_seed5_neighbor_recovery_stagea2_command_gated_gain099_x0_rough_z002_gentle_push_15s_8seed_cpu.json
```

## Gate Result

Both commands were evaluated for 15 seconds across seeds 0-7 with fitted
corrected bridge, rough `z=0.002`, and gentle pushes every `1.0-1.5 s` at
magnitude `0.05-0.10`.

### x=0.08

```text
status:                 PASS_CANDIDATE_SIM_GATE 8/8
falls:                  0/8
duration_complete:      8/8
mean vx:                0.0328 m/s
mean track ratio:       0.4104
max pitch vel p95:      2.3950 rad/s
max velocity excess:    0.0000 rad/s
mean tracking p95:      0.1924 rad
max tracking p95:       0.1944 rad
mean push success:      0.9704
min swing peak lift:    0.0116 m
min swing rel-x p95:    0.0063 m
```

### x=0.0

```text
status:                 PASS_CANDIDATE_SIM_GATE 8/8
falls:                  0/8
duration_complete:      8/8
mean vx:                0.0007 m/s
max |seed mean vx|:     0.0037 m/s
max pitch vel p95:      0.3906 rad/s
max velocity excess:    0.0000 rad/s
mean tracking p95:      0.0652 rad
max tracking p95:       0.0687 rad
mean push success:      0.9704
```

## Decision

The gain-0.99 diagnostic is a useful local robustness margin result: the same
packaged command-gated candidate survives the 15-second rough-terrain gentle
push gate at both `x=0.08` and `x=0.0` when actions are attenuated by 1%.

It is not a deployable promotion yet. The next deployable step is to package a
real gain-0.99 candidate or otherwise remove the evaluator-only multiplier,
then run the canonical no-push and gentle-push gates again. If the packaged
gain loses no-push swing geometry, keep it diagnostic-only and return to
training-time robustness rather than runtime/eval attenuation.
