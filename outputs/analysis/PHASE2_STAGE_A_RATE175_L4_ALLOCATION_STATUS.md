# Phase 2 Stage A Rate175 L4 Allocation Status

status: `HOLD_COLAB_GPU_ALLOCATION`
generated_at: `2026-07-06T10:18:39Z`

Offline only. No robot, SSH, deploy, grounded replay, training-result promotion,
or runtime behavior change was performed.

## Attempt Summary

The detached Stage A launcher was run once with:

- session: `open-duck-l4-stagea`
- accelerator: `L4`
- execution_mode: `detached`

Colab returned `HOLD_ACCELERATOR_REJECTED`: the backend rejected accelerator
`L4`, likely due to quota or entitlement for the account/runtime. The Stage A
workflow was not started and no checkpoint/gate artifact was produced.

## Impact

The current usable path remains retrying available Colab GPUs, especially T4,
or using another explicitly allocated runtime. CPU smoke is still wiring
evidence only and is not promotable as a Phase 2 gate.

