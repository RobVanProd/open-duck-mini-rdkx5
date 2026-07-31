# Phase 2 Stage C5a Clearance Preserve Decision

status: `HOLD_STAGE_C5A_RETREATS_TO_DOUBLE_SUPPORT`

## Scope

Offline sim/training only. No robot, SSH, deploy, grounded replay, or runtime
behavior change was performed.

## Why

C4 proved the new `forward_swing_clearance` objective has leverage, but the
first setting over-drove the gait into early fall and corrected-envelope
violation. C5a tested whether much weaker clearance pressure plus stronger
restore-policy KL could preserve the C3 gait while nudging clearance upward.

## Backend Note

Two follow-up GPU runs (`C4b`, `C5`) failed before training with:

```text
rocblas_status_internal_error during JAX evaluator reset
```

A basic JAX ROCm matmul still passed. Retrying C5a with:

```text
XLA_FLAGS=--xla_gpu_autotune_level=0
XLA_PYTHON_CLIENT_PREALLOCATE=false
```

allowed the training run to complete. Use this as the local ROCm workaround for
subsequent short training attempts unless a cleaner backend fix is found.

## Recipe

Warm-start:

```text
outputs/phase2_domain_randomization/stage_c3_terrain_z002_contact_from_c2_gpu/smoke_20260628T121159Z_gpu/2026_06_28_081839_245760
```

Training artifact:

```text
outputs/phase2_domain_randomization/stage_c5a_terrain_z002_clearance_preserve_xla_autotune0_from_c3_gpu/smoke_20260628T130026Z_gpu
```

Key settings:

```text
restore_policy_kl_scale: 2.5
forward_swing_clearance_scale: -0.001
forward_swing_clearance_target_m: 0.022
forward_swing_clearance_huber_delta: 0.005
target_rate_scale: -0.03
actuator_tracking_scale: -0.05
terrain_hfield_z_scale: 0.002
```

Training completed:

```text
status: PASS_SMOKE_RUN
elapsed_s: 390.93
terrain XML restored: true
```

## Screen

```text
outputs/analysis/PHASE2_STAGE_C5A_TERRAIN_Z002_SCREEN_CPU.md
outputs/analysis/phase2_stage_c5a_terrain_z002_screen_cpu.json
```

| policy | status | tracking p95 | track ratio | velocity excess | min swing peak | single support | double support |
|---|---|---:|---:|---:|---:|---:|---:|
| `c5a_0` | `HOLD_CANDIDATE_TRACKING` | 0.2046 | 0.4061 | 0.0000 | 0.0165 m | 20.8% | 79.2% |
| `c5a_81920` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1946 | 0.2220 | 0.0000 | 0.0086 m | 9.6% | 90.4% |

## Interpretation

C5a stayed stable and in-envelope, but it did not solve terrain. It reduced
strict tracking error below `0.20 rad`, but did so by retreating into lower
forward progress, lower swing clearance, less single support, and more double
support.

This identifies a reward loophole: a touchdown clearance penalty can be avoided
by reducing swing/transition behavior. The next C-stage attempt should keep
transition/single-support pressure active enough that the policy cannot satisfy
clearance preservation by shuffling more conservatively.

## Next

Try a short staged run with:

- the same ROCm workaround,
- moderate restore-policy KL instead of `2.5`,
- slightly stronger transition/single-support pressure than C3,
- very weak clearance pressure,
- frequent checkpoint screens.

Do not promote C5a.
