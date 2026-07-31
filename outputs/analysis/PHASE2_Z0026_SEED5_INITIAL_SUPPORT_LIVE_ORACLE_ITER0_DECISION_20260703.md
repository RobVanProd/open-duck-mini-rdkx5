# Phase 2 z=0.0026 Seed-5 Initial-Support Live-Oracle Smoke Decision

status: `HOLD_LIVE_ORACLE_RESET_REPAIR_SMOKE_FAILED`

This was an offline diagnostic smoke only. It did not SSH, deploy, run robot
tests, change runtime behavior, or run grounded replay.

## Inputs

- parent policy: `outputs/analysis/colab_cli_downloads/extracted/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T223519Z/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T223519Z/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260701T223737Z_gpu/2026_07_01_224518_81920.onnx`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain heightfield z scale: `0.0026`
- platform: local CPU
- live-oracle iteration: `0`
- targeted seed: `5`

## What Ran

The parent checkpoint was rolled out on the known bad z=0.0026 seed-5 reset
state for both:

- `x=0.08`, relabeled with the `source_vx_blend` oracle
- `x=0.0`, relabeled with a `zero_action` oracle to preserve command semantics

Those relabeled states were aggregated with the existing z=0.0024 positive
source manifest and used for a small phase-modulated behavior-cloning smoke
student.

## Data Iteration

Artifact:

```text
outputs/analysis/PHASE2_Z0026_SEED5_INITIAL_SUPPORT_LIVE_ORACLE_ITER0.md
```

Status:

```text
PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY
```

The iteration produced an aggregate manifest:

```text
outputs/analysis/phase2_z0026_seed5_initial_support_live_oracle_iter0/live_oracle_dagger_aggregate_manifest.json
```

Aggregate contents:

- `6123` samples total
- `6000` samples from the original z=0.0024 positive source entries
- `65` relabeled x=0.08 seed-5 failure-state samples
- `58` relabeled x=0.0 seed-5 failure-state samples

Important nuance: the two new entries are relabeled actions on bad reset/failure
states, not successful trace behavior.

## Student Fit Smoke

Artifact:

```text
outputs/analysis/PHASE2_Z0026_SEED5_INITIAL_SUPPORT_LIVE_ORACLE_ITER0_STUDENT.md
```

Status:

```text
PASS_PHASE_MODULATED_BC_FIT_SMOKE
```

Fit metrics:

```text
samples:             6123
MAE:                 0.007024
p95_abs_error:       0.022539
max_abs_error:       0.389182
target_rate_p95:     1.751672 rad/s
target_rate_max:     2.279135 rad/s
ONNX p95 error:      0.00000012
ONNX max error:      0.00000041
```

The supervised fit and ONNX export were clean, but rollout behavior is the
decision criterion.

## Short Rollout Screens

### x=0.08, seed 5

Artifact:

```text
outputs/analysis/PHASE2_Z0026_SEED5_INITIAL_SUPPORT_LIVE_ORACLE_ITER0_STUDENT_X008_SEED5_SHORT.md
```

Result:

```text
status:              HOLD_CANDIDATE_FALL_OR_TERMINATION
samples:             57
termination:         fall_or_nan
mean_vx:             -0.2527 m/s
track_ratio:         -3.1587
base_height_min:     0.0751 m
p95_vel_excess:      0.0000
max_tracking_p95:    0.1880 rad
single_support:      10.5263 %
double_support:      84.2105 %
```

The smoke student did not repair the known moving-command seed-5 failure. It
fell earlier than the parent and still moved backward.

### x=0.0, seed 5

Artifact:

```text
outputs/analysis/PHASE2_Z0026_SEED5_INITIAL_SUPPORT_LIVE_ORACLE_ITER0_STUDENT_X000_SEED5_SHORT.md
```

Result:

```text
status:              HOLD_CANDIDATE_FALL_OR_TERMINATION
samples:             43
termination:         fall_or_nan
mean_vx:             -0.3436 m/s
base_height_min:     0.0576 m
p95_vel_excess:      0.1776
max_vel_excess:      0.8481
max_tracking_p95:    0.2326 rad
single_support:      6.9767 %
double_support:      81.3953 %
```

The smoke student also broke x=0.0 command preservation and introduced
corrected-envelope velocity excess. This is a hard stop for this repair shape.

## Decision

Do not scale this student and do not spend A100 time on this exact relabel
recipe. The live-oracle data pass was useful, but the naive small bad-reset
relabel plus phase-modulated BC smoke made the target seed worse and degraded
the standing command.

The failure is still best read as an initial-support/reset-manifold problem:
the current Playground reset can produce seed-5-like no-contact states outside
the passing support manifold, and this smoke did not teach a deployable recovery
action for that state.

## Next Branch

The next branch should not be another scalar reward tweak or a larger version
of this failed smoke. It should first choose one of these mechanisms:

1. Audit and, if justified by the real robot start protocol, constrain the reset
   distribution so the sim gate starts from physically grounded home/support
   states rather than airborne no-contact states.
2. Build a support-recovery oracle that actually survives seed-5-like no-contact
   resets before relabeling those states.
3. Add reset/contact-state augmentation only if the augmented states are labeled
   by a recovery source that clears the short screen.

No robot validation is allowed from this branch.
