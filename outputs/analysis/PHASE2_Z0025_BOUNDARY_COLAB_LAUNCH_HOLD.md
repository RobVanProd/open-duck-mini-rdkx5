# Phase 2 z=0.0025 Boundary Colab Launch Hold

status: `HOLD_COLAB_EXEC_UNAVAILABLE`
workflow: `phase2-z0025-boundary`
session: `open-duck-a100-phase2d`
hardware_reported: `A100`
date_utc: `2026-06-30`

## Summary

- The z=0.0025 boundary workflow is implemented, packaged, validated, and pushed.
- `colab sessions` and `colab status` report `open-duck-a100-phase2d` as an A100 session.
- `colab console` fails immediately with `Session 'open-duck-a100-phase2d' appears to be lost (404/401).`
- `colab exec` fails with the same lost-session/auth condition.
- `colab --auth adc` is not usable because Application Default Credentials are not configured.
- No training was started on Colab.

## Ready Command

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow phase2-z0025-boundary \
  --session open-duck-a100-phase2d \
  --candidate-name phase2_z0025_boundary_cuda \
  --candidate-checkpoint-sweep \
  --candidate-checkpoint-sweep-commands 0.0,0.08 \
  --candidate-checkpoint-sweep-duration 1.0 \
  --candidate-checkpoint-sweep-jax-platform cpu \
  --candidate-timeout-s 10800 \
  --run
```

## Local State

- Package-only check passed for the same workflow.
- Local ROCm sees the RX 7900 XTX, but the local Playground env currently reports JAX `0.8.2`; the trusted Colab workflow pins JAX `0.7.2`.
- Full local training was not launched to avoid mixing backend versions with the established Phase 2 evidence.

## Scope

No robot tests, SSH, deploy, grounded replay, policy overwrite, or runtime behavior changes were performed.
