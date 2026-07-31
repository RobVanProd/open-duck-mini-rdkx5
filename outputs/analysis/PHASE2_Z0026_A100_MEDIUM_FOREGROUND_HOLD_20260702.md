# Phase 2 Z0026 A100 Medium Foreground Hold

generated_at: `2026-07-02T05:00:00Z`

## Executive Summary

- `HOLD_REMOTE_NO_SENTINEL`: the medium A100 teacher-continuity foreground run disappeared without an exit sentinel or artifact bundle.
- Foreground remote mode is sufficient for the small 4-env/8192-step probe, but not yet reliable for this 8-env/20480-step medium run.
- No deployable candidate was produced and no checkpoint from this run is promotable.

No robot test, SSH, deployment, grounded replay, or runtime behavior change was performed.

## Attempted Run

- session: `open-duck-a100-poll`
- workflow: `phase2-z002-teacher-continuity`
- candidate name: `phase2_z0026_teacher_continuity_a100_medium_foreground_probe`
- remote mode: `foreground-remote`
- requested timesteps: `20480`
- envs: `8`
- episode length: `256`
- post-training gates: skipped
- deps/audit: skipped, using the existing pinned A100 environment

The runner reached the planned command for:

`/content/open_duck_training_phase2_z002_teacher_continuity_cli/smoke_20260702T044610Z_gpu`

The local live log stopped after the planned-run configuration block. No local artifact directory, remote bundle, or exit sentinel was recovered.

## Hold Evidence

- hold status: `HOLD_REMOTE_NO_SENTINEL`
- remote log path: `/content/open_duck_colab_cli_phase2-z002-teacher-continuity_20260702T044606Z.log`
- remote exit path: `/content/open_duck_colab_cli_phase2-z002-teacher-continuity_20260702T044606Z.exit`
- remote bundle path: `/content/open_duck_colab_cli_phase2-z002-teacher-continuity_20260702T044606Z_artifacts.tar.gz`
- idle polls without exit sentinel: `5`
- local live log: `outputs/analysis/colab_cli/open-duck-a100-poll-phase2-z002-teacher-continuity-20260702T044536Z/remote_live.log`

A direct follow-up `colab console` inspection reported that session `open-duck-a100-poll` appeared lost with `404/401` and the CLI cleaned it up. A later `colab status` call still reported the named session as idle, but no medium-run artifact was recoverable through the workflow.

## Interpretation

This is a Colab workflow transport/artifact recovery hold, not evidence that the teacher-continuity recipe failed to train. The previous small foreground probe proved the same recipe can start, train briefly, export an ONNX, and download artifacts. This medium run shows the current CLI execution strategy is still unreliable at longer horizon.

Do not infer candidate quality from this attempt. There is no medium-run ONNX and no gate evidence.

## Next Recommendation

Use a more conservative remote execution strategy before spending another medium A100 run:

- keep foreground mode
- reduce the next run to a staged scale between the successful small probe and failed medium probe, such as `4 envs / 20480 steps` or `8 envs / 8192 steps`
- write frequent remote heartbeat/checkpoint files before and during training so a disappearing workflow can still distinguish runner crash from CLI/session loss
- prefer artifact creation immediately after every exported checkpoint rather than only at workflow end
