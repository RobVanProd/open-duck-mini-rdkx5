# Phase 2 Stage C4 Clearance Decision

status: `HOLD_STAGE_C4_CLEARANCE_OVERDRIVES_GAIT`

## Scope

Offline sim/training only. No robot, SSH, deploy, grounded replay, or runtime
behavior change was performed.

## Inputs

C4 used the new default-off `forward_swing_clearance` reward hook introduced in:

```text
outputs/analysis/PHASE2_STAGE_C4_CLEARANCE_REWARD_PLUMBING.md
```

Warm-start:

```text
outputs/phase2_domain_randomization/stage_c3_terrain_z002_contact_from_c2_gpu/smoke_20260628T121159Z_gpu/2026_06_28_081839_245760
```

Baseline C3 short screen:

```text
tracking p95: 0.2046 rad
track ratio: 0.4061
velocity excess: 0.0000 rad/s
min swing peak lift: 0.0165 m
single support: 20.8%
double support: 79.2%
```

## C4 Run

Training artifact:

```text
outputs/phase2_domain_randomization/stage_c4_terrain_z002_clearance_from_c3_gpu/smoke_20260628T124154Z_gpu
```

Recipe delta from C3:

```text
forward_swing_clearance_scale: -0.05
forward_swing_clearance_target_m: 0.03
forward_swing_clearance_huber_delta: 0.01
```

Training completed successfully:

```text
status: PASS_SMOKE_RUN
elapsed_s: 493.73
terrain XML restored: true
```

Short terrain screen:

```text
outputs/analysis/PHASE2_STAGE_C4_TERRAIN_Z002_SCREEN_CPU.md
outputs/analysis/phase2_stage_c4_terrain_z002_screen_cpu.json
```

| policy | status | samples | tracking p95 | track ratio | velocity excess | min swing peak | single support | double support |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `c4_0` | `HOLD_CANDIDATE_TRACKING` | 250 | 0.2046 | 0.4061 | 0.0000 | 0.0165 m | 20.8% | 79.2% |
| `c4_245760` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | 0.4266 | -6.0028 | 3.2400 | 0.0193 m | 81.8% | 9.1% |

## Interpretation

The clearance term changed behavior, but too aggressively. The final C4 policy
increased single-support time and peak lift slightly, but destroyed the gait:
it fell early, moved backward, and exceeded the corrected velocity envelope.

This is not a terrain candidate and should not be promoted.

## C4b Weak Retry

A weaker follow-up was attempted:

```text
outputs/phase2_domain_randomization/stage_c4b_terrain_z002_clearance_weak_from_c3_gpu/smoke_20260628T125456Z_gpu

forward_swing_clearance_scale: -0.005
forward_swing_clearance_target_m: 0.025
```

It did not reach training:

```text
status: HOLD_SMOKE_RUN
returncode: 1
elapsed_s: 33.02
failure: rocblas_status_internal_error during JAX evaluator reset
```

Treat C4b as a local ROCm/backend hold, not a policy result.

## Next

The next useful C-stage attempt should use a gentler or staged clearance
curriculum, likely with:

- lower initial clearance scale than C4,
- shorter staged update and early checkpoint screens,
- restore-policy/behavior prior pressure to preserve the C3 gait,
- corrected-envelope gate after each checkpoint,
- and CPU/CUDA fallback if local ROCm repeats `rocblas_status_internal_error`.
