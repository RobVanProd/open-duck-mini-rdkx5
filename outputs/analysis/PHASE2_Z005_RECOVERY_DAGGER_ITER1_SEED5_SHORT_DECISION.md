# Phase 2 z=0.005 Recovery DAgger Iter1 Seed-5 Short Decision

status: `HOLD_RECOVERY_DAGGER_ITER1_SHORT_GATE_FAILED`

This is an offline live/on-policy recovery DAgger precheck. It did not run
robot tests, SSH, deploy, grounded replay, PPO training, or runtime behavior
changes.

## Inputs

- student: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- teacher/base manifest: `outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.005`
- seed: `5`
- short gate duration: `2s`

## DAgger Data

The bounded live recovery pass completed:

```text
outputs/analysis/phase2_z005_recovery_dagger_iter1_seed5_short/LIVE_ORACLE_DAGGER_ITERATION.md
status: PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY
aggregate dataset_id: ca062df6fc861084
entries: 10
samples: 6117
```

The aggregate combines the 6000-sample corrected z=0.0024 source with 117
student-visited z=0.005 seed-5 drift samples relabeled by the current oracle
path.

## Supervised Fit

The phase/command-modulated BC student fit the aggregate:

```text
outputs/analysis/PHASE2_Z005_RECOVERY_DAGGER_ITER1_SEED5_SHORT_BC_FIT.md
status: PASS_PHASE_MODULATED_BC_FIT_SMOKE
```

| metric | value |
|---|---:|
| samples | `6117` |
| p95 abs error | `0.01963` |
| target-rate p95 | `1.81627 rad/s` |
| target-rate max | `2.78872 rad/s` |
| ONNX p95 error | `0.00000012` |

Fit quality alone is not promotable; the short closed-loop gate is decisive.

## Short Gate Results

| command | status | samples | mean vx | base height min | max tracking p95 | max p95 vel excess | max vel excess |
|---|---|---:|---:|---:|---:|---:|---:|
| `x=0.0` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 41 | `-0.3861` | `0.0450` | `0.2425` | `0.0000` | `0.0000` |
| `x=0.08` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 64 | `-0.2340` | `0.0684` | `0.1801` | `0.0000` | `0.0399` |

The `x=0.0` gate fails on fall, reverse velocity, low base height, and tracking
above the corrected threshold. The `x=0.08` gate fails on fall, reverse
velocity, low base height, and a small right-ankle max-velocity excess.

## Decision

Do not promote the iter1 short student. Do not use its ONNX as a parent policy.
Do not run a full 8-seed z=0.005 gate or Colab scaling from this fit.

The important difference from the previous 141-sample composite BC smoke is
that this student no longer saturates all pitch-chain joints at the simulator
target-rate ceiling. However, live recovery DAgger using the z=0.0024 source
still does not create a stable z=0.005 support behavior for seed 5.

## Next Implication

The current corrected z=0.0024 oracle is not strong enough to relabel z=0.005
seed-5 collapse states into a passing support behavior. The next source work
should generate a passing intermediate-terrain support source closer to
`z=0.005` before another DAgger fit, rather than adding more capacity or more
samples from the same failed z=0.005 relabel pattern.

Recommended next source direction:

1. Bisection/ramp source mining between `z=0.0024` and `z=0.005`.
2. Require seed-5 `x=0.0` support survival first, not just `x=0.08` motion.
3. Only use traces as positive labels when the source itself passes the short
   support gate under the corrected bridge.

Robot validation remains blocked.
