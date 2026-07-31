# Phase 2 Stage A Rate175 Detached Retry Status

status: `HOLD_COLAB_GPU_ALLOCATION`
generated_at: `2026-07-06T09:51:33Z`

Offline only. No robot, SSH, deploy, grounded replay, training-result promotion,
or runtime behavior change was performed.

## Attempt Summary

The detached Stage A retry launcher was run after the earlier T4 session vanished
before exporting any checkpoint. The launcher attempted to allocate the
`open-duck-t4-stagea` Colab session six times with `--execution-mode detached`.

All six allocation attempts returned `HOLD_SERVICE_UNAVAILABLE` from `colab new`.
No Colab GPU session became available, so the Stage A workflow was not started
and no checkpoint/gate artifact was produced.

## Impact

- Phase 2 Stage A remains untrained.
- The CPU smoke remains wiring evidence only and is not promotable.
- The next valid action is to retry the detached Colab launcher when GPU
  allocation is available.
