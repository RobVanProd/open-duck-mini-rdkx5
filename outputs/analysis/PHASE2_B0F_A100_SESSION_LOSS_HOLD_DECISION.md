# Phase 2 B0F A100 Session-Loss Hold

status: `HOLD_B0F_A100_SESSION_LOST`

## Purpose

Attempt the B0F push-local preserve recipe on the `open-duck-a100` CUDA session
after B0E regressed moving tracking. B0F restores the B0C rough-terrain parent
and applies frequent gentle pushes with stronger behavior preservation.

This was offline sim/training only. No robot tests, SSH, deploy, grounded
replay, runtime behavior changes, or policy overwrite were performed.

## What Was Verified

The B0F recipe itself is not syntactically or mechanically invalid:

```text
8-env tiny B0F-shaped A100 probe:  returncode 0
64-env B0F-shaped A100 probe:      returncode 0
```

The workflow was updated to use `64` envs / batch `512` after the original
`128`-env launch died before normal runner artifacts.

Pinned stack observed before the full attempts:

```text
jax/jaxlib: 0.7.2 / 0.7.2
brax: 0.14.2
mujoco/mujoco-mjx: 3.9.0 / 3.9.0
playground: 0.0.5
backend/device: gpu / cuda:0
```

## Failure

The full B0F workflow repeatedly lost the Colab session or detached remote
process after printing the training manifest and before writing normal runner
stdout/stderr, ONNX exports, or a complete artifact bundle.

Observed attempts:

```text
open-duck-a100-phase2-b0f-20260629T101300Z:
  first session disappeared during setup/extraction.

open-duck-a100-phase2-b0f-20260629T102438Z:
  --skip-deps on fresh session; dependencies missing; no policy result.

open-duck-a100-phase2-b0f-20260629T103018Z:
  deps installed; detached full run died after manifest, no exit sentinel,
  no normal runner stdout/stderr.

open-duck-a100-phase2-b0f-20260629T110536Z:
  64-env detached full run died after manifest, no active runner process.

open-duck-a100-phase2-b0f-20260629T111905Z:
  foreground remote mode also lost the named Colab session before normal
  artifact download.
```

## Decision

Do not treat this as a B0F policy result. B0F has not been trained to a
candidate checkpoint, and no gate result exists.

Current blocker is the cloud execution path for full B0F, not the robot and not
the recipe's tiny/64-env viability. The next attempt should avoid the detached
Colab console path, for example by running B0F through a direct `colab exec`
driver on a stable session, reducing artifact upload size, or using another
stable CUDA runtime.

Robot validation remains blocked.
