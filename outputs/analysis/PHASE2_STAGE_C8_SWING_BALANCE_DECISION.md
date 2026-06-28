# Phase 2 Stage C8 Swing-Balance Decision

status: `HOLD_STAGE_C8_SWING_BALANCE_TOO_STRONG`

## Scope

Offline sim/training only. No robot, SSH, deploy, grounded replay, runtime
behavior change, or policy overwrite was performed.

## Why

C7 trace comparison showed a low-progress seed that almost never left double
support and never swung the left foot. C8 tested the new default-off
`forward_swing_balance` hook to see whether penalizing one-sided accumulated
swing usage would reduce that collapse.

## Recipe

Warm-start:

```text
outputs/phase2_domain_randomization/stage_c3_terrain_z002_contact_from_c2_gpu/smoke_20260628T121159Z_gpu/2026_06_28_081839_245760
```

Training artifact:

```text
outputs/phase2_domain_randomization/stage_c8_terrain_z002_swing_balance_from_c3_gpu/smoke_20260628T142552Z_gpu
```

Key settings:

```text
restore_policy_kl_scale: 1.25
forward_single_support_scale: 0.30
forward_contact_transition_scale: 0.20
forward_double_support_dwell_scale: -0.05
forward_swing_clearance_scale: -0.0005
forward_swing_clearance_target_m: 0.020
forward_swing_balance_scale: -0.05
forward_swing_balance_grace_steps: 20
target_rate_scale: -0.03
actuator_tracking_scale: -0.05
terrain_hfield_z_scale: 0.002
num_timesteps: 105360
ppo_num_evals: 4
```

Training completed:

```text
status: PASS_SMOKE_RUN
elapsed_s: 408.45
terrain XML restored: true
```

## Screen

Focused seed-0 terrain screen:

```text
outputs/analysis/PHASE2_STAGE_C8_TERRAIN_Z002_SCREEN_CPU.md
outputs/analysis/phase2_stage_c8_terrain_z002_screen_cpu.json
```

| checkpoint | status | tracking p95 | track ratio | velocity excess | min swing peak | single support | double support |
|---|---|---:|---:|---:|---:|---:|---:|
| `c8_0` | `HOLD_CANDIDATE_TRACKING` | 0.2046 | 0.4061 | 0.0000 | 0.0165 m | 20.8% | 79.2% |
| `c8_35120` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1846 | 0.1819 | 0.0000 | 0.0084 m | 6.8% | 93.2% |
| `c8_70240` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1706 | 0.1174 | 0.0000 | 0.0061 m | 4.4% | 95.6% |
| `c8_105360` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1676 | 0.0747 | 0.0000 | 0.0056 m | 2.0% | 98.0% |

## Interpretation

The `forward_swing_balance_scale=-0.05` setting is too strong or is applying
pressure in the wrong order for this gait. It does not rescue the C7 seed-4
failure mode. Instead, it removes the useful early C7 transient: C7 `35120`
passed seed 0 with track ratio `0.2606`, while C8 `35120` held at `0.1819` and
lower swing/support metrics.

The useful part of this result is diagnostic:

- the hook executes and has behavioral leverage,
- this weight pushes toward lower motion rather than balanced stepping,
- therefore the next attempt should not simply increase balance pressure.

## Next

Do not promote C8 and do not run it on hardware.

Keep the hook available, but only use it with a staged target that first
preserves motion, or with a much weaker balance scale. The stronger next branch
is still to change the target manifold: higher-clearance/alternating-step
demonstrations or a hard step-advance constraint, then gate-selected checkpoint
screening.
