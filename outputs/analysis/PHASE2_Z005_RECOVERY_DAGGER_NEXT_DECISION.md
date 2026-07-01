# Phase 2 z=0.005 Recovery DAgger Next Decision

status: `PASS_Z005_RECOVERY_DAGGER_NEXT_STEP_DEFINED`

This is an offline decision artifact. It did not run robot tests, SSH, deploy,
grounded replay, PPO training, or runtime behavior changes.

## Current Hold

Phase 2 remains blocked at:

```text
HOLD_PHASE2_STAGE_Z005_SUPPORT
```

The current command-gated Phase A2 candidate remains valid at `z=0.002`, but
`z=0.005` no-push terrain still fails on seed 5 in both `x=0.08` and `x=0.0`.

## Latest Closed Branch

The seed-5 z=0.005 composite recovery BC smoke is closed:

```text
outputs/analysis/PHASE2_A2_SEED5_Z005_COMPOSITE_RECOVERY_BC_SMOKE_DECISION.md
status: HOLD_COMPOSITE_RECOVERY_BC_CLOSED_LOOP_UNSTABLE
```

It fit the 141-sample composite manifest offline, but failed the short
closed-loop seed-5 z=0.005 support gate after 44 samples with:

| metric | value |
|---|---:|
| max sent target p95 | `5.2400 rad/s` |
| corrected velocity excess | `3.2400 rad/s` |
| max pitch tracking p95 | `0.3727 rad` |
| max action saturation | `65.9091%` |

That result closes one-shot fixed BC on the tiny recovery manifest. Do not use
the smoke ONNX as a candidate, parent, or training warm start.

## Surviving Source Evidence

The corrected z=0.0024 source remains the best available terrain source:

```text
outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json
dataset_id: d8498b665c201936
entries: 8
samples: 6000
```

It is in-envelope and BC-ready, but it is not itself z=0.005 evidence. The
z=0.005 seed-5 collapse is therefore a recovery/on-policy support problem, not
a solved source problem.

## Next Authorized Offline Step

Run a bounded live/on-policy recovery DAgger iteration from the Phase A2
candidate, not from the failed smoke ONNX:

```text
student:
  policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx

teacher/base source:
  outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json

task:
  rough_terrain_backlash

terrain:
  z=0.005

bridge:
  outputs/analysis/actuator_response_fit_corrected_knee.json
```

The first iteration should be deliberately small:

1. Roll out only the failing seed-5 z=0.005 support cases first:
   `x=0.0` and `x=0.08`, full-observation traces, corrected bridge, CPU-safe
   platform.
2. Relabel the student-visited pre-collapse states from the corrected z=0.0024
   source/oracle.
3. Aggregate with the 6000-sample z=0.0024 source, not with the failed 141-row
   composite smoke candidate.
4. Train one small phase/command-modulated BC student.
5. Immediately run the same short seed-5 z=0.005 gates before any 8-seed or
   Colab scaling.

## Hard Stops

Stop the branch and write a decision artifact if either short seed-5 gate shows:

- any corrected pitch-chain velocity excess,
- `max_pitch_tracking_p95 > 0.20 rad`,
- fall/termination before 2 seconds,
- mean local `vx < -0.02 m/s` at `x=0.0`,
- or action saturation above `10%`.

Passing a supervised fit is not enough. The short closed-loop gate is the only
thing that can authorize scaling to the full 8-seed z=0.005 no-push gate.

## Forbidden Next Moves

Do not:

- train from scratch,
- continue one-shot fixed BC on the 141-sample composite manifest,
- promote the composite smoke ONNX,
- launch another scalar support/swing reward run as the next step,
- use historical old-bridge source-VX manifests,
- run robot validation, SSH, deploy, or grounded replay.

## Decision

The next aligned work is live/on-policy z=0.005 recovery DAgger with immediate
short closed-loop gates. The Phase 2 goal remains active and incomplete until a
deployable warm-started candidate clears the corrected z=0.005 gates and the
z=0.002 regression gates remain clear.
