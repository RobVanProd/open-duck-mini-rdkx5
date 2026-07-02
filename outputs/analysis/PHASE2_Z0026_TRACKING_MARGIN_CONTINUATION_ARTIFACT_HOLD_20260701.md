# Phase 2 z=0.0026 Tracking-Margin Continuation Artifact Hold

recorded_at: `2026-07-01T23:58:00Z`

status: `HOLD_COLAB_ARTIFACT_UNRECOVERED`

## Executive Summary

A narrow continuation was launched from the preserved teacher-continuity 81920
checkpoint with slightly stronger actuator-tracking pressure and modestly
stronger forward-progress pressure.

The Colab exec transcript reports that training and the compact checkpoint sweep
returned successfully, selecting the 122880-step ONNX as
`best_available_but_not_promoted`. However, the Colab session disappeared before
the artifact bundle could be downloaded. The sweep JSON, checkpoint directories,
ONNX files, and training summary for this continuation were not recovered.

This run is therefore not authoritative evidence for promotion or for changing
the Phase 2 training direction. Treat it as a Colab transport/artifact hold, not
as a model result.

No robot test, SSH, deploy, grounded replay, or runtime behavior change was
performed.

## Launch Summary

- session: `open-duck-a100-phase2-z0026-tc2`
- workflow: `phase2-z002-teacher-continuity`
- restore checkpoint: `/content/phase2_restore_tc_81920/2026_07_01_224518_81920`
- local restore tar sha256: `032ff4e448ab832a74a0872e3edc92e0f505d6035ddaecf381410d89fcca9263`
- terrain hfield z scale: `0.0026`
- num timesteps: `40960`
- actuator tracking scale: `-0.0075`
- forward progress scale: `4.8`
- command progress scale: `3.8`
- command progress shortfall scale: `-11`
- artifact checkpoint mode: `all`
- exec log: `outputs/analysis/colab_cli/open-duck-a100-phase2-z0026-tc2-phase2-z002-teacher-continuity-20260701T232551Z/exec_remote.log`

## Transcript Evidence

The local exec transcript contains:

```text
<<< returncode 0
CANDIDATE_SELECTED_CHECKPOINT best_available_but_not_promoted HOLD_PARTIAL_CANDIDATE_CHECKPOINT /content/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260701T232622Z_gpu/2026_07_01_233827_122880.onnx
PHASE2_POST_TRAINING_GATES_SKIPPED /content/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260701T232622Z_gpu/2026_07_01_233827_122880.onnx
COLAB_CLI_ARTIFACT /content/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T232618Z_artifacts.tar.gz
COLAB_EXEC_REMOTE_RETURNCODE 0
```

The helper then reported:

```text
REMOTE_BUNDLE_MISSING /content/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T232618Z_artifacts.tar.gz
```

Immediately afterward, the Colab session was lost:

```text
[colab] Session 'open-duck-a100-phase2-z0026-tc2' appears to be lost (404/401). Cleaning up.
```

## Decision

`HOLD_COLAB_ARTIFACT_UNRECOVERED`

The continuation is not usable as a promoted candidate, checkpoint source, or
canonical result because the required artifacts were not recovered.

## Next Recommendation

Repeat the continuation only with artifact capture that does not depend on the
session surviving after the training command returns. The current trustworthy
continuation point remains the preserved 81920 checkpoint recorded in:

`outputs/analysis/PHASE2_Z0026_TEACHER_CONTINUITY_A100_ALL_CHECKPOINTS_DECISION_20260701.md`
