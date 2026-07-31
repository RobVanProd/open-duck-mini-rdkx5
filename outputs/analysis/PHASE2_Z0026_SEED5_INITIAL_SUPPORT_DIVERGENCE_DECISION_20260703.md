# Phase 2 z=0.0026 Seed-5 Initial Support Divergence Decision

status: `HOLD_Z0026_INITIAL_SUPPORT_MANIFOLD`

## Executive Summary

The z=0.0026 seed-5 failure is now isolated before meaningful policy action:
seed 5 starts outside the parent policy's support/contact manifold at tick 0.
The failing rollout begins with no foot contact and a very different right-leg
posture, while the policy sends nearly the same initial target as the passing
seed-0 rollout. The failure is therefore not fixed by another scalar
anti-reverse/base-height penalty.

Passive reset settling is also not a safe workaround. Adding
`--reset-settle-ticks 25` makes seed 5 fail faster and harder.

## Source Artifacts

```text
outputs/analysis/PHASE2_Z0026_TC81920_SEED0_VS_SEED5_TRACE.md
outputs/analysis/phase2_z0026_tc81920_seed0_vs_seed5_trace.json
outputs/analysis/phase2_z0026_tc81920_seed0_vs_seed5_trace/tc81920/seed_000/trace.jsonl
outputs/analysis/phase2_z0026_tc81920_seed0_vs_seed5_trace/tc81920/seed_005/trace.jsonl

outputs/analysis/PHASE2_Z0026_TC81920_SEED5_RESETSETTLE25_SHORT.md
outputs/analysis/phase2_z0026_tc81920_seed5_resetsettle25_short.json
```

Policy under test:

```text
outputs/analysis/colab_cli_downloads/extracted/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T223519Z/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T223519Z/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260701T223737Z_gpu/2026_07_01_224518_81920.onnx
```

Eval setup:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.0026
command_x: 0.08
bridge: outputs/analysis/actuator_response_fit_corrected_knee.json
jax_platform: cpu
duration: 2.0 s
```

## Short Screen Result

| seed | status | samples | termination | mean vx | track ratio | base min | max pitch vel p95 | p95 vel excess | tracking p95 | single support | double support |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TRACKING` | 100 | duration_complete | 0.0250 | 0.3128 | 0.1519 | 1.7138 | 0.0000 | 0.2129 | 13.0000 | 87.0000 |
| 5 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 65 | fall_or_nan | -0.2279 | -2.8483 | 0.0667 | 1.8401 | 0.0000 | 0.2022 | 9.2308 | 83.0769 |

Both rollouts stay inside the corrected velocity envelope. The difference is
not actuator over-rate.

## First Divergence

The first divergence occurs at tick 0.

| field | seed 0 | seed 5 | interpretation |
|---|---:|---:|---|
| foot contact | `[0, 1]` | `[0, 0]` | seed 0 starts with right contact; seed 5 starts airborne |
| left foot z | 0.0249 m | 0.0235 m | similar |
| right foot z | -0.0020 m | 0.0553 m | seed 5 right foot starts about 5.7 cm higher |
| base height | 0.1519 m | 0.1498 m | similar base height at reset |
| local vx | -0.0374 m/s | +0.0373 m/s | seed 5 initially moves forward, then reverses |
| action L2 delta | NA | 0.2198 | policy action only mildly differs at reset |
| sent-target L2 delta | NA | 0.0436 | sent targets are effectively the same |
| actual-position L2 delta | NA | 0.8789 | robot state is substantially different |

Largest tick-0 joint-position differences, seed5 minus seed0:

| joint | delta rad |
|---|---:|
| right_ankle | +0.5354 |
| right_knee | +0.4809 |
| left_ankle | -0.4302 |
| right_hip_pitch | -0.1951 |
| left_hip_pitch | +0.1713 |

The policy is receiving a very different initial support/posture state but is
not sending a corresponding early recovery target.

## Timing

| divergence | first tick |
|---|---:|
| foot contact differs | 0 |
| actual joint-position L2 > 0.5 | 0 |
| local-vx difference > 0.1 m/s | 1 |
| seed-5 local vx becomes negative | 10 |
| action L2 > 0.5 | 35 |
| sent-target L2 > 0.5 | never during shared trace |
| base-height difference > 0.02 m | 60 |

This ordering is important: the support-state mismatch precedes the reverse
event and the height collapse. It is not a late-action saturation or late
tracking error.

## Reset-Settle Probe

Adding `--reset-settle-ticks 25` is not a solution:

| seed | reset settle | status | samples | mean vx | track ratio | base min | p95 vel excess | single support | double support |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 5 | 25 ticks | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 18 | -0.7045 | -8.8068 | 0.0768 | 0.0000 | 27.7778 | 72.2222 |

Passive settling drives the seed farther from the usable support manifold.
Do not change the gate to include reset-settle as a silent workaround.

## Decision

The current z=0.0026 seed-5 blocker is:

```text
HOLD_Z0026_INITIAL_SUPPORT_MANIFOLD
```

The parent policy is 7/8 at z=0.0026, but seed 5 starts from an unsupported
right-leg/contact state that the policy does not recognize or correct. The next
branch should target this state manifold directly.

Recommended next branch:

```text
reset/contact-state recovery for seed-5-like initial states
```

Valid directions:

- on-policy/live-oracle relabeling on seed-5 visited states starting at tick 0,
- reset distribution augmentation that includes airborne/no-contact support
  states like seed 5,
- a recovery head or gated behavior prior conditioned on early contact/posture,
- direct comparison against the seven passing seeds to mine recoverable
  support-transfer actions.

Closed directions:

- another scalar anti-reverse/base-height escalation,
- passive reset-settle gate changes,
- promotion of the 40960/81920/122880 repair checkpoints,
- robot validation from this branch.
