# Phase 2 Stage C6 Transition Clearance Decision

status: `HOLD_STAGE_C6_TRANSITION_PRESSURE_RETREATS_TO_DOUBLE_SUPPORT`

## Scope

Offline sim/training only. No robot, SSH, deploy, grounded replay, or runtime
behavior change was performed.

## Why

C5a showed that weak clearance pressure plus strong restore-policy KL can lower
tracking error, but the policy satisfies the objective by retreating into
double support and low forward progress. C6 tested whether stronger
single-support/contact-transition pressure with only very weak clearance
pressure would preserve the C3 gait while improving rough-terrain clearance.

## Backend Note

C6 used the same local ROCm workaround that allowed C5a to train after the
`rocblas_status_internal_error` reset failures:

```text
XLA_FLAGS=--xla_gpu_autotune_level=0
XLA_PYTHON_CLIENT_PREALLOCATE=false
```

## Recipe

Warm-start:

```text
outputs/phase2_domain_randomization/stage_c3_terrain_z002_contact_from_c2_gpu/smoke_20260628T121159Z_gpu/2026_06_28_081839_245760
```

Training artifact:

```text
outputs/phase2_domain_randomization/stage_c6_terrain_z002_transition_clearance_from_c3_gpu/smoke_20260628T131402Z_gpu
```

Key settings:

```text
restore_policy_kl_scale: 1.25
forward_single_support_scale: 0.30
forward_contact_transition_scale: 0.20
forward_double_support_dwell_scale: -0.05
forward_double_support_dwell_grace_steps: 8
forward_swing_clearance_scale: -0.0005
forward_swing_clearance_target_m: 0.020
forward_swing_clearance_huber_delta: 0.005
target_rate_scale: -0.03
actuator_tracking_scale: -0.05
terrain_hfield_z_scale: 0.002
num_timesteps: 81920
```

Training completed:

```text
status: PASS_SMOKE_RUN
elapsed_s: 296.87
terrain XML restored: true
```

Export hashes:

```text
c6_0:     50589ffefd9fc5344d43afbb3f17fbf876e7abdd5886a547e4398f9f674a8a3c
c6_81920: f1bc974454d002f4a7978de13e9d96b3977f9ba3145a8c2f5b0597a42cc457b3
```

## Screen

```text
outputs/analysis/PHASE2_STAGE_C6_TERRAIN_Z002_SCREEN_CPU.md
outputs/analysis/phase2_stage_c6_terrain_z002_screen_cpu.json
```

| policy | status | tracking p95 | track ratio | velocity excess | min swing peak | single support | double support |
|---|---|---:|---:|---:|---:|---:|---:|
| `c6_0` | `HOLD_CANDIDATE_TRACKING` | 0.2046 | 0.4061 | 0.0000 | 0.0165 m | 20.8% | 79.2% |
| `c6_81920` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1654 | 0.0985 | 0.0000 | 0.0072 m | 4.0% | 96.0% |

## Interpretation

C6 stayed stable and inside the corrected actuator envelope, but it did not
solve the terrain/carpeting problem. The trained checkpoint reduced tracking
error by retreating further into double support and low motion:

- track ratio fell from `0.4061` to `0.0985`
- minimum swing peak fell from `0.0165 m` to `0.0072 m`
- single-support time fell from `20.8%` to `4.0%`
- double-support time rose from `79.2%` to `96.0%`

This extends the C5a finding. Stronger transition pressure and very weak
clearance pressure are still not enough when optimized through the current PPO
recipe; the policy can avoid rough-terrain risk by shuffling more conservatively
instead of lifting and advancing the feet.

## Next

Do not promote C6 and do not run it on hardware.

The next terrain branch should stop treating clearance as a small additive
touchdown cost. Candidate directions:

- gate-selected training on terrain metrics instead of reward-only checkpoint
  selection,
- a hard minimum swing-clearance / step-advance constraint during commanded
  motion,
- a teacher or target-source update that explicitly contains higher-clearance
  steps,
- or a staged terrain task that starts with a command/lift target the Phase 1
  gait can satisfy before adding PPO updates.
