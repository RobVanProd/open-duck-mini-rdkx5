# Phase 2 Stage A Rate175 A100 Allocation Status

status: `HOLD_COLAB_GPU_ALLOCATION`
generated_at: `2026-07-06T10:17:48Z`

Offline only. No robot, SSH, deploy, grounded replay, training-result promotion,
or runtime behavior change was performed.

## Attempt Summary

The detached Stage A launcher was run once with:

- session: `open-duck-a100-stagea`
- accelerator: `A100`
- execution_mode: `detached`

Colab returned `HOLD_ACCELERATOR_REJECTED`: the backend rejected accelerator
`A100`, likely due to quota or entitlement for the account/runtime. The Stage A
workflow was not started and no checkpoint/gate artifact was produced.

## Impact

The current usable path remains retrying available Colab GPUs, especially T4,
or using another explicitly allocated runtime. CPU smoke is still wiring
evidence only and is not promotable as a Phase 2 gate.

