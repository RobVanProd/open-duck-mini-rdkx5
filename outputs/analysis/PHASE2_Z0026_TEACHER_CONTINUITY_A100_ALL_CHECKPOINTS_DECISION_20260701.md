# Phase 2 z=0.0026 Teacher-Continuity A100 All-Checkpoints Decision

recorded_at: `2026-07-01T22:56:00Z`

status: `HOLD_PARTIAL_CANDIDATE_TRACKING`

## Executive Summary

The `phase2-z002-teacher-continuity` recipe was rerun on A100 with
`--artifact-checkpoint-mode all` after the previous run selected an intermediate
checkpoint but only preserved the latest checkpoint directory.

The rerun succeeded and preserved all Orbax checkpoint directories. The compact
checkpoint sweep again selected the 81920-step checkpoint as the best available
candidate, but it is still not promotable: x=0.08 has meaningful in-envelope
forward motion, yet misses the strict corrected-bridge pitch-chain tracking gate.

No robot test, SSH, deploy, grounded replay, or runtime behavior change was
performed.

## Run

- session: `open-duck-a100-phase2-z0026-tc2`
- workflow: `phase2-z002-teacher-continuity`
- hardware: A100 / CUDA
- JAX pin: `0.7.2`
- artifact mode: `all`
- terrain hfield z scale: `0.0026`
- post-training full gates: skipped intentionally; compact checkpoint sweep ran
- artifact bundle: `outputs/analysis/colab_cli/open-duck-a100-phase2-z0026-tc2-phase2-z002-teacher-continuity-20260701T223440Z/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T223519Z_artifacts.tar.gz`
- artifact sha256: `feb5ed2f488451cf27e71c146a8da6ff112f980aaf2105bbdb347867244865c2`

## Checkpoint Preservation

The bundle preserved all checkpoint directories:

- `2026_07_01_224423_40960`
- `2026_07_01_224518_81920`
- `2026_07_01_224539_122880`

Selected continuation checkpoint:

`outputs/analysis/colab_cli_downloads/extracted/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T223519Z/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T223519Z/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260701T223737Z_gpu/2026_07_01_224518_81920`

Selected ONNX:

`outputs/analysis/colab_cli_downloads/extracted/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T223519Z/open_duck_colab_cli_phase2-z002-teacher-continuity_20260701T223519Z/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260701T223737Z_gpu/2026_07_01_224518_81920.onnx`

## Compact Sweep Results

commands: `[0.0, 0.08]`

bridge mode: `fitted`

duration: `1.0s`

velocity envelope: `[2.0, 3.25] rad/s`

| checkpoint | command_x | status | max pitch vel p95 | envelope | max tracking p95 | track ratio | mean local vx |
|---|---:|---|---:|---|---:|---:|---:|
| 40960 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 1.0737 | below | 0.1941 | NA | 0.0063 |
| 40960 | 0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.5263 | below | 0.2181 | 0.2128 | 0.0170 |
| 81920 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 1.1464 | below | 0.1946 | NA | 0.0057 |
| 81920 | 0.08 | `HOLD_CANDIDATE_TRACKING` | 1.4887 | below | 0.2170 | 0.3008 | 0.0241 |
| 122880 | 0.00 | `PASS_CANDIDATE_SIM_GATE` | 1.1247 | below | 0.1949 | NA | 0.0056 |
| 122880 | 0.08 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 1.5483 | below | 0.2174 | 0.2187 | 0.0175 |

## Decision

`HOLD_PARTIAL_CANDIDATE_TRACKING`

The 81920 checkpoint is a useful continuation point, not a promoted robot
candidate. It restores meaningful z=0.0026 forward motion under the corrected
bridge while staying well below the measured velocity envelope, but pitch-chain
tracking p95 remains above the strict `0.20 rad` gate.

## Next Recommendation

Continue from the preserved 81920 checkpoint with a narrow tracking-margin
follow-up that preserves teacher-continuity and forward motion. Do not return to
the prior support-only recipe; that recipe made the policy safer but too slow.
