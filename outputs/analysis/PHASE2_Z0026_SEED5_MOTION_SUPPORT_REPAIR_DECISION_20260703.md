# Phase 2 z=0.0026 Seed-5 Motion-Support Repair Decision

status: `HOLD_Z0026_REPAIR_DID_NOT_RECOVER_SEED5`

This was an offline Colab A100 training run plus local CPU corrected-bridge
screen. It did not run robot tests, SSH, deploy, grounded replay, or runtime
behavior changes.

## Purpose

The current z=0.0026 blocker was isolated to moving-command support transfer:
the preserved teacher-continuity `81920` checkpoint passed 7/8 full x=0.08
seeds, with seed 5 failing by reverse velocity and base-height collapse while
remaining inside the corrected actuator envelope.

This run tested the narrow repair recipe from:

```text
outputs/analysis/PHASE2_Z0026_SEED5_MOTION_SUPPORT_NEXT_RECIPE.md
```

## Remote Training

- session: `open-duck-a100-phase2-z0026`
- workflow: `phase2-z002-teacher-continuity`
- hardware: Colab `A100`
- JAX/JAXLIB: `0.7.2`
- terrain: `rough_terrain_backlash`, hfield z-scale `0.0026`
- restore checkpoint: `outputs/analysis/phase2_restore_checkpoints/phase2_z0026_teacher_continuity_81920`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- pushed/robot/deploy/grounded replay: `false`

Training completed and exported ONNX checkpoints:

| step | sha256 |
|---:|---|
| 40960 | `fded6556135ce795c4b31e51dd4faac5aba0304d248626f2526733f43ffae88e` |
| 81920 | `75b4b88226b9d0662c62e6e16ea46a638d205553caf4fe977c60dfaceaed6372` |
| 122880 | `ce582e7d037acdf11ae1ea84676bc764428216102c58cb433ac3ca30829cd659` |

Artifact bundle:

```text
outputs/analysis/colab_cli/open-duck-a100-phase2-z0026-phase2-z002-teacher-continuity-20260703T013212Z/manual_download/open_duck_colab_cli_phase2-z002-teacher-continuity_20260703T013239Z_artifacts.tar.gz
sha256: d105b43aac906649117281aef3522d2591755fb8934280587c607eec1b42ad20
```

The remote CPU checkpoint sweep was stopped after the local decisive seed-5
screen below showed no checkpoint was promotable. The Colab session was then
terminated to avoid spending more compute.

## Local Seed-5 Screen

Command:

```text
rough_terrain_backlash, z=0.0026, command_x=0.08, seed=5, duration=2s,
corrected fitted bridge, CPU, trace enabled
```

Artifact:

```text
outputs/analysis/PHASE2_Z0026_SEED5_MOTION_SUPPORT_REPAIR_SEED5_SHORT.md
outputs/analysis/phase2_z0026_seed5_motion_support_repair_seed5_short.json
```

| checkpoint | status | samples | mean vx | track ratio | base min | pitch vel p95 | vel excess | tracking p95 | single support | double support |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 40960 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 65 | -0.2219 | -2.7736 | 0.0733 | 1.7289 | 0.0000 | 0.2032 | 12.31% | 84.62% |
| 81920 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 65 | -0.2262 | -2.8270 | 0.0687 | 1.7510 | 0.0000 | 0.2034 | 13.85% | 81.54% |
| 122880 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 64 | -0.2184 | -2.7300 | 0.0806 | 1.7437 | 0.0000 | 0.2019 | 12.50% | 81.25% |

## Latest Checkpoint Trace

Artifact:

```text
outputs/analysis/PHASE2_Z0026_SEED5_MOTION_SUPPORT_REPAIR_122880_TRACE_ANALYSIS.md
```

Trace status: `REVERSE_HEIGHT_COLLAPSE`

- first reverse: tick `10` / `0.20s`
- first low height: tick `62` / `1.24s`
- first done: tick `63` / `1.26s`
- contact counts: `(1,1)` double support `52/64`, `(0,0)` flight `4/64`
- max pitch-chain sent target velocity p95: `1.7437 rad/s`
- corrected velocity excess: `0.0`

## Decision

`HOLD_Z0026_REPAIR_DID_NOT_RECOVER_SEED5`

The narrow anti-reverse/base-height repair did not change the failure surface:
all exported checkpoints still fail the exact seed-5 z=0.0026 x=0.08 screen by
reverse-height collapse, with no corrected-envelope velocity excess.

Do not promote these checkpoints and do not run robot validation.

## Next Recommendation

Stop this narrow scalar repair direction. The repeated seed-5 failure is now a
state/contact-manifold problem: the policy remains double-support dominant,
drifts backward early, then collapses in height while staying in envelope.

Next work should inspect or alter the seed-5 state/contact manifold directly
rather than increasing the same scalar penalties:

- compare the passing z=0.0026 seeds against seed 5 at ticks 0-65;
- identify the first divergent contact/support variable before tick 10;
- test an on-policy/live-oracle correction on seed-5 visited states, or a
  state-conditioned support transfer rule, before spending another A100 run.
