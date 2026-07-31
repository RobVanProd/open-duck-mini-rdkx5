# Phase 2 z=0.0026 A100 Teacher-Continuity Runtime Hold

timestamp_utc: `2026-07-02T04:18:00Z`
branch: `codex/live-oracle-dagger-phase-student`
head_before_report: `114d0a1834a9cabc7d2e22f491d7f6001574f334`

## Executive Summary

Gate result: `HOLD_A100_RUNNER_START_NO_SENTINEL`

The A100/Colab runtime is usable for device import, package import, and policy/sim contract audit, but the `phase2-z002-teacher-continuity` training runner repeatedly disappears after runner startup and before the first export. No promotable ONNX was recovered from the valid polling-path runs.

This is an offline runtime/workflow blocker, not a robot result. No robot, SSH, deploy, or grounded replay was performed.

## Attempts

| attempt | session | mode | deps | shape | result | artifact |
|---|---|---|---|---|---|---|
| exec medium | `open-duck-a100-startup` | `colab exec` | reused | 8 envs, 20480 steps | train + 1s sweep returned `0`, then session/file API lost | no ONNX recovered |
| poll medium | `open-duck-a100-poll` | detached poll | skipped on fresh runtime | 8 envs, 20480 steps | `HOLD_SMOKE_RUN`, missing `playground` package | partial audit only |
| poll medium deps | `open-duck-a100-poll` | detached poll | installed | 8 envs, 20480 steps | `HOLD_REMOTE_NO_SENTINEL` | no ONNX |
| poll medium warm | `open-duck-a100-poll` | detached poll | reused | 8 envs, 20480 steps | `HOLD_REMOTE_NO_SENTINEL` | no ONNX |
| poll small warm | `open-duck-a100-poll` | detached poll | reused | 4 envs, 8192 steps | `HOLD_REMOTE_NO_SENTINEL` | no ONNX |

## Common Failure Signature

The valid polling runs all reached:

- JAX/JAXlib: `0.7.2`
- backend/device: `gpu` / `CudaDevice(id=0)`
- `has_device_put_replicated`: `True`
- MuJoCo contract audit: completed
- runner task: `rough_terrain_backlash`
- observation size: `101`
- restore-policy KL enabled
- behavior prior enabled
- corrected actuator bridge enabled

They then stopped after:

```text
Enabled restore-policy KL loss: scale=7.5 ...
Skipping checkpoint/export at step 0; export_min_step=1
```

The smoke manifest remained at:

```text
status = RUNNING
returncode = None
onnx_exports = None
elapsed_s ~= 240-270
```

The remote PID was gone, the session reported idle, and no `.exit` sentinel was written.

The only stderr signal was:

```text
RuntimeWarning: overflow encountered in cast
```

No Python traceback was captured.

## Interpretation

The `colab exec` path can run the medium command to completion but is not trustworthy for artifact recovery: the file API/session disappeared before download.

The detached polling path recovers artifacts correctly on ordinary failures, but this recipe disappears at runner startup before a checkpoint is exported. Scaling from 8 envs / 20480 steps down to 4 envs / 8192 steps did not change the failure point, so this is not simply medium-run size.

Treat this as a runtime isolation hold around the Phase 2 teacher-continuity runner shape on Colab A100. Do not promote or gate any candidate from these attempts.

## Recommended Next Step

Stop launching longer A100 runs for this recipe until the runner-start disappearance is isolated. The next useful test is a narrower matrix that toggles one feature at a time on the same polling path:

1. restore checkpoint only, no bridge, no behavior prior
2. restore checkpoint + bridge
3. restore checkpoint + behavior prior
4. restore checkpoint + bridge + behavior prior
5. same as failing recipe but CPU platform for the runner, if feasible

The earlier startup matrix proved these flags can start in short smoke runs; the missing case is whether the full runner enters the first PPO update/export without disappearing.
